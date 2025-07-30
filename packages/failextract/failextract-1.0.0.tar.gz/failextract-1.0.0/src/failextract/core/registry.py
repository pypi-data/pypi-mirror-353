"""Central feature registry for runtime discovery of available components.

This module provides a centralized registry system that discovers available
features based on installed dependencies. It enables graceful degradation
when optional features are not available.
"""

from typing import Dict, List, Optional, Type, Any, Set
import importlib.util
import logging
from dataclasses import dataclass, field
from pathlib import Path

from ..core.formatters.base import OutputFormatter


logger = logging.getLogger(__name__)


@dataclass
class FeatureInfo:
    """Information about a discovered feature."""
    name: str
    category: str
    available: bool
    dependencies: List[str] = field(default_factory=list)
    error_message: Optional[str] = None
    suggestion: Optional[str] = None


class FeatureRegistry:
    """Central registry for available features and components.
    
    Automatically discovers available features based on installed dependencies
    and provides graceful degradation when features are unavailable.
    """
    
    def __init__(self):
        """Initialize the feature registry."""
        self._formatters: Dict[str, Type[OutputFormatter]] = {}
        self._integrations: Dict[str, Any] = {}
        self._analyzers: Dict[str, Any] = {}
        self._features: Dict[str, FeatureInfo] = {}
        self._core_features: Set[str] = set()
        
        # Discover all available features
        self._discover_features()
    
    def _discover_features(self) -> None:
        """Discover all available features across categories."""
        logger.debug("Starting feature discovery")
        
        # Always register core features
        self._register_core_features()
        
        # Discover optional features
        self._discover_formatters()
        self._discover_config()
        self._discover_cli()
        
        logger.debug(f"Discovered {len(self._features)} total features")
    
    def _register_core_features(self) -> None:
        """Register core features that are always available."""
        # Core formatters
        try:
            from ..core.formatters.json import JSONFormatter
            self._formatters['json'] = JSONFormatter
            self._register_feature('json', 'formatters', True)
            self._core_features.add('json')
        except ImportError as e:
            logger.warning(f"Failed to import core JSON formatter: {e}")
        
        # Core extraction
        self._register_feature('basic_extraction', 'extraction', True)
        self._core_features.add('basic_extraction')
        
        # Core CLI
        self._register_feature('basic_cli', 'cli', True)
        self._core_features.add('basic_cli')
    
    def _discover_formatters(self) -> None:
        """Discover available formatters."""
        # Register built-in formatters (always available)
        try:
            from ..core.formatters.csv import CSVFormatter
            self._formatters['csv'] = CSVFormatter
            self._register_feature('csv', 'formatters', True)
            self._core_features.add('csv')
        except ImportError as e:
            logger.warning(f"Failed to import CSV formatter: {e}")
        
        try:
            from ..core.formatters.markdown import MarkdownFormatter
            self._formatters['markdown'] = MarkdownFormatter
            self._register_feature('markdown', 'formatters', True)
            self._core_features.add('markdown')
        except ImportError as e:
            logger.warning(f"Failed to import Markdown formatter: {e}")
        
        try:
            from ..core.formatters.xml import XMLFormatter
            self._formatters['xml'] = XMLFormatter
            self._register_feature('xml', 'formatters', True)
            self._core_features.add('xml')
        except ImportError as e:
            logger.warning(f"Failed to import XML formatter: {e}")
        
        # YAML formatter requires pyyaml dependency
        try:
            from ..core.formatters.yaml import YAMLFormatter
            self._formatters['yaml'] = YAMLFormatter
            self._register_feature('yaml', 'formatters', True)
        except ImportError:
            self._register_feature(
                'yaml', 'formatters', False,
                dependencies=['pyyaml>=6.0'],
                suggestion='pip install failextract[formatters]'
            )
    
    
    def _discover_config(self) -> None:
        """Discover available configuration features."""
        # Basic configuration is always available
        self._register_feature('basic_config', 'config', True)
        self._core_features.add('basic_config')
        
        # Advanced config features require dependencies
        try:
            import pydantic
            self._register_feature('advanced_validation', 'config', True)
        except ImportError:
            self._register_feature(
                'advanced_validation', 'config', False,
                dependencies=['pydantic>=2.0'],
                suggestion='pip install failextract[config]'
            )
        
        # TOML support for older Python versions
        try:
            import tomllib
            self._register_feature('toml_config', 'config', True)
        except ImportError:
            try:
                import tomli
                self._register_feature('toml_config', 'config', True)
            except ImportError:
                self._register_feature(
                    'toml_config', 'config', False,
                    dependencies=['tomli>=1.2.0; python_version < "3.11"'],
                    suggestion='pip install failextract[config]'
                )
    
    
    def _discover_cli(self) -> None:
        """Discover available CLI features."""
        # Basic CLI is always available (already registered in core features)
        
        # Enhanced CLI features require dependencies
        try:
            import rich
            import typer
            self._register_feature('enhanced_cli', 'cli', True)
        except ImportError:
            self._register_feature(
                'enhanced_cli', 'cli', False,
                dependencies=['rich>=13.0', 'typer>=0.9'],
                suggestion='pip install failextract[cli]'
            )
    
    def _register_feature(
        self, 
        name: str, 
        category: str, 
        available: bool, 
        dependencies: Optional[List[str]] = None,
        suggestion: Optional[str] = None,
        error_message: Optional[str] = None
    ) -> None:
        """Register a feature in the registry."""
        feature = FeatureInfo(
            name=name,
            category=category,
            available=available,
            dependencies=dependencies or [],
            suggestion=suggestion,
            error_message=error_message
        )
        self._features[f"{category}:{name}"] = feature
    
    # Public API methods
    
    def get_available_features(self) -> Dict[str, List[str]]:
        """Get all available features grouped by category."""
        result = {}
        for feature_key, feature in self._features.items():
            if feature.available:
                if feature.category not in result:
                    result[feature.category] = []
                result[feature.category].append(feature.name)
        return result
    
    def get_missing_features(self) -> Dict[str, List[str]]:
        """Get all missing features grouped by category."""
        result = {}
        for feature_key, feature in self._features.items():
            if not feature.available:
                if feature.category not in result:
                    result[feature.category] = []
                result[feature.category].append(feature.name)
        return result
    
    def is_feature_available(self, category: str, name: str) -> bool:
        """Check if a specific feature is available."""
        feature_key = f"{category}:{name}"
        feature = self._features.get(feature_key)
        return feature is not None and feature.available
    
    def get_feature_info(self, category: str, name: str) -> Optional[FeatureInfo]:
        """Get detailed information about a feature."""
        feature_key = f"{category}:{name}"
        return self._features.get(feature_key)
    
    def get_formatter(self, format_name: str) -> Optional[Type[OutputFormatter]]:
        """Get a formatter class by name."""
        return self._formatters.get(format_name)
    
    def get_available_formatters(self) -> List[str]:
        """Get list of available formatter names."""
        return list(self._formatters.keys())
    
    def suggest_installation(self, category: str, name: str) -> Optional[str]:
        """Get installation suggestion for a missing feature."""
        feature = self.get_feature_info(category, name)
        return feature.suggestion if feature else None
    
    def get_core_features(self) -> Set[str]:
        """Get set of core feature names that are always available."""
        return self._core_features.copy()
    
    def is_core_feature(self, name: str) -> bool:
        """Check if a feature is a core feature."""
        return name in self._core_features


# Global registry instance
_registry: Optional[FeatureRegistry] = None


def get_registry() -> FeatureRegistry:
    """Get the global feature registry instance."""
    global _registry
    if _registry is None:
        _registry = FeatureRegistry()
    return _registry


def reset_registry() -> None:
    """Reset the global registry (mainly for testing)."""
    global _registry
    _registry = None