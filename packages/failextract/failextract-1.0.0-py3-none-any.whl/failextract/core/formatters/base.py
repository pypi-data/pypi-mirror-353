"""Base formatter classes and interfaces."""

from abc import ABC, abstractmethod
from enum import Enum
from typing import List, Dict, Any


class OutputFormat(Enum):
    """Supported output formats for test failure reports.
    
    This enum defines the available output formats that can be used to
    generate test failure reports. Each format serves different use cases
    from machine-readable data to human-readable documentation.
    
    Attributes:
        JSON: JavaScript Object Notation format for machine-readable data
        MARKDOWN: Markdown format for documentation and human-readable output
        YAML: YAML format for configuration-like structured data
        XML: XML format for structured data exchange
        CSV: Comma-separated values format for spreadsheet analysis
        CUSTOM: Custom formatter implementation
    """

    JSON = "json"
    MARKDOWN = "md"
    YAML = "yaml"
    XML = "xml"
    CSV = "csv"
    CUSTOM = "custom"


class OutputFormatter(ABC):
    """Base class for output formatters.
    
    This abstract base class defines the interface that all output formatters
    must implement. It provides the foundation for creating custom formatters
    that can render test failure data in various formats.
    
    Subclasses must implement the format() and get_extension() methods to
    provide format-specific rendering and file extension handling.
    """

    @abstractmethod
    def format(self, failures: List[Dict[str, Any]]) -> str:
        """Format failure data for output.
        
        Args:
            failures: List of failure dictionaries containing test failure information
            
        Returns:
            Formatted string representation of the failure data
            
        Raises:
            NotImplementedError: If not implemented by subclass
        """
        pass

    @abstractmethod
    def get_extension(self) -> str:
        """Get default file extension for this format.
        
        Returns:
            File extension string (e.g., 'json', 'md', 'xml')
            
        Raises:
            NotImplementedError: If not implemented by subclass
        """
        pass