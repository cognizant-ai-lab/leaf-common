# Shared-loop request executor

`SharedLoopAsyncioExecutor` implements the `TaskExecutor` interface on an event
loop that is **already running**, rather than owning a thread and a loop of its
own the way `AsyncioExecutor` does. It creates no threads, does not change loop
settings, and never stops or closes the loop.

That makes it the variant for runtimes with no threads to give — Pyodide in the
browser above all, and transpiled JavaScript, where `threading.Thread.start()`
cannot run anything. It also works on native asyncio, which is how it is tested.

## Choosing between the two

Go through `AsyncioExecutorFactory`, so the choice lives in one place:

```python
from leaf_common.asyncio.asyncio_executor_factory import AsyncioExecutorFactory
from leaf_common.asyncio.asyncio_executor_types import AsyncioExecutorTypes

pool = AsyncioExecutorFactory.create_pool(AsyncioExecutorTypes.SHARED_LOOP)
executor = pool.get_executor()        # already started
```

The factory builds **pools only** — there is deliberately no `create_executor()`.
Executors are constructed solely by their pool, so every executor has an owner
that knows how to start it, hand it out, and tear it down.

A caller needing exactly one long-lived executor — a background service, say —
makes a pool-of-one with `reuse_mode=False`. **Cleanup differs by type**, and the
difference matters:

```python
# THREADED: return_executor() shuts the executor down with wait=True, joining
# its thread, so cleanup is complete when the call returns.
pool.return_executor(executor)
pool.shutdown()

# SHARED_LOOP: there is no thread to join and the executor runs on the caller's
# own loop, so a synchronous method cannot drain it. Await instead:
await pool.areturn_executor(executor)
pool.shutdown()
```

That costs nothing: the threaded pool's GC thread only exists when `reuse_mode`
is True.

Pass the type in explicitly, from config. The factory deliberately does not sniff
the platform or probe for a running loop: platform branching is the part that
does not survive transpilation.

`AsyncioExecutorTypes.THREADED` remains the default, and is what every caller
predating the factory gets.

## Direct use

Constructing one yourself bypasses the ownership the pool provides, so prefer
the factory above. The class remains importable for tests and for code that
already holds its own lifecycle:

```python
from leaf_common.asyncio.shared_loop_asyncio_executor import SharedLoopAsyncioExecutor

# Inside async Python code, such as pyodide.runPythonAsync():
executor = SharedLoopAsyncioExecutor()
executor.start()
try:
    task = executor.submit("request-1", async_request_function, request)
    response = await task
finally:
    await executor.ashutdown()
```

## Lifecycle differences from AsyncioExecutor

- Construct outside async code if needed; call `start()` inside the running loop.
- `initialize()` runs a synchronous, nonblocking initializer immediately and
  propagates failures. ContextVar changes are isolated from the caller and copied
  into subsequent tasks. Thread-local logging state is not request-isolated.
- `submit()` supports async callables, awaitables, and short synchronous callables.
  Synchronous work runs on the host loop. Blocking I/O must be adapted separately.
- `create_task()` returns an awaitable task. Exceptions propagate when awaited.
  `raise_exception=True` additionally reports background errors to the existing
  loop exception handler. It does not install a new handler.
- `await cancel_current_tasks(timeout=5)` cancels a snapshot of owned tasks and
  leaves the executor reusable. Later submissions are outside that snapshot.
- `await ashutdown()` rejects future submissions, cancels outstanding tasks, and
  awaits cleanup. Use `cancel_futures=False` for graceful completion, and an
  optional `timeout` to bound waiting. Timed-out tasks remain tracked.
- `shutdown(wait=False)` rejects submissions immediately; optionally pass
  `cancel_futures=True` to request cancellation. It does not await cleanup.
  `shutdown(wait=True)` raises if unfinished tasks would require blocking.
- Cleanup must be awaited outside executor-owned tasks to avoid self-deadlock.
  This is enforced by a ContextVar marker stamped into the context every
  submitted task runs in, not by comparing the running task against the tracked
  one: under a task factory returning a non-Task Future, the tracked object is
  the factory's wrapper while `asyncio.current_task()` is the inner Task that
  drives the coroutine, so an identity comparison never matches. The marker is
  a *chain* of (executor, owned task) entries rather than a single slot, so an
  executor used inside another executor's task appends rather than overwriting —
  without that, the outer executor could be drained from inside the inner's
  task while the outer's own task sat awaiting it. An entry is pushed before
  `create_task()` is called, so a host *eager* task factory, which runs the
  coroutine's first step inside `create_task()`, still sees the work as owned
  before the task object exists. The test is whether a still-pending owned task
  is an ancestor of the caller. Owned work may therefore still clean
  up a different executor, and a detached child may clean up once the owned root
  it descends from has finished — it was never drained, cancelled or reported,
  so it cannot be waited on. While that root is still pending, cleanup from a
  descendant stays refused, because draining would wait on work the descendant
  is holding up. A factory that discards the `context=` it is handed defeats the
  marker, but such a factory already breaks per-request ContextVar isolation;
  a factory that hands back a real Task is covered by the identity check
  instead.
- Only work submitted through the executor is owned. Await any child tasks you
  spawn; there is no public way to hand one over, since the self-cleanup guard
  cannot recognise work the executor did not schedule. Cleanup does not inspect
  global loop tasks.

`max_workers` is accepted by both the executor and its pool so callers need not
branch on type, but the shared-loop implementations have no worker threads and
ignore it.

## Returning an executor

`SharedLoopAsyncioExecutorPool` offers two return paths, because a synchronous
one cannot keep the native pool's promise that "returned means finished".

`await pool.areturn_executor(executor)` is the complete path. The executor keeps
whatever ownership it already had until cleanup resolves, and only then moves:

- **Drained** — the pool gives up ownership entirely.
- **Timed out** — `TimeoutError` is raised and the executor becomes *retiring*.
  It has already stopped accepting submissions, but some task outlasted the
  wait, so the pool keeps it: a misbehaving executor must not be lost precisely
  when you need to see it. Await `ashutdown()` or call this again to retry.
- **Refused** — `ashutdown()` will not run at all when called from one of the
  executor's own tasks, and in that case the executor was never shut down and
  is still perfectly usable. It stays checked out, so it keeps its owner rather
  than being retired and then pruned away once the calling task ends.

`pool.return_executor(executor)` requests cancellation and returns at once. It
does **not** guarantee cleanup has finished. A task that catches
`CancelledError` and keeps running leaves the executor *retiring*: still owned
by the pool, still counted by `get_threads_metrics()` under a `retiring` bucket,
and still listed by `dump_tasks_in_used_executors()` with `"retiring": True`.
An executor with nothing pending is released outright, so the ordinary path
accumulates nothing.

`await pool.ashutdown()` drains anything left retiring. Synchronous
`pool.shutdown()` cannot, so it raises `RuntimeError` pointing at `ashutdown()`
when retiring work remains — the same way
`SharedLoopAsyncioExecutor.shutdown(wait=True)` does one level down. Pass
`wait=False` to shut down without that check.

## Loops that do not take `context=`

CPython's `AbstractEventLoop.create_task` accepts `context=`, and this class
uses it to give each submission its own ContextVar copy. But this class borrows
whatever loop the host is running, and a hand-written loop need not implement
the full signature — **Pyodide's `WebLoop` is exactly such a loop**, and it is
this class's main reason to exist.

So the loop's `create_task` is probed once, by signature, and a loop without a
`context` parameter gets a fallback: the context is entered around the call
instead. `asyncio.Task` snapshots `copy_context()` at construction when given no
context, and that snapshot is taken inside the entered context, so per-request
isolation and the ownership marker both survive unchanged.

The probe reads the signature rather than catching `TypeError`, because a
`TypeError` from anywhere else inside `create_task()` would be indistinguishable
from a rejected keyword — and retrying would schedule the work twice.

## What this is not

This is **not** a drop-in replacement for every `AsyncioExecutor` caller. Anything
that blocks a thread waiting on loop work still needs adapting:
`AsyncToSyncGenerator` and synchronous session cleanup are the two that matter.
Run acquisition on the existing event loop, use an async session path, and await
request cleanup when completion must be guaranteed.

`SharedLoopAsyncioExecutorPool` mirrors the `AsyncioExecutorPool` surface, but
has no reuse, no idle expiry, no worker pool, and no GC thread: every acquisition
builds a fresh executor. It accepts the pool configuration arguments and honors
none of them. Its return lifecycle also differs, as described above — that one is
a behavioral difference, not just an ignored argument.

No global monkey patch of leaf-common is required or performed.
