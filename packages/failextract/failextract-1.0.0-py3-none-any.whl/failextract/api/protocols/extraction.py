"""Extraction protocols for type-safe interfaces."""

from typing import Protocol, Dict, Any, List, Optional, runtime_checkable
from abc import abstractmethod


@runtime_checkable
class FailureExtractorProtocol(Protocol):
    """Protocol for failure extraction implementations."""
    
    @abstractmethod
    def extract_failure_info(self, frame: Any, exception: Exception) -> Dict[str, Any]:
        """Extract failure information from a frame and exception."""
        ...
    
    @abstractmethod
    def clear_cache(self) -> None:
        """Clear internal caches."""
        ...
    
    @abstractmethod
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        ...


@runtime_checkable
class CodeContextExtractorProtocol(Protocol):
    """Protocol for code context extraction implementations."""
    
    @abstractmethod
    def extract_context(self, file_path: str, line_number: int, context_lines: int = 5) -> Dict[str, Any]:
        """Extract code context around a specific line."""
        ...
    
    @abstractmethod
    def analyze_imports(self, file_path: str) -> List[Dict[str, Any]]:
        """Analyze imports in a file."""
        ...
    
    @abstractmethod
    def analyze_dependencies(self, file_path: str, max_depth: int = 3) -> Dict[str, Any]:
        """Analyze dependencies of a file."""
        ...


@runtime_checkable
class FixtureExtractorProtocol(Protocol):
    """Protocol for fixture extraction implementations."""
    
    @abstractmethod
    def extract_fixtures(self, frame: Any) -> Dict[str, Any]:
        """Extract fixture information from a frame."""
        ...
    
    @abstractmethod
    def get_fixture_dependencies(self, test_name: str) -> List[str]:
        """Get fixture dependencies for a test."""
        ...