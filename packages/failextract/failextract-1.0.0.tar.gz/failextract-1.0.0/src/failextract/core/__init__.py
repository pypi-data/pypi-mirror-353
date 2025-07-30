"""Failextract Core Module.

This module contains the stable core functionality for failure extraction,
analysis, and formatting. It is designed to be independent of external
integrations and provides the foundation for all failextract operations.
"""

# Import core components that are always available
from .extraction import *
from .analysis import *
from .formatters import OutputFormat, OutputFormatter, JSONFormatter

# Build __all__ dynamically based on what's actually available
__all__ = [
    # Core formatters (always available)
    "OutputFormat",
    "OutputFormatter", 
    "JSONFormatter",
    # Extraction (always available)
    "FixtureExtractor",
    # Analysis (always available)
    "CodeContextExtractor",
]

# Try to import optional formatters and add to __all__ if available
try:
    from .formatters import MarkdownFormatter
    __all__.append("MarkdownFormatter")
except ImportError:
    pass

# HTMLFormatter removed - use external tools for HTML conversion

try:
    from .formatters import XMLFormatter
    __all__.append("XMLFormatter")
except ImportError:
    pass

try:
    from .formatters import CSVFormatter
    __all__.append("CSVFormatter")
except ImportError:
    pass

try:
    from .formatters import YAMLFormatter
    __all__.append("YAMLFormatter")
except ImportError:
    pass

try:
    from .formatters import FormatterRegistry
    __all__.append("FormatterRegistry")
except ImportError:
    pass