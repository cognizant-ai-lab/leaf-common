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
makes a pool-of-one with `reuse_mode=False`:

```python
pool = AsyncioExecutorFactory.create_pool(reuse_mode=False, max_workers=max_workers)
executor = pool.get_executor()
...
pool.return_executor(executor)        # shuts it down when reuse_mode=False
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
- Only submitted or explicitly tracked tasks are owned. Await child tasks or
  register them with `track_task()`; cleanup does not inspect global loop tasks.

`max_workers` is accepted by both the executor and its pool so callers need not
branch on type, but the shared-loop implementations have no worker threads and
ignore it.

## What this is not

This is **not** a drop-in replacement for every `AsyncioExecutor` caller. Anything
that blocks a thread waiting on loop work still needs adapting:
`AsyncToSyncGenerator` and synchronous session cleanup are the two that matter.
Run acquisition on the existing event loop, use an async session path, and await
request cleanup when completion must be guaranteed.

`SharedLoopAsyncioExecutorPool` mirrors the `AsyncioExecutorPool` surface, but
has no reuse, no idle expiry, no worker pool, and no GC thread: every acquisition
builds a fresh executor. It accepts the pool configuration arguments and honors
none of them.

No global monkey patch of leaf-common is required or performed.
