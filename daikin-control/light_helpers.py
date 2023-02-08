from collections.abc import Callable
from typing import Any, TypeVar

_CallableT = TypeVar("_CallableT", bound=Callable[..., Any])

def callback(func: _CallableT) -> _CallableT:
    """Annotation to mark method as safe to call from within the event loop."""
    setattr(func, "_hass_callback", True)
    return func