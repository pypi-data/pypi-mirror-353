"""Component registry for dynamic discovery and registration."""

from typing import Dict, Any, List, Optional, Type, TypeVar, Generic
from threading import RLock
import weakref

T = TypeVar('T')


class ComponentRegistry(Generic[T]):
    """Thread-safe registry for components with type safety."""
    
    def __init__(self):
        self._components: Dict[str, T] = {}
        self._metadata: Dict[str, Dict[str, Any]] = {}
        self._lock = RLock()
    
    def register(self, name: str, component: T, metadata: Optional[Dict[str, Any]] = None) -> None:
        """Register a component with optional metadata."""
        with self._lock:
            self._components[name] = component
            self._metadata[name] = metadata or {}
    
    def unregister(self, name: str) -> None:
        """Unregister a component."""
        with self._lock:
            self._components.pop(name, None)
            self._metadata.pop(name, None)
    
    def get(self, name: str) -> Optional[T]:
        """Get a component by name."""
        with self._lock:
            return self._components.get(name)
    
    def list_names(self) -> List[str]:
        """List all registered component names."""
        with self._lock:
            return list(self._components.keys())
    
    def get_metadata(self, name: str) -> Optional[Dict[str, Any]]:
        """Get metadata for a component."""
        with self._lock:
            return self._metadata.get(name, {}).copy()
    
    def clear(self) -> None:
        """Clear all registered components."""
        with self._lock:
            self._components.clear()
            self._metadata.clear()


# Global registries for different component types
_formatter_registry = ComponentRegistry()
_ci_integration_registry = ComponentRegistry()
_chat_integration_registry = ComponentRegistry() 
_editor_integration_registry = ComponentRegistry()


def get_formatter_registry() -> ComponentRegistry:
    """Get the global formatter registry."""
    return _formatter_registry


def get_ci_integration_registry() -> ComponentRegistry:
    """Get the global CI integration registry."""
    return _ci_integration_registry


def get_chat_integration_registry() -> ComponentRegistry:
    """Get the global chat integration registry."""
    return _chat_integration_registry


def get_editor_integration_registry() -> ComponentRegistry:
    """Get the global editor integration registry."""
    return _editor_integration_registry