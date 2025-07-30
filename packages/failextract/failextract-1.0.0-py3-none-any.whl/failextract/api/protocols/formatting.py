"""Formatting protocols for type-safe interfaces."""

from typing import Protocol, Dict, Any, List, Optional, Union, runtime_checkable
from abc import abstractmethod
from enum import Enum


class OutputFormat(Enum):
    """Supported output formats."""
    JSON = "json"
    MARKDOWN = "md"
    XML = "xml" 
    CSV = "csv"
    YAML = "yaml"


@runtime_checkable
class OutputFormatterProtocol(Protocol):
    """Protocol for output formatter implementations."""
    
    @abstractmethod
    def format(self, failures: List[Dict[str, Any]], metadata: Optional[Dict[str, Any]] = None) -> str:
        """Format failure data into the target format."""
        ...
    
    @abstractmethod
    def get_file_extension(self) -> str:
        """Get the file extension for this format."""
        ...
    
    @abstractmethod
    def supports_streaming(self) -> bool:
        """Check if this formatter supports streaming output."""
        ...


@runtime_checkable
class FormatterRegistryProtocol(Protocol):
    """Protocol for formatter registry implementations."""
    
    @abstractmethod
    def register(self, format_name: str, formatter: OutputFormatterProtocol) -> None:
        """Register a formatter for a specific format."""
        ...
    
    @abstractmethod
    def get_formatter(self, format_name: str) -> Optional[OutputFormatterProtocol]:
        """Get a formatter by format name."""
        ...
    
    @abstractmethod
    def list_formats(self) -> List[str]:
        """List all available formats."""
        ...