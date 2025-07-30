"""Output formatters for different report formats."""

from .base import OutputFormat, OutputFormatter
from .json import JSONFormatter  # JSON is always available

# Core exports that are always available
__all__ = [
    "OutputFormat",
    "OutputFormatter", 
    "JSONFormatter",
]

# Try to import optional formatters with graceful degradation
try:
    from .markdown import MarkdownFormatter
    __all__.append("MarkdownFormatter")
except ImportError:
    pass


try:
    from .xml import XMLFormatter
    __all__.append("XMLFormatter")
except ImportError:
    pass

try:
    from .csv import CSVFormatter
    __all__.append("CSVFormatter")
except ImportError:
    pass

try:
    from .yaml import YAMLFormatter
    __all__.append("YAMLFormatter")
except ImportError:
    pass

try:
    from .registry import FormatterRegistry
    __all__.append("FormatterRegistry")
except ImportError:
    pass