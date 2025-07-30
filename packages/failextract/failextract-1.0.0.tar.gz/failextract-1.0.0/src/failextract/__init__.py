"""Failextract - Comprehensive test failure extraction and reporting library.

This library provides advanced capabilities for extracting, analyzing, and reporting
test failures in pytest-based testing environments. It automatically captures
detailed failure context including fixture information, source code, and dependency
chains to aid in debugging and analysis.

Key Features:
    - Automatic fixture extraction and dependency analysis
    - Multiple output formats (JSON always available, others via extras)
    - Thread-safe singleton design for concurrent test execution
    - Performance-optimized with intelligent caching
    - Extensible formatter system for custom output formats
    - Memory management with configurable limits
    - Integration with pytest through decorators

Optional Feature Extras:
    - Formatters: YAML formatter (pip install failextract[formatters])
    - Config: Advanced configuration validation (pip install failextract[config])
    - CLI: Rich terminal output (pip install failextract[cli])

Example:
    Basic usage with the decorator:

    >>> from failextract import extract_on_failure
    >>>
    >>> @extract_on_failure
    >>> def test_example():
    ...     assert 1 == 2, "This will be captured with full context"

    Generate comprehensive reports:

    >>> from failextract import FailureExtractor, OutputConfig
    >>>
    >>> extractor = FailureExtractor()
    >>> config = OutputConfig("failures.json", format="json")  # JSON always available
    >>> extractor.save_report(config)

Author: Failextract Contributors
License: Apache 2.0
"""

import warnings
import os
from typing import Any, Union, List

# Development mode bypasses graceful degradation for testing
_DEV_MODE = os.environ.get('FAILEXTRACT_DEV_MODE', '').lower() in ('1', 'true', 'yes')

# Core imports (always available)
from .failextract import (
    # Constants
    BUILTIN_FIXTURES,
    # Core classes
    CodeContextExtractor,
    FailureExtractor,
    FixtureExtractor,
    # Output configuration
    OutputConfig,
    OutputFormat,
    extract_failure_info,
    extract_function_source,
    # Decorators and utilities
    extract_on_failure,
    generate_session_report,
    save_failure_report,
    save_single_failure,
    save_with_config,
)

# Core formatters (always available)
from .core.formatters.json import JSONFormatter
from .core.formatters.base import OutputFormatter

# Feature registry for dynamic discovery
from .core.registry import get_registry

__version__ = "1.0.0"
__author__ = "Failextract Contributors"

# Core exports that are always available
__all__ = [
    # Core classes
    "CodeContextExtractor",
    "FixtureExtractor", 
    "FailureExtractor",
    # Output configuration
    "OutputConfig",
    "OutputFormat",
    # Core formatters
    "OutputFormatter",
    "JSONFormatter",
    # Decorators and utilities
    "extract_on_failure",
    "extract_failure_info",
    "extract_function_source",
    "save_single_failure",
    "save_failure_report",
    "save_with_config",
    "generate_session_report",
    # Constants
    "BUILTIN_FIXTURES",
    # Feature detection
    "get_available_features",
    "suggest_installation",
]


def get_available_features() -> dict:
    """Get information about available features based on installed extras.
    
    Returns:
        Dictionary with feature availability information.
    """
    registry = get_registry()
    return {
        'available': registry.get_available_features(),
        'missing': registry.get_missing_features(),
        'core': list(registry.get_core_features()),
    }


def suggest_installation(feature_name: str) -> str:
    """Suggest installation command for a missing feature.
    
    Args:
        feature_name: Name of the feature to install
        
    Returns:
        Installation command suggestion
    """
    registry = get_registry()
    
    # Map common feature names to categories
    feature_map = {
        'xml': ('formatters', 'xml'),
        'yaml': ('formatters', 'yaml'),
        'markdown': ('formatters', 'markdown'),
        'csv': ('formatters', 'csv'),
        'config': ('config', 'basic_config'),
        'configuration': ('config', 'basic_config'),
        'cli': ('cli', 'enhanced_cli'),
    }
    
    if feature_name.lower() in feature_map:
        category, specific_feature = feature_map[feature_name.lower()]
        suggestion = registry.suggest_installation(category, specific_feature)
        return suggestion or f"pip install failextract[{category}]"
    
    return f"pip install failextract[{feature_name}]"


def __getattr__(name: str) -> Any:
    """Dynamic attribute access for optional features with helpful error messages."""
    registry = get_registry()
    
    # Handle formatter requests
    if name.endswith('Formatter') and name != 'OutputFormatter':
        format_name = name.replace('Formatter', '').lower()
        
        if format_name == 'json':
            return JSONFormatter
        
        # In development mode, try direct imports first
        if _DEV_MODE:
            try:
                if format_name == 'xml':
                    from .core.formatters.xml import XMLFormatter
                    return XMLFormatter
                elif format_name == 'yaml':
                    from .core.formatters.yaml import YAMLFormatter
                    return YAMLFormatter
                elif format_name == 'markdown':
                    from .core.formatters.markdown import MarkdownFormatter
                    return MarkdownFormatter
                elif format_name == 'csv':
                    from .core.formatters.csv import CSVFormatter
                    return CSVFormatter
            except ImportError:
                pass  # Fall through to normal handling
        
        # Check if formatter is available
        formatter_class = registry.get_formatter(format_name)
        if formatter_class:
            return formatter_class
        
        # Provide helpful error message
        if format_name in ['xml', 'yaml', 'markdown', 'csv']:
            if _DEV_MODE:
                # In dev mode, show the actual import error
                try:
                    if format_name == 'xml':
                        from .core.formatters.xml import XMLFormatter
                    elif format_name == 'yaml':
                        from .core.formatters.yaml import YAMLFormatter
                    elif format_name == 'markdown':
                        from .core.formatters.markdown import MarkdownFormatter
                    elif format_name == 'csv':
                        from .core.formatters.csv import CSVFormatter
                except ImportError as e:
                    raise ImportError(f"Failed to import {name} in development mode: {e}")
            else:
                # For YAML, suggest the formatters extra
                if format_name == 'yaml':
                    raise ImportError(
                        f"{name} requires additional dependencies. "
                        f"Install with: pip install failextract[formatters]"
                    )
                # Other formatters are built-in but missing
                raise ImportError(f"Failed to import {name} - this should not happen")
    
    # Handle FormatterRegistry
    if name == 'FormatterRegistry':
        if _DEV_MODE:
            from .core.formatters.registry import FormatterRegistry
            return FormatterRegistry
        else:
            try:
                from .core.formatters.registry import FormatterRegistry
                return FormatterRegistry
            except ImportError:
                raise ImportError(
                    f"FormatterRegistry requires additional dependencies. "
                    f"Install with: pip install failextract[formatters]"
                )
    
    # Handle configuration system
    config_exports = [
        'ConfigurationManager', 'ProjectConfig', 'WorkspaceDetector',
        'ConfigurationError', 'ConfigurationSchema', 'OutputSection',
        'WorkspaceSection', 'ExtractionSection', 'FormattingSection', 'MemorySection'
    ]
    if name in config_exports:
        # Import directly from configuration module (always available)
        try:
            from .configuration import (
                ConfigurationManager, ProjectConfig, WorkspaceDetector,
                ConfigurationError, ConfigurationSchema, OutputSection,
                WorkspaceSection, ExtractionSection, FormattingSection, MemorySection
            )
            return locals()[name]
        except ImportError as e:
            raise ImportError(f"Failed to import {name}: {e}")
    
    
    
    # If we get here, the attribute doesn't exist
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")


def _add_optional_exports() -> None:
    """Add optional exports to __all__ if they're available."""
    global __all__
    registry = get_registry()
    
    # Add available formatters to __all__
    available_formatters = registry.get_available_formatters()
    for format_name in available_formatters:
        if format_name != 'json':  # JSON already in core
            formatter_name = f"{format_name.title()}Formatter"
            if formatter_name not in __all__:
                __all__.append(formatter_name)
    
    # Add FormatterRegistry if formatters are available
    if len(available_formatters) > 1:  # More than just JSON
        if 'FormatterRegistry' not in __all__:
            __all__.append('FormatterRegistry')
    
    # Add other optional features based on availability
    available_features = registry.get_available_features()
    
    if 'config' in available_features:
        config_exports = [
            'ConfigurationManager', 'ProjectConfig', 'WorkspaceDetector',
            'ConfigurationError', 'ConfigurationSchema', 'OutputSection',
            'WorkspaceSection', 'ExtractionSection', 'FormattingSection', 'MemorySection'
        ]
        __all__.extend([export for export in config_exports if export not in __all__])
    


# Add optional exports to __all__ based on what's available
_add_optional_exports()