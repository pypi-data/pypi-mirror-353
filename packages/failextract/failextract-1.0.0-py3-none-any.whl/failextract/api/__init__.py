"""Failextract API Layer.

This module defines the public interfaces, protocols, and contracts
for the failextract system. It provides type-safe interfaces for
all major components and enables dynamic discovery of plugins.
"""

from .protocols import *
from .registry import *
from .events import *

__all__ = [
    # Re-export all protocols
    "FailureExtractorProtocol",
    "CodeContextExtractorProtocol", 
    "FixtureExtractorProtocol",
    "OutputFormatterProtocol",
    "FormatterRegistryProtocol",
    "OutputFormat",
    "CIPlatformIntegrationProtocol",
    "ChatPlatformIntegrationProtocol", 
    "EditorIntegrationProtocol",
    "CacheProtocol",
    "PersistenceProtocol",
    # Registry components
    "ComponentRegistry",
    "get_formatter_registry",
    "get_ci_integration_registry", 
    "get_chat_integration_registry",
    "get_editor_integration_registry",
    # Event system
    "Event",
    "EventHandler", 
    "EventSystem",
    "EventNames",
    "get_event_system",
]