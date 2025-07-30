"""Component registry for dynamic discovery."""

from .components import (
    ComponentRegistry,
    get_formatter_registry,
    get_ci_integration_registry,
    get_chat_integration_registry,
    get_editor_integration_registry,
)

__all__ = [
    "ComponentRegistry",
    "get_formatter_registry",
    "get_ci_integration_registry", 
    "get_chat_integration_registry",
    "get_editor_integration_registry",
]