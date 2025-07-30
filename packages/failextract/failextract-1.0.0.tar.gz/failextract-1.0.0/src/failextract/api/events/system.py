"""Event system for loose coupling between components."""

from typing import Dict, Any, List, Callable, Optional
from threading import RLock
from dataclasses import dataclass
from datetime import datetime
import weakref


@dataclass
class Event:
    """Represents an event in the system."""
    name: str
    data: Dict[str, Any]
    timestamp: datetime
    source: Optional[str] = None


EventHandler = Callable[[Event], None]


class EventSystem:
    """Thread-safe event system for component communication."""
    
    def __init__(self):
        self._handlers: Dict[str, List[EventHandler]] = {}
        self._lock = RLock()
    
    def subscribe(self, event_name: str, handler: EventHandler) -> None:
        """Subscribe to an event."""
        with self._lock:
            if event_name not in self._handlers:
                self._handlers[event_name] = []
            self._handlers[event_name].append(handler)
    
    def unsubscribe(self, event_name: str, handler: EventHandler) -> None:
        """Unsubscribe from an event."""
        with self._lock:
            if event_name in self._handlers:
                try:
                    self._handlers[event_name].remove(handler)
                except ValueError:
                    pass  # Handler not found
    
    def publish(self, event_name: str, data: Dict[str, Any], source: Optional[str] = None) -> None:
        """Publish an event to all subscribers."""
        event = Event(
            name=event_name,
            data=data,
            timestamp=datetime.now(),
            source=source
        )
        
        with self._lock:
            handlers = self._handlers.get(event_name, []).copy()
        
        # Call handlers outside of lock to avoid deadlocks
        for handler in handlers:
            try:
                handler(event)
            except Exception:
                # Silently ignore handler exceptions to prevent one bad handler
                # from affecting others
                pass
    
    def clear(self) -> None:
        """Clear all event subscriptions."""
        with self._lock:
            self._handlers.clear()


# Global event system instance
_event_system = EventSystem()


def get_event_system() -> EventSystem:
    """Get the global event system instance."""
    return _event_system


# Standard event names
class EventNames:
    """Standard event names used throughout the system."""
    FAILURE_EXTRACTED = "failure_extracted"
    REPORT_GENERATED = "report_generated"
    CACHE_CLEARED = "cache_cleared"
    CONFIG_CHANGED = "config_changed"
    INTEGRATION_ENABLED = "integration_enabled"
    INTEGRATION_DISABLED = "integration_disabled"