# Copyright © 2019-2026 Cognizant Technology Solutions Corp, www.cognizant.com.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# END COPYRIGHT
"""Run tasks on an event loop that is already running, without Python threads.

The counterpart to AsyncioExecutor, which owns a thread and the loop running on
it. This one borrows the caller's running loop and creates no threads at all, so
it is the variant that works where threads do not exist -- Pyodide in the browser
above all, and transpiled JavaScript, where threading.Thread.start() cannot run
anything. It also works on native asyncio, which is how it is tested.

Call start() from async code. submit() returns an awaitable Future (an
asyncio.Task on a loop with no custom task factory; see below).
Synchronous callables run on the loop and MUST be short and nonblocking.
Use await cancel_current_tasks() and await ashutdown() for cleanup; synchronous
shutdown(wait=True) refuses to block on pending tasks. This is not a drop-in
replacement for callers using AsyncToSyncGenerator or the threaded executor pool.

Only work submitted through this executor is owned. Callers must await any child
tasks they spawn from within it; there is no public way to hand one over, because
ownership of work the executor did not schedule cannot be reconciled with the
self-cleanup guard. The host loop and its global settings are untouched.

That includes the host's task factory. loop.create_task() may validly return any
Future-compatible object when a factory is installed -- on Python 3.12 such a
result need not be an asyncio.Task, and need not provide get_name(), get_coro()
or get_stack(). Ownership here needs only the Future API (add_done_callback,
cancel, cancelled, exception, get_loop), so any Future on this loop can be
tracked; the Task-only methods are used for reporting alone and are guarded.
The alternative -- constructing asyncio.Task directly to guarantee the type --
was rejected because it would silently bypass a factory the host installed for
a reason, such as eager task execution or tracing.

One consequence: ownership cannot be decided by object identity. A factory
returning a non-Task Future must delegate the running to an inner real Task, so
the tracked object is not the task asyncio reports as current. The owned task an
execution descends from is therefore marked in the context each submitted task
runs in. See _OWNING_ROOT and _pending().
"""
import asyncio
import contextvars
import inspect
from typing import Any
from typing import Awaitable
from typing import Callable
from typing import ClassVar
from typing import Coroutine
from typing import Dict
from typing import List
from typing import Tuple

from leaf_common.asyncio.task_executor import TaskExecutor


class SharedLoopAsyncioExecutor(TaskExecutor):
    """Track one request's tasks while borrowing the host's running event loop."""

    # Identifies the owned task the current execution descends from, so that
    # "would cleaning up here wait on me?" can be answered without relying on
    # the identity of whatever loop.create_task() returned.
    #
    # It cannot rely on that identity: a task factory returning a non-Task
    # Future has to delegate the running to an inner real Task, because a bare
    # Future cannot drive a coroutine. So _tasks holds the wrapper while
    # asyncio.current_task() is the inner Task, and comparing them never
    # matches.
    #
    # The value is a CHAIN of (executor, holder) pairs, appended to rather
    # than overwritten, so an executor used inside another executor's task does
    # not erase the outer one's entry. Overwriting would let the outer be
    # drained from inside the inner's task -- while the outer's own task sits
    # awaiting that very task.
    #
    # Each holder is a one-slot list rather than the task itself, because the
    # context has to exist before create_task() can hand the task back. The
    # holder is pushed EMPTY and filled immediately after, and an empty holder
    # is itself meaningful: it says the task has not been handed back yet, so
    # execution reaching the guard is the eager first step of the very
    # coroutine being scheduled. That is still this executor's own work.
    #
    # Child tasks inherit the chain, which is the point: it says which OWNED
    # ROOT an execution descends from, so an untracked child is judged by
    # whether that root is still pending rather than merely by which executor
    # it came from.
    #
    # One ContextVar for the whole class, never per instance: a Context holds a
    # strong reference to every ContextVar set in it, and these executors are
    # per request, so a per-instance var would retain one var per request.
    _OWNING_ROOT: ClassVar[contextvars.ContextVar] = \
        contextvars.ContextVar("shared_loop_owning_root", default=())

    # max_workers is accepted so callers need not branch on executor type.
    # pylint: disable=unused-argument
    def __init__(self, max_workers: int = None):
        # Accepted for constructor compatibility; no worker threads are created.
        super().__init__()
        self._loop: asyncio.AbstractEventLoop = None
        self._context: contextvars.Context = None
        self._shutdown: bool = False
        self._tasks: Dict[asyncio.Future, bool] = {}
        # Whether this loop's create_task() accepts context=. Probed once on
        # first use. See _create_task_in_context().
        self._loop_takes_context: bool = None

    def get_event_loop(self) -> asyncio.AbstractEventLoop:
        """Return the borrowed loop, or None before start()."""
        return self._loop

    def start(self) -> None:
        """Bind to the running loop and capture this request's ContextVars."""
        if self._shutdown:
            raise RuntimeError("Cannot restart an executor after shutdown")
        loop = asyncio.get_running_loop()
        if self._loop is None:
            self._loop = loop
            self._context = contextvars.copy_context()
        elif self._loop is not loop:
            raise RuntimeError("Executor must be used on its original event loop")

    def _check_loop(self, *, allow_shutdown: bool = False) -> None:
        if self._loop is None:
            raise RuntimeError("Call start() from async code before using the executor")
        if asyncio.get_running_loop() is not self._loop:
            raise RuntimeError("Executor must be used on its original event loop")
        if self._shutdown and not allow_shutdown:
            raise RuntimeError("Cannot schedule new tasks after shutdown")

    def initialize(self, init_function: Callable) -> None:
        """Run a synchronous initializer in the request context; propagate errors.

        ContextVar changes apply to future submissions, not the calling task.
        Thread-local variables cannot provide request isolation on a shared loop.
        """
        self._check_loop()
        result = self._context.run(init_function)
        if inspect.isawaitable(result):
            if inspect.iscoroutine(result):
                result.close()
            raise TypeError("initialize() requires a synchronous initializer")

    @staticmethod
    def get_function_name(function: Any, submitter_id: str) -> str:
        """Build the same submitter-prefixed task names as leaf-common."""
        name = getattr(function, "__qualname__", type(function).__name__)
        return f"{submitter_id}:{name}" if submitter_id else name

    def submit(self, submitter_id: str, function: Any, /, *args: Any, **kwargs: Any) -> asyncio.Future:
        """Schedule a callable or awaitable; return its task, including its result.

        Sync callables run inline when the task runs, never in a worker thread.
        Callable results that are awaitable are awaited as well.
        """
        self._check_loop()
        if inspect.isawaitable(function):
            if args or kwargs:
                raise TypeError("Arguments cannot be supplied with an awaitable")
            return self.create_task(function, submitter_id)
        if not callable(function):
            raise TypeError("submit() requires a callable or awaitable")

        return self._schedule(self._invoke(function, *args, **kwargs),
                              self.get_function_name(function, submitter_id), False)

    @staticmethod
    async def _invoke(function: Callable, *args: Any, **kwargs: Any) -> Any:
        """Call a callable on the loop, awaiting its result when it is awaitable.

        :param function: The callable to invoke
        :param args: args for the callable
        :param kwargs: keyword args for the callable
        :return: The callable's result, awaited if it was awaitable
        """
        result: Any = function(*args, **kwargs)
        return await result if inspect.isawaitable(result) else result

    def create_task(self, awaitable: Awaitable, submitter_id: str,
                    raise_exception: bool = False) -> asyncio.Future:
        """Schedule an awaitable; optionally report failures to the loop handler.

        Awaiting the returned task always propagates its exception, regardless of
        raise_exception. The flag controls reporting of background failures only.
        """
        self._check_loop()
        if not inspect.isawaitable(awaitable):
            raise TypeError("create_task() requires an awaitable")
        # asyncio.isfuture(), not isinstance(), so that the loop check and the
        # cancellation hand-off below cover the same structural Future objects
        # _track_task() accepts. A subclass check would let a wrapper from
        # another loop through to be scheduled, failing only once _consume()
        # awaited it -- with its underlying work already running outside this
        # executor's cleanup.
        if asyncio.isfuture(awaitable):
            if awaitable.get_loop() is not self._loop:
                raise ValueError("Awaitable belongs to another event loop")
            if isinstance(awaitable, asyncio.Task):
                raise TypeError("create_task() cannot adopt an existing asyncio.Task")
        # Use coroutine objects directly so cancellation before the first step
        # cannot leave a nested coroutine unawaited.
        coroutine: Coroutine = None
        if inspect.iscoroutine(awaitable):
            coroutine = awaitable
        else:
            coroutine = self._consume(awaitable)
        task = self._schedule(coroutine, self.get_function_name(awaitable, submitter_id), raise_exception)
        if asyncio.isfuture(awaitable):
            # Cancelling our wrapper must reach the awaitable it wraps, or the
            # work behind it keeps running once we stop tracking. This matters
            # most when the wrapper is cancelled before its first step, since
            # _consume() never gets to await the awaitable at all.

            def callback(completed):
                if completed.cancelled() and not awaitable.done():
                    return awaitable.cancel()
                return None

            task.add_done_callback(callback)
        return task

    def _create_task_in_context(self, coroutine: Coroutine, name: str,
                                context: contextvars.Context) -> asyncio.Future:
        """Schedule a coroutine so it runs in the given context.

        CPython's AbstractEventLoop.create_task takes context=, but this class
        borrows whatever loop the host is running, and a hand-written loop need
        not implement the full signature. Pyodide's WebLoop is exactly such a
        loop, and it is this class's main reason to exist, so a loop that
        rejects context= must not break every submission.

        The loop is probed once rather than discovered by catching TypeError,
        because a TypeError from anywhere else in create_task() would leave us
        unable to tell a rejected keyword from work that was already scheduled,
        and retrying would schedule it twice.

        :param coroutine: The coroutine to schedule
        :param name: The task name to request
        :param context: The context the task should run in
        :return: Whatever the loop's create_task() produced
        """
        if self._loop_takes_context is None:
            self._loop_takes_context = self._takes_context(self._loop.create_task)
        if self._loop_takes_context:
            return self._loop.create_task(coroutine, name=name, context=context)

        # The loop cannot be told which context to use, so enter it ourselves.
        # asyncio.Task snapshots copy_context() at construction when given no
        # context, and that snapshot is taken inside this run(), so the task
        # still gets this context -- ContextVar isolation and the ownership
        # marker included.
        return context.run(self._loop.create_task, coroutine, name=name)

    @staticmethod
    def _takes_context(create_task: Callable) -> bool:
        """Report whether a loop's create_task() accepts a context keyword.

        :param create_task: The bound create_task of the loop in use
        :return: True if context= can be passed. A loop whose signature cannot
                 be read is assumed to follow the standard contract, since
                 that is what CPython's own loops do.
        """
        try:
            parameters = inspect.signature(create_task).parameters
        except (TypeError, ValueError):
            return True
        if "context" in parameters:
            return True
        return any(parameter.kind is inspect.Parameter.VAR_KEYWORD
                   for parameter in parameters.values())

    @staticmethod
    async def _consume(awaitable: Awaitable) -> Any:
        """Wrap a non-coroutine awaitable so it can be handed to create_task().
        :param awaitable: The awaitable to await
        :return: Whatever the awaitable produces
        """
        return await awaitable

    def _schedule(self, coroutine: Coroutine, name: str, raise_exception: bool) -> asyncio.Future:
        """Create a task on the host loop and take ownership of it.

        :param coroutine: The coroutine to schedule
        :param name: The task name to request
        :param raise_exception: True to report background failures to the loop
        :return: The Future the host loop's task factory produced
        """
        # The holder is pushed onto the chain before the task exists, so that
        # a host eager task factory -- which runs the coroutine's first step
        # inside create_task() below -- already sees this executor as the owner
        # of what is running. It receives the task itself immediately after.
        # See _OWNING_ROOT.
        root_holder: List[asyncio.Future] = []
        context: contextvars.Context = self._context.copy()
        context.run(self._push_owning_root, root_holder)
        try:
            task = self._create_task_in_context(coroutine, name, context)
        except BaseException:
            coroutine.close()
            raise
        root_holder.append(task)

        # By this point the factory has already scheduled the work. If we
        # cannot own the object it handed back, cancel it rather than let it
        # run untracked and outside shutdown.
        try:
            return self._track_task(task, raise_exception)
        except BaseException:
            cancel = getattr(task, "cancel", None)
            if callable(cancel):
                cancel()
            raise

    def _track_task(self, task: asyncio.Future, raise_exception: bool = False) -> asyncio.Future:
        """Take ownership of a task on this loop (without changing its context).

        Internal: not part of the TaskExecutor interface, and deliberately not
        public. Ownership is only ever taken of work this executor scheduled
        itself, because the self-cleanup guard has to be able to recognise the
        work that is running. Anything adopted from outside would defeat that:
        it carries no ownership marker, and for a non-Task Future
        asyncio.current_task() reports its inner runner rather than the
        wrapper in _tasks, so cleanup called from that work would wait on the
        caller itself instead of being refused.

        Accepts any Future-compatible object because a host task factory may
        hand one back from _schedule(); those carry the marker. See the module
        comment.

        :param task: A Future on this executor's event loop
        :param raise_exception: True to report background failures to the loop
        :return: The same Future, now owned by this executor
        """
        self._check_loop()
        if not asyncio.isfuture(task) or task.get_loop() is not self._loop:
            raise ValueError("Expected a Future-compatible object on the executor's event loop")
        if task not in self._tasks:
            task.add_done_callback(self.submission_done)
        self._tasks[task] = raise_exception
        return task

    def submission_done(self, task: asyncio.Future) -> None:
        """Release references and retrieve errors, including unawaited failures."""
        report = self._tasks.pop(task, False)
        if task.cancelled():
            return
        exception = task.exception()
        if report and exception is not None:
            self._loop.call_exception_handler({
                "message": f"Executor task failed: {self.get_task_name(task)}",
                "exception": exception,
                "task": task,
            })

    @staticmethod
    def get_task_name(task: asyncio.Future) -> str:
        """Name a tracked task for reporting, whatever the factory produced.

        get_name() is an asyncio.Task method. A Future-compatible factory
        result need not have it, so fall back to repr().

        :param task: The tracked Future to name
        :return: The task's name, or its repr when it has none
        """
        get_name = getattr(task, "get_name", None)
        if callable(get_name):
            return get_name()
        return repr(task)

    def get_tracked_tasks(self) -> List[asyncio.Future]:
        """Report the tasks this executor owns, finished ones included.

        Ownership bookkeeping is this executor's business, so callers that need
        to see it -- a pool rendering a task dump, say -- ask here rather than
        reading the internal table.

        :return: A snapshot list of every Future still tracked by this executor
        """
        return list(self._tasks)

    def has_pending_tasks(self) -> bool:
        """Report whether any owned task is still running.

        Unlike _pending(), this never raises when called from inside an owned
        task, because it is a question a caller may ask from anywhere.

        :return: True if at least one owned task has not finished
        """
        return any(not task.done() for task in self._tasks)

    def _pending(self) -> List[asyncio.Future]:
        """Report unfinished owned tasks, refusing to run inside one of them.

        Cleanup that would wait on the execution performing it is rejected.
        That is the whole test, so the question is whether a STILL PENDING
        owned task is an ancestor of the caller -- not merely whether the
        caller came from this executor. A detached child whose owned root has
        already finished is never in the drained set and cannot be waited on,
        so cleanup from it is allowed.

        Two independent checks, because neither covers every case:

          - The owning root catches work submitted through this executor
            whatever the host's task factory returned, including a non-Task
            Future wrapper whose inner Task is what current_task() reports, and
            including that work's child tasks. Because `tasks` holds only this
            executor's pending work, a root belonging to another executor, or
            one that has already finished, simply is not in it. What it cannot
            catch is work under a factory that discards the context= it is
            handed -- such a factory already breaks per-request ContextVar
            isolation, but it should not also cost us the guard.
          - The identity check catches exactly that: any tracked object that
            *is* the running task, which is the case whenever such a factory
            hands back a real Task.

        :return: The owned tasks that have not finished
        """
        tasks: List[asyncio.Future] = [task for task in self._tasks if not task.done()]
        if self._owns_current_execution(tasks) or asyncio.current_task() in tasks:
            raise RuntimeError("Await executor cleanup outside its owned tasks")
        return tasks

    def _push_owning_root(self, holder: List[asyncio.Future]) -> None:
        """Append this executor's ownership entry to the chain.

        Must be run inside the context being prepared, so that the read and the
        write both see that context rather than the submitter's.

        :param holder: The one-slot list that will receive the task
        """
        self._OWNING_ROOT.set(self._OWNING_ROOT.get() + ((self, holder),))

    def _owns_current_execution(self, tasks: List[asyncio.Future]) -> bool:
        """Report whether the caller is running inside this executor's own work.

        :param tasks: This executor's unfinished owned tasks
        :return: True if draining those tasks would wait on the caller
        """
        for executor, holder in self._OWNING_ROOT.get():
            if executor is not self:
                continue
            # An empty holder means create_task() has not returned yet, so this
            # is the eager first step of the coroutine being scheduled. It is
            # ours, even though it is not in `tasks` yet.
            return not holder or holder[0] in tasks
        return False

    @staticmethod
    async def _drain(tasks: List[asyncio.Future], timeout: float) -> None:
        if tasks:
            _, pending = await asyncio.wait(tasks, timeout=timeout)
            if pending:
                raise TimeoutError(f"{len(pending)} executor task(s) did not finish")

    async def cancel_current_tasks(self, timeout: float = 5.0) -> None:
        """Cancel and await a snapshot of owned tasks; keep the executor reusable.

        Tasks that ignore cancellation remain tracked if the timeout expires.
        New tasks submitted during cancellation are outside this snapshot.
        """
        self._check_loop(allow_shutdown=True)
        tasks = self._pending()
        for task in tasks:
            task.cancel()
        await self._drain(tasks, timeout)

    async def ashutdown(self, *, cancel_futures: bool = True, timeout: float = None) -> None:
        """Reject submissions and await owned tasks without stopping the host loop.

        By default cancel outstanding work. With cancel_futures=False, let it
        finish. A timeout does not drop ownership of unfinished tasks.
        """
        self._check_loop(allow_shutdown=True)
        tasks = self._pending()
        self._shutdown = True
        if cancel_futures:
            for task in tasks:
                task.cancel()
        await self._drain(tasks, timeout)

    def shutdown(self, wait: bool = True, *, cancel_futures: bool = False) -> None:
        """Nonblocking shutdown; use ashutdown() when pending work must be awaited."""
        self._check_loop(allow_shutdown=True)
        tasks = self._pending()
        if wait and tasks:
            raise RuntimeError("Cannot block the shared loop; use await executor.ashutdown()")
        self._shutdown = True
        if cancel_futures:
            for task in tasks:
                task.cancel()

    def get_threads_metrics(self) -> Tuple[int, int]:
        """This executor creates no threads."""
        return 0, 0
