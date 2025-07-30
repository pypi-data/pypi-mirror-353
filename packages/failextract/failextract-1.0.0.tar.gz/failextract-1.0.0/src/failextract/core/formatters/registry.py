"""Formatter registry for managing output formatters.

This module provides a centralized registry for managing all available
output formatters in FailExtract. It handles formatter discovery, format
detection from file extensions, and provides a clean interface for
accessing formatters throughout the application.
"""

from typing import Union
from pathlib import Path

from .base import OutputFormat, OutputFormatter
from .json import JSONFormatter
from .markdown import MarkdownFormatter
from .xml import XMLFormatter
from .csv import CSVFormatter
from .yaml import YAMLFormatter


class FormatterRegistry:
    """Registry for managing and accessing output formatters.
    
    This class provides a centralized registry for all available output
    formatters in FailExtract. It maintains a mapping between format types
    and formatter instances, and provides utilities for format detection
    and formatter access.
    
    The registry is designed as a class with class methods to provide
    a singleton-like interface without the complexity of actual singleton
    implementation.
    
    Attributes:
        _formatters (Dict[OutputFormat, OutputFormatter]): Mapping of format
            types to formatter instances
    
    Example:
        >>> formatter = FormatterRegistry.get_formatter('json')
        >>> output = formatter.format(failures)
        >>> 
        >>> # Detect format from filename
        >>> format_type = FormatterRegistry.detect_format('report.xml')
        >>> print(format_type)
        OutputFormat.XML
    """

    _formatters = {
        OutputFormat.JSON: JSONFormatter(),
        OutputFormat.MARKDOWN: MarkdownFormatter(),
        OutputFormat.YAML: YAMLFormatter(),
        OutputFormat.XML: XMLFormatter(),
        OutputFormat.CSV: CSVFormatter(),
    }

    @classmethod
    def get_formatter(cls, format_type: Union[OutputFormat, str]) -> OutputFormatter:
        """Get formatter for the specified format."""
        if isinstance(format_type, str):
            # Try to match string to format
            format_type = format_type.lower()
            for fmt in OutputFormat:
                if fmt.value == format_type or fmt.name.lower() == format_type:
                    return cls._formatters[fmt]
            # Check file extension
            ext_map = {
                ".json": OutputFormat.JSON,
                ".md": OutputFormat.MARKDOWN,
                ".markdown": OutputFormat.MARKDOWN,
                ".yaml": OutputFormat.YAML,
                ".yml": OutputFormat.YAML,
                ".xml": OutputFormat.XML,
                ".csv": OutputFormat.CSV,
            }
            if format_type in ext_map:
                return cls._formatters[ext_map[format_type]]
        elif isinstance(format_type, OutputFormat):
            if format_type in cls._formatters:
                return cls._formatters[format_type]

        raise ValueError(f"Unknown format type: {format_type}")

    @classmethod
    def register_formatter(cls, format_type: OutputFormat, formatter: OutputFormatter):
        """Register a custom formatter."""
        cls._formatters[format_type] = formatter

    @classmethod
    def detect_format(cls, filename: str) -> OutputFormat:
        """Detect format from filename extension."""
        ext = Path(filename).suffix.lower()
        ext_map = {
            ".json": OutputFormat.JSON,
            ".md": OutputFormat.MARKDOWN,
            ".markdown": OutputFormat.MARKDOWN,
            ".yaml": OutputFormat.YAML,
            ".yml": OutputFormat.YAML,
            ".xml": OutputFormat.XML,
            ".csv": OutputFormat.CSV,
        }
        return ext_map.get(ext, OutputFormat.JSON)