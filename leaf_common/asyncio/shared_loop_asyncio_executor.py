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
from asyncio import AbstractEventLoop
from asyncio import Future
from asyncio import Task
from asyncio import current_task
from asyncio import get_running_loop
from asyncio import isfuture
from asyncio import wait as wait_on_tasks
from contextvars import Context
from contextvars import ContextVar
from contextvars import copy_context
from inspect import Parameter
from inspect import Signature
from inspect import isawaitable
from inspect import iscoroutine
from inspect import signature
from types import MappingProxyType
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
    """
    Tracks one request's tasks while borrowing the host's running event loop.

    The counterpart to AsyncioExecutor, which owns a thread and the loop on it.
    This variant creates no threads, so it works where threads are unavailable:
    Pyodide in the browser, and transpiled JavaScript. It also runs on native
    asyncio, which is how it is tested.

    Call start() from async code. submit() returns an awaitable Future.
    Synchronous callables run on the loop and must not block. Clean up with
    await cancel_current_tasks() and await ashutdown(); the synchronous
    shutdown(wait=True) refuses to block on pending tasks. This is not a
    drop-in replacement for callers of AsyncToSyncGenerator or the threaded
    executor pool.

    Only work submitted through this executor is owned; callers must await any
    child tasks they spawn from within it. The host loop and its settings,
    including its task factory, are left untouched.

    A host task factory may return any Future-compatible object. Such a result
    need not be an asyncio.Task and need not provide get_name(), get_coro() or
    get_stack(), so ownership requires only the Future API and the Task-only
    methods are guarded and used for reporting alone. Constructing asyncio.Task
    directly would guarantee the type but bypass a factory the host installed
    deliberately, so it is not done.

    Ownership therefore cannot be decided by object identity: a factory
    returning a non-Task Future delegates execution to an inner Task, so the
    tracked object is not the task asyncio reports as current. The owned root
    task is marked in the context each submitted task runs in instead. See
    _OWNING_ROOT and _pending().
    """

    # Identifies the owned root task the current execution descends from.
    #
    # Object identity cannot answer this: a factory returning a non-Task Future
    # delegates to an inner Task, so _tasks holds the wrapper while
    # asyncio.current_task() is the inner Task.
    #
    # The value is a chain of (executor, holder) pairs, appended to rather than
    # overwritten, so an executor used inside another executor's task does not
    # erase the outer entry. Overwriting would allow the outer executor to be
    # drained from inside the inner's task.
    #
    # Each holder is a one-slot list because the context must exist before
    # create_task() returns the task. An empty holder is meaningful: it means
    # execution reaching the guard is the eager first step of the coroutine
    # being scheduled, which is still this executor's work.
    #
    # Child tasks inherit the chain, so an untracked child is judged by whether
    # its owned root is still pending.
    #
    # One ContextVar for the class, never per instance: a Context strongly
    # references every ContextVar set in it, and these executors are per
    # request.
    _OWNING_ROOT: ClassVar[ContextVar] = ContextVar("shared_loop_owning_root", default=())

    # max_workers is accepted so callers need not branch on executor type.
    # pylint: disable=unused-argument
    def __init__(self, max_workers: int = None):
        # Accepted for constructor compatibility; no worker threads are created.
        super().__init__()
        self._loop: AbstractEventLoop = None
        self._context: Context = None
        self._shutdown: bool = False
        self._tasks: Dict[Future, bool] = {}
        # Whether this loop's create_task() accepts context=. Probed once on
        # first use. See _create_task_in_context().
        self._loop_takes_context: bool = None

    def get_event_loop(self) -> AbstractEventLoop:
        """Return the borrowed loop, or None before start()."""
        return self._loop

    def start(self) -> None:
        """Bind to the running loop and capture this request's ContextVars."""
        if self._shutdown:
            raise RuntimeError("Cannot restart an executor after shutdown")
        loop = get_running_loop()
        if self._loop is None:
            self._loop = loop
            self._context = copy_context()
        elif self._loop is not loop:
            raise RuntimeError("Executor must be used on its original event loop")

    def _check_loop(self, *, allow_shutdown: bool = False) -> None:
        if self._loop is None:
            raise RuntimeError("Call start() from async code before using the executor")
        if get_running_loop() is not self._loop:
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
        if isawaitable(result):
            if iscoroutine(result):
                result.close()
            raise TypeError("initialize() requires a synchronous initializer")

    @staticmethod
    def get_function_name(function: Any, submitter_id: str) -> str:
        """Build the same submitter-prefixed task names as leaf-common."""
        name: str = None
        try:
            name = function.__qualname__
        except AttributeError:
            # Callables such as functools.partial carry no __qualname__.
            name = type(function).__name__
        return f"{submitter_id}:{name}" if submitter_id else name

    def submit(self, submitter_id: str, function: Any, /, *args: Any, **kwargs: Any) -> Future:
        """Schedule a callable or awaitable; return its task, including its result.

        Sync callables run inline when the task runs, never in a worker thread.
        Callable results that are awaitable are awaited as well.
        """
        self._check_loop()
        if isawaitable(function):
            if args or kwargs:
                raise TypeError("Arguments cannot be supplied with an awaitable")
            return self.create_task(function, submitter_id)
        if not callable(function):
            raise TypeError("submit() requires a callable or awaitable")

        return self._schedule(self._invoke(function, *args, **kwargs),
                              self.get_function_name(function, submitter_id), False)

    async def _invoke(self, function: Callable, *args: Any, **kwargs: Any) -> Any:
        """Call a callable on the loop, awaiting its result when it is awaitable.

        :param function: The callable to invoke
        :param args: args for the callable
        :param kwargs: keyword args for the callable
        :return: The callable's result, awaited if it was awaitable
        """
        result: Any = function(*args, **kwargs)
        if isfuture(result):
            result_future: Future = result
            if result_future.get_loop() is not self._loop:
                raise ValueError("Awaitable belongs to another event loop")
            if isinstance(result_future, Task):
                raise TypeError("submit() cannot adopt an existing asyncio.Task")
            if not result_future.done():
                raise TypeError("submit() cannot adopt a pending Future; submit the work that completes it instead")

        retval: Any = result
        if isawaitable(result):
            result_awaitable: Awaitable = result
            retval = await result_awaitable
        return retval

    def create_task(self, awaitable: Awaitable, submitter_id: str,
                    raise_exception: bool = False) -> Future:
        """Schedule an awaitable; optionally report failures to the loop handler.

        Accepts a coroutine, or any awaitable that runs inside the task this
        schedules. Work already being driven elsewhere is rejected: an existing
        Task, or a Future still pending. Everything this executor can be asked
        to drain must be an execution it scheduled, and so must carry the
        ownership marker. Otherwise cleanup called from that execution would go
        unrecognised and wait on itself.

        Awaiting the returned task always propagates its exception, regardless of
        raise_exception. The flag controls reporting of background failures only.
        """
        self._check_loop()
        if not isawaitable(awaitable):
            raise TypeError("create_task() requires an awaitable")

        # asyncio.isfuture(), not isinstance(), so these checks cover the same
        # structural Future objects the rest of the class accepts. A subclass
        # check would let one through to be scheduled, failing only once
        # _consume() awaited it.
        if isfuture(awaitable):
            if awaitable.get_loop() is not self._loop:
                raise ValueError("Awaitable belongs to another event loop")
            if isinstance(awaitable, Task):
                raise TypeError("create_task() cannot adopt an existing asyncio.Task")
            if not awaitable.done():
                # A pending Future is a handle on work driven elsewhere; a
                # bare Future cannot run a coroutine itself. Wrapping it would
                # make this executor wait on an execution it never scheduled
                # and cannot mark, so an ashutdown() from that execution would
                # deadlock against its own wrapper.
                raise TypeError("create_task() cannot adopt a pending Future; "
                                "submit the work that completes it instead")

        # Use coroutine objects directly so cancellation before the first step
        # cannot leave a nested coroutine unawaited.
        coroutine: Coroutine = None
        if iscoroutine(awaitable):
            coroutine = awaitable
        else:
            coroutine = self._consume(awaitable)
        return self._schedule(coroutine, self.get_function_name(awaitable, submitter_id), raise_exception)

    def _create_task_in_context(self, coroutine: Coroutine, name: str,
                                context: Context) -> Future:
        """Schedule a coroutine so it runs in the given context.

        CPython's AbstractEventLoop.create_task takes context=, but this class
        borrows the host's loop, and a hand-written loop need not implement the
        full signature. Pyodide's WebLoop is one such loop, so rejecting
        context= must not break every submission.

        The loop is probed once rather than by catching TypeError: a TypeError
        raised elsewhere in create_task() would be indistinguishable from a
        rejected keyword, and retrying would schedule the work twice.

        :param coroutine: The coroutine to schedule
        :param name: The task name to request
        :param context: The context the task should run in
        :return: Whatever the loop's create_task() produced
        """
        if self._loop_takes_context is None:
            self._loop_takes_context = self._takes_context(self._loop.create_task)
            task_factory = self._loop.get_task_factory()
            if task_factory is not None:
                self._loop_takes_context = (
                    self._loop_takes_context and self._takes_context(task_factory))
        if self._loop_takes_context:
            return self._loop.create_task(coroutine, name=name, context=context)

        # The loop cannot be told which context to use, so enter it here.
        # asyncio.Task snapshots copy_context() at construction when given no
        # context, and that snapshot is taken inside this run(), so the task
        # still receives this context, ownership marker included.
        return context.run(self._loop.create_task, coroutine, name=name)

    @staticmethod
    def _takes_context(create_task: Callable) -> bool:
        """Report whether a loop's create_task() accepts a context keyword.

        :param create_task: The bound create_task of the loop in use
        :return: True if context= can be passed. A loop whose signature cannot
                 be read is assumed to follow the standard contract, as
                 CPython's own loops do.
        """
        parameters: MappingProxyType = None
        try:
            task_signature: Signature = signature(create_task)
            parameters = task_signature.parameters
        except (TypeError, ValueError):
            return True

        if "context" in parameters:
            return True

        parameter: Parameter = None
        for parameter in parameters.values():
            if parameter.kind is Parameter.VAR_KEYWORD:
                return True
        return False

    @staticmethod
    async def _consume(awaitable: Awaitable) -> Any:
        """Wrap a non-coroutine awaitable so it can be handed to create_task().
        :param awaitable: The awaitable to await
        :return: Whatever the awaitable produces
        """
        return await awaitable

    def _schedule(self, coroutine: Coroutine, name: str, raise_exception: bool) -> Future:
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
        root_holder: List[Future] = []
        context: Context = self._context.copy()
        context.run(self._push_owning_root, self._OWNING_ROOT.get(), root_holder)
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
            # Only the lookup is guarded. Calling inside the try would also
            # swallow an AttributeError raised by cancel() itself.
            cancel: Any = None
            try:
                cancel = task.cancel
            except AttributeError:
                cancel = None
            if callable(cancel):
                cancel()
            raise

    def _track_task(self, task: Future, raise_exception: bool = False) -> Future:
        """Take ownership of a task on this loop (without changing its context).

        Internal: not part of the TaskExecutor interface, and deliberately not
        public. Ownership is only ever taken of work this executor scheduled
        itself, because the self-cleanup guard has to be able to recognise the
        work that is running. Anything adopted from outside would defeat that:
        it carries no ownership marker, and for a non-Task Future
        asyncio.current_task() reports its inner runner rather than the
        wrapper in _tasks, so cleanup called from that work would wait on the
        caller itself instead of being refused.

        Accepts any Future-compatible object, because a host task factory may
        return one from _schedule(); those carry the marker. See the class
        comment.

        :param task: A Future on this executor's event loop
        :param raise_exception: True to report background failures to the loop
        :return: The same Future, now owned by this executor
        """
        self._check_loop()
        if not isfuture(task) or task.get_loop() is not self._loop:
            raise ValueError("Expected a Future-compatible object on the executor's event loop")
        if task not in self._tasks:
            task.add_done_callback(self.submission_done)
        self._tasks[task] = raise_exception
        return task

    def submission_done(self, task: Future) -> None:
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
    def get_task_name(task: Future) -> str:
        """Name a tracked task for reporting, whatever the factory produced.

        get_name() is an asyncio.Task method. A Future-compatible factory
        result need not have it, so fall back to repr().

        :param task: The tracked Future to name
        :return: The task's name, or its repr when it has none
        """
        get_name: Any = None
        try:
            get_name = task.get_name
        except AttributeError:
            get_name = None
        if callable(get_name):
            return get_name()
        return repr(task)

    def get_tracked_tasks(self) -> List[Future]:
        """Report the tasks this executor owns, finished ones included.

        Ownership bookkeeping is internal, so callers needing to see it, such
        as a pool rendering a task dump, ask here rather than reading the
        table directly.

        :return: A snapshot list of every Future still tracked by this executor
        """
        return list(self._tasks)

    def is_shutdown(self) -> bool:
        """Report whether this executor has stopped accepting new work.

        ashutdown() and shutdown() set this before they do anything that can
        fail or be interrupted, so an owner that sees it set knows the executor
        is unusable regardless of how its cleanup call ended.

        :return: True once shutdown has begun
        """
        return self._shutdown

    def has_pending_tasks(self) -> bool:
        """Report whether any owned task is still running.

        Unlike _pending(), this never raises when called from inside an owned
        task, because it is a question a caller may ask from anywhere.

        :return: True if at least one owned task has not finished
        """
        return any(not task.done() for task in self._tasks)

    def _pending(self) -> List[Future]:
        """Report unfinished owned tasks, refusing to run inside one of them.

        Cleanup that would wait on the execution performing it is rejected.
        The test is whether a still-pending owned task is an ancestor of the
        caller, not merely whether the caller came from this executor. A
        detached child whose owned root has finished is not in the drained set
        and cannot be waited on, so cleanup from it is allowed.

        Two checks are needed, because neither covers every case:

          - The owning root catches work submitted through this executor
            whatever the task factory returned, including a non-Task wrapper
            and that work's children. Since `tasks` holds only this executor's
            pending work, a root from another executor, or one already
            finished, is absent from it. It cannot catch work under a factory
            that discards the context= it is given.
          - The identity check covers that case: a tracked object that is
            itself the running task, which such a factory returns.

        :return: The owned tasks that have not finished
        """
        tasks: List[Future] = [task for task in self._tasks if not task.done()]
        if self._owns_current_execution(tasks) or current_task() in tasks:
            raise RuntimeError("Await executor cleanup outside its owned tasks")
        return tasks

    def _push_owning_root(self, inherited: Tuple, holder: List[Future]) -> None:
        """Append this executor's ownership entry to the submitter's chain.

        Must run inside the context being prepared, so the write lands there.
        The chain is passed in rather than read here because each task runs in
        a copy of the context captured at start(), not the submitter's. Without
        carrying it across, a task submitted from inside another task would
        start a fresh chain and lose its ancestry.

        :param inherited: The chain in effect where the submission was made
        :param holder: The one-slot list that will receive the task
        """
        self._OWNING_ROOT.set(inherited + ((self, holder),))

    def _owns_current_execution(self, tasks: List[Future]) -> bool:
        """Report whether the caller is running inside this executor's own work.

        Every entry for this executor is considered, not just the innermost.
        A nested submission appends its own entry, so a descendant may descend
        from several of this executor's tasks at once; draining waits on all of
        them, so any one still pending is enough to refuse. Stopping at the
        first entry missed the case where the nearest root had finished while
        an outer one was still pending and awaiting the caller.

        :param tasks: This executor's unfinished owned tasks
        :return: True if draining those tasks would wait on the caller
        """
        for executor, holder in self._OWNING_ROOT.get():
            # An empty holder means create_task() has not returned yet, so this
            # is the eager first step of the coroutine being scheduled. It is
            # ours, even though it is not in `tasks` yet.
            if executor is self and (not holder or holder[0] in tasks):
                return True
        return False

    @staticmethod
    async def _drain(tasks: List[Future], timeout: float) -> None:
        if tasks:
            _, pending = await wait_on_tasks(tasks, timeout=timeout)
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
