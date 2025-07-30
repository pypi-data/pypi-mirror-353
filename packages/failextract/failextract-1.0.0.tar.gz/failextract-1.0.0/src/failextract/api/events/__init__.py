"""Event system for component communication."""

from .system import (
    Event,
    EventHandler,
    EventSystem,
    EventNames,
    get_event_system,
)

__all__ = [
    "Event",
    "EventHandler", 
    "EventSystem",
    "EventNames",
    "get_event_system",
]