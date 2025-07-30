"""Protocol definitions for type-safe interfaces."""

from .extraction import (
    FailureExtractorProtocol,
    CodeContextExtractorProtocol,
    FixtureExtractorProtocol,
)
from .formatting import (
    OutputFormatterProtocol,
    FormatterRegistryProtocol,
    OutputFormat,
)
from .integration import (
    CIPlatformIntegrationProtocol,
    ChatPlatformIntegrationProtocol,
    EditorIntegrationProtocol,
)
from .storage import (
    CacheProtocol,
    PersistenceProtocol,
)

__all__ = [
    # Extraction protocols
    "FailureExtractorProtocol",
    "CodeContextExtractorProtocol", 
    "FixtureExtractorProtocol",
    # Formatting protocols
    "OutputFormatterProtocol",
    "FormatterRegistryProtocol",
    "OutputFormat",
    # Integration protocols
    "CIPlatformIntegrationProtocol",
    "ChatPlatformIntegrationProtocol", 
    "EditorIntegrationProtocol",
    # Storage protocols
    "CacheProtocol",
    "PersistenceProtocol",
]