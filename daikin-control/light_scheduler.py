from __future__ import annotations

from collections.abc import Callable, Coroutine
from typing import Any, TypeVar
import asyncio
from contextvars import ContextVar
from light_helpers import callback

_T = TypeVar("_T")
_R = TypeVar("_R")


class PathHelper:
    """simulate Config for HomeScheduler"""
    def __init__(self)-> None:
        ...

    def path(self, filename: str):
        return f"./{filename}"


class HomeScheduler:
    """Root object of the Home Assistant home automation."""
    config_entries: ConfigEntries = None  # type: ignore[assignment]

    def __new__(cls):
        """Set the _cv_hass context variable."""
        hass = super().__new__(cls)
        _cv_hass.set(hass)
        return hass

    def __init__(self) -> None:
        """Initialize new Home Assistant object."""
        self.loop = asyncio.get_running_loop()
        self._pending_tasks: list[asyncio.Future[Any]] = []
        # This is a dictionary that any component can store any data on.
        self.data: dict[str, Any] = {}
        self._track_task = True
        self.config = PathHelper()

    @callback
    def async_add_executor_job(self, target: Callable[..., _T], *args: Any) -> asyncio.Future[_T]:
        """Add an executor job from within the event loop."""
        task = self.loop.run_in_executor(None, target, *args)

        # If a task is scheduled
        if self._track_task:
            self._pending_tasks.append(task)
        return task

    @callback
    def async_create_task(self, target: Coroutine[Any, Any, _R]) -> asyncio.Task[_R]:
        """Create a task from within the eventloop.
        This method must be run in the event loop.
        target: target to call.  """
        task = self.loop.create_task(target)
        if self._track_task:
            self._pending_tasks.append(task)
        return task


_cv_hass: ContextVar[HomeScheduler] = ContextVar("current_entry")

