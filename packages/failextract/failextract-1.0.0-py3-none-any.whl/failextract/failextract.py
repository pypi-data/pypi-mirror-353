import ast
import csv
import functools
import importlib.util
import inspect
import io
import json
import sys
import threading
import traceback
import difflib
import hashlib
import re
import sqlite3
import time
from abc import ABC, abstractmethod
from collections import defaultdict, Counter
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Set, Union, Tuple, NamedTuple

# Import core components from new modular structure
from .core.analysis import CodeContextExtractor
from .core.extraction import FixtureExtractor  
from .core.formatters import OutputFormat, OutputFormatter, JSONFormatter

# Try to import optional formatters with graceful degradation
try:
    from .core.formatters import MarkdownFormatter, XMLFormatter, CSVFormatter, YAMLFormatter, FormatterRegistry
except ImportError:
    # These will be available through the registry if the formatters extra is installed
    pass


# Keep existing CodeContextExtractor import for backward compatibility
# (The actual class is now in core.analysis.context_extractor)

# Remove the large class definition and replace with a comment

# [Large class definitions moved to core modules]

class DependencyGraph:
    """Represents a dependency graph for Python files and modules.
    
    This class provides a structured representation of dependencies between
    Python files, including methods for analysis, visualization, and traversal.
    """
    
    def __init__(self):
        """Initialize an empty dependency graph."""
        self.nodes: Dict[str, Dict[str, Any]] = {}  # file_path -> node_info
        self.edges: List[Tuple[str, str, Dict[str, Any]]] = []  # (from, to, edge_info)
        self.root_file: Optional[str] = None
        self.metadata: Dict[str, Any] = {}
    
    @classmethod
    def build_from_file(cls, root_file: str, max_depth: int, 
                       extractor: 'CodeContextExtractor') -> 'DependencyGraph':
        """Build dependency graph from a root file using CodeContextExtractor.
        
        Args:
            root_file: Root file to start analysis from
            max_depth: Maximum depth for dependency traversal
            extractor: CodeContextExtractor instance for analysis
            
        Returns:
            Populated DependencyGraph instance
        """
        graph = cls()
        graph.root_file = root_file
        graph.metadata = {
            'max_depth': max_depth,
            'build_timestamp': datetime.now().isoformat(),
            'total_files_analyzed': 0,
            'circular_dependencies': [],
        }
        
        visited = set()
        to_process = [(root_file, 0)]  # (file_path, depth)
        
        while to_process:
            current_file, depth = to_process.pop(0)
            
            if depth > max_depth or current_file in visited:
                continue
                
            visited.add(current_file)
            
            # Add node for current file
            try:
                file_exists = Path(current_file).exists()
                
                # If file doesn't exist, mark as error
                if not file_exists:
                    graph.nodes[current_file] = {
                        'file_path': current_file,
                        'depth': depth,
                        'error': True,
                        'exists': False,
                        'is_root': current_file == root_file,
                        'import_count': 0,
                    }
                    continue  # Skip processing imports for nonexistent files
                
                imports = extractor.analyze_imports(current_file)
                node_info = {
                    'file_path': current_file,
                    'depth': depth,
                    'imports': imports,
                    'import_count': len(imports),
                    'is_root': current_file == root_file,
                    'exists': True,
                }
                
                # Add file stats for existing files
                stat = Path(current_file).stat()
                node_info.update({
                    'size_bytes': stat.st_size,
                    'modified_time': stat.st_mtime,
                })
                
                graph.nodes[current_file] = node_info
                
                # Process imports and create edges
                for import_info in imports:
                    module_name = import_info['module']
                    if not module_name:
                        continue
                    
                    # Try to resolve module to file path
                    resolved_path = extractor._resolve_module_path(module_name, current_file)
                    
                    if resolved_path and Path(resolved_path).exists():
                        # Create edge
                        edge_info = {
                            'import_type': import_info['type'],
                            'module_name': module_name,
                            'line_number': import_info['line'],
                            'import_level': import_info.get('level', 0),
                        }
                        graph.edges.append((current_file, resolved_path, edge_info))
                        
                        # Add to processing queue if not too deep
                        if depth < max_depth:
                            to_process.append((resolved_path, depth + 1))
                
            except Exception:
                # Add error node
                graph.nodes[current_file] = {
                    'file_path': current_file,
                    'depth': depth,
                    'error': True,
                    'is_root': current_file == root_file,
                }
        
        graph.metadata['total_files_analyzed'] = len(graph.nodes)
        graph._detect_cycles()
        
        return graph
    
    def _detect_cycles(self) -> None:
        """Detect circular dependencies in the graph."""
        # Build adjacency list
        adj_list = {}
        for from_file, to_file, _ in self.edges:
            if from_file not in adj_list:
                adj_list[from_file] = []
            adj_list[from_file].append(to_file)
        
        # DFS to detect cycles
        WHITE, GRAY, BLACK = 0, 1, 2
        colors = {node: WHITE for node in self.nodes}
        cycles = []
        
        def dfs(node: str, path: List[str]) -> None:
            if colors[node] == GRAY:
                # Cycle detected
                cycle_start = path.index(node)
                cycle = path[cycle_start:] + [node]
                cycles.append(cycle)
                return
            
            if colors[node] == BLACK:
                return
            
            colors[node] = GRAY
            path.append(node)
            
            for neighbor in adj_list.get(node, []):
                if neighbor in self.nodes:  # Only process known nodes
                    dfs(neighbor, path.copy())
            
            colors[node] = BLACK
        
        for node in self.nodes:
            if colors[node] == WHITE:
                dfs(node, [])
        
        self.metadata['circular_dependencies'] = cycles
    
    def get_dependencies(self, file_path: str) -> List[str]:
        """Get direct dependencies of a file.
        
        Args:
            file_path: File to get dependencies for
            
        Returns:
            List of file paths that this file depends on
        """
        dependencies = []
        for from_file, to_file, _ in self.edges:
            if from_file == file_path:
                dependencies.append(to_file)
        return dependencies
    
    def get_dependents(self, file_path: str) -> List[str]:
        """Get files that depend on the given file.
        
        Args:
            file_path: File to get dependents for
            
        Returns:
            List of file paths that depend on this file
        """
        dependents = []
        for from_file, to_file, _ in self.edges:
            if to_file == file_path:
                dependents.append(from_file)
        return dependents
    
    def get_node_info(self, file_path: str) -> Optional[Dict[str, Any]]:
        """Get information about a specific node.
        
        Args:
            file_path: File path to get info for
            
        Returns:
            Node information dictionary or None if not found
        """
        return self.nodes.get(file_path)
    
    def get_shortest_path(self, from_file: str, to_file: str) -> Optional[List[str]]:
        """Find shortest path between two files in the dependency graph.
        
        Args:
            from_file: Starting file
            to_file: Target file
            
        Returns:
            List of file paths forming the shortest path, or None if no path exists
        """
        if from_file not in self.nodes or to_file not in self.nodes:
            return None
        
        # BFS for shortest path
        from collections import deque
        
        queue = deque([(from_file, [from_file])])
        visited = {from_file}
        
        while queue:
            current, path = queue.popleft()
            
            if current == to_file:
                return path
            
            # Get neighbors
            for next_file in self.get_dependencies(current):
                if next_file not in visited:
                    visited.add(next_file)
                    queue.append((next_file, path + [next_file]))
        
        return None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert graph to dictionary representation for serialization.
        
        Returns:
            Dictionary containing complete graph data
        """
        return {
            'nodes': self.nodes,
            'edges': [
                {
                    'from': from_file,
                    'to': to_file,
                    'info': edge_info
                }
                for from_file, to_file, edge_info in self.edges
            ],
            'root_file': self.root_file,
            'metadata': self.metadata,
        }
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get graph statistics for analysis.
        
        Returns:
            Dictionary containing graph metrics and statistics
        """
        total_nodes = len(self.nodes)
        total_edges = len(self.edges)
        
        # Calculate in-degree and out-degree for each node
        in_degrees = {}
        out_degrees = {}
        
        for node in self.nodes:
            in_degrees[node] = len(self.get_dependents(node))
            out_degrees[node] = len(self.get_dependencies(node))
        
        # Find nodes with highest dependencies
        most_dependencies = max(out_degrees.items(), key=lambda x: x[1]) if out_degrees else (None, 0)
        most_dependents = max(in_degrees.items(), key=lambda x: x[1]) if in_degrees else (None, 0)
        
        return {
            'total_nodes': total_nodes,
            'total_edges': total_edges,
            'circular_dependencies': len(self.metadata.get('circular_dependencies', [])),
            'max_depth': max(node.get('depth', 0) for node in self.nodes.values()) if self.nodes else 0,
            'root_file': self.root_file,
            'most_dependencies': {
                'file': most_dependencies[0],
                'count': most_dependencies[1]
            },
            'most_dependents': {
                'file': most_dependents[0], 
                'count': most_dependents[1]
            },
            'average_dependencies': sum(out_degrees.values()) / len(out_degrees) if out_degrees else 0,
        }


class FixtureExtractor:
    """Extract fixture definitions and their dependencies.

    This class provides functionality to analyze test functions and extract
    information about pytest fixtures they depend on, including fixture
    definitions, dependencies, and scope information. It uses caching
    for performance optimization.

    Attributes:
        _fixture_cache (Dict[str, Dict[str, Any]]): Internal cache for fixture
            definitions to improve performance on repeated lookups.
    """

    def __init__(self):
        """Initialize the FixtureExtractor with an empty cache.

        Creates a new instance with an empty fixture cache. The cache will
        be populated as fixtures are discovered and analyzed.

        Example:
            >>> extractor = FixtureExtractor()
            >>> fixtures = extractor.get_fixture_info(my_test_function)
            >>> print(len(fixtures))
            3
        """
        self._fixture_cache = {}

    def get_fixture_info(
        self, test_func: Callable, frame_locals: dict = None
    ) -> List[Dict[str, Any]]:
        """Extract all fixtures used by a test function.

        Analyzes the test function's signature to identify fixture dependencies,
        then recursively extracts information about each fixture including its
        definition, scope, dependencies, and source code.

        Args:
            test_func: The test function to analyze for fixture dependencies
            frame_locals: Optional dictionary of local variables from the test
                execution frame, used for enhanced fixture discovery

        Returns:
            List of dictionaries containing fixture information with keys:
            - 'name': Fixture name
            - 'type': Always 'fixture'
            - 'scope': Fixture scope ('function', 'class', 'module', 'session')
            - 'source': Source code of the fixture function
            - 'dependencies': List of other fixtures this fixture depends on
            - 'file': Path to file containing the fixture definition

        Example:
            >>> def test_example(user_fixture, db_fixture):
            ...     pass
            >>> extractor = FixtureExtractor()
            >>> fixtures = extractor.get_fixture_info(test_example)
            >>> print(fixtures[0]['name'])
            'user_fixture'
            >>> print(fixtures[0]['scope'])
            'function'
        """
        fixtures = []
        seen = set()

        # Get fixture names from function signature
        sig = inspect.signature(test_func)
        fixture_names = [
            param
            for param in sig.parameters
            if param not in ["self", "cls"]  # Skip self/cls
        ]

        # Extract each fixture
        for fixture_name in fixture_names:
            if fixture_name not in seen:
                fixture_info = self._extract_fixture_chain(
                    fixture_name, test_func, frame_locals or {}, seen
                )
                fixtures.extend(fixture_info)

        return fixtures

    def _extract_fixture_chain(
        self, fixture_name: str, test_func: Callable, frame_locals: dict, seen: Set[str]
    ) -> List[Dict[str, Any]]:
        """Extract a fixture and all its dependencies."""
        if fixture_name in seen:
            return []

        seen.add(fixture_name)
        fixtures = []

        # Try to find the fixture definition
        fixture_def = self._find_fixture_definition(
            fixture_name, test_func, frame_locals
        )

        if fixture_def:
            fixtures.append(fixture_def)

            # Extract dependencies
            if "dependencies" in fixture_def:
                for dep_name in fixture_def["dependencies"]:
                    dep_fixtures = self._extract_fixture_chain(
                        dep_name, test_func, frame_locals, seen
                    )
                    fixtures.extend(dep_fixtures)

        return fixtures

    def _find_fixture_definition(
        self, fixture_name: str, test_func: Callable, frame_locals: dict
    ) -> Optional[Dict[str, Any]]:
        """Find and extract a fixture definition."""

        # Check cache first
        cache_key = f"{test_func.__module__}:{fixture_name}"
        if cache_key in self._fixture_cache:
            return self._fixture_cache[cache_key]

        fixture_info = None

        # Look in various places for the fixture
        search_locations = [
            # 1. Frame locals (for running fixtures)
            frame_locals,
            # 2. Test module
            sys.modules.get(test_func.__module__).__dict__
            if test_func.__module__ in sys.modules
            else {},
            # 3. Conftest files
            *self._get_conftest_modules(test_func),
        ]

        for location in search_locations:
            if not location:
                continue

            # Look for pytest fixture marker
            for _name, obj in location.items():
                if self._is_fixture(obj, fixture_name):
                    fixture_info = self._extract_fixture_info(obj, fixture_name)
                    if fixture_info:
                        self._fixture_cache[cache_key] = fixture_info
                        return fixture_info

        # Check if it's a built-in fixture
        if fixture_name in BUILTIN_FIXTURES:
            fixture_info = {
                "name": fixture_name,
                "type": "builtin",
                "description": BUILTIN_FIXTURES[fixture_name],
            }
            self._fixture_cache[cache_key] = fixture_info
            return fixture_info

        return None

    def _is_fixture(self, obj: Any, fixture_name: str) -> bool:
        """Check if object is a fixture with the given name."""
        if not callable(obj):
            return False

        # Check for pytest fixture marker
        if hasattr(obj, "_pytestfixturefunction"):
            # Get fixture name (might be different from function name)
            marker = getattr(obj, "_pytestfixturefunction", None)
            if marker:
                fname = getattr(marker, "name", None) or obj.__name__
                return fname == fixture_name

        # Check function name as fallback
        return obj.__name__ == fixture_name

    def _extract_fixture_info(
        self, fixture_func: Callable, fixture_name: str
    ) -> Dict[str, Any]:
        """Extract detailed information about a fixture."""
        info = {
            "name": fixture_name,
            "type": "fixture",
            "function_name": fixture_func.__name__,
        }

        # Get source code
        try:
            info["source"] = inspect.getsource(fixture_func)
            info["file"] = inspect.getfile(fixture_func)
            info["line"] = inspect.getsourcelines(fixture_func)[1]
        except (OSError, TypeError):
            info["source"] = f"# Could not extract source for {fixture_name}"

        # Get fixture metadata
        if hasattr(fixture_func, "_pytestfixturefunction"):
            marker = fixture_func._pytestfixturefunction
            info["scope"] = getattr(marker, "scope", "function")
            info["params"] = getattr(marker, "params", None)
            info["autouse"] = getattr(marker, "autouse", False)
            info["ids"] = getattr(marker, "ids", None)

        # Extract dependencies
        sig = inspect.signature(fixture_func)
        dependencies = [
            param for param in sig.parameters if param not in ["self", "cls", "request"]
        ]
        if dependencies:
            info["dependencies"] = dependencies

        # Check if it's a yield fixture
        if info.get("source"):
            info["is_yield_fixture"] = "yield" in info["source"]

        return info

    def _get_conftest_modules(self, test_func: Callable) -> List[dict]:
        """Get all conftest modules in the hierarchy."""
        modules = []

        try:
            test_file = Path(inspect.getfile(test_func))
            current_dir = test_file.parent

            # Walk up directory tree looking for conftest.py files
            while current_dir != current_dir.parent:
                conftest_path = current_dir / "conftest.py"
                if conftest_path.exists():
                    # Import conftest module
                    spec = importlib.util.spec_from_file_location(
                        f"conftest_{current_dir.name}", conftest_path
                    )
                    if spec and spec.loader:
                        module = importlib.util.module_from_spec(spec)
                        spec.loader.exec_module(module)
                        modules.append(module.__dict__)

                current_dir = current_dir.parent
        except Exception:
            pass

        return modules


# Built-in pytest fixtures
BUILTIN_FIXTURES = {
    "request": "Pytest request object containing test context",
    "tmp_path": "Temporary directory unique to test invocation",
    "tmp_path_factory": "Factory for creating temporary directories",
    "pytestconfig": "Access to configuration values and plugin manager",
    "cache": "Store and retrieve values across test runs",
    "capfd": "Capture file descriptors stdout/stderr",
    "capfdbinary": "Capture binary file descriptors",
    "caplog": "Capture log messages",
    "capsys": "Capture system stdout/stderr",
    "capsysbinary": "Capture binary system output",
    "doctest_namespace": "Namespace for doctest execution",
    "monkeypatch": "Modify objects, dict items, os.environ, etc.",
    "pytester": "Plugin testing helper",
    "recwarn": "Record warnings",
    "tmpdir": "Temporary directory (legacy, use tmp_path)",
}


def _extract_failure_info_legacy(exception, frame, config=None, enhanced_context=True, 
                                code_context_lines=5, include_line_numbers=True, max_code_lines=100):
    """Legacy implementation for backward compatibility."""
    # Build basic failure info
    result = {
        'test_name': frame.f_code.co_name,
        'test_module': frame.f_globals.get('__name__', 'unknown'),
        'test_file': frame.f_code.co_filename,
        'timestamp': datetime.now().isoformat(),
        'exception_type': type(exception).__name__,
        'exception_message': str(exception),
        'exception_traceback': traceback.format_exc(),
        'enhanced_context': enhanced_context,
    }
    
    # Get test source using simple approach
    try:
        with open(frame.f_code.co_filename, 'r') as f:
            lines = f.readlines()
        result['test_source'] = ''.join(lines)
    except:
        result['test_source'] = 'Source not available'
    
    # Add enhanced context if requested
    if enhanced_context:
        extractor = CodeContextExtractor()
        context = extractor.extract_function_source_with_context(
            frame, context_lines=code_context_lines, 
            include_line_numbers=include_line_numbers,
            max_lines=max_code_lines
        )
        if context and 'error' not in context:
            result['test_source_with_context'] = context
    
    # Add empty lists for compatibility
    result['extracted_code'] = []
    result['fixtures'] = []
    
    return result


def extract_failure_info(
    test_func_or_exception,
    exception_or_frame=None,
    args: tuple = None,
    kwargs: dict = None,
    frame_locals: dict = None,
    include_locals: bool = False,
    include_fixtures: bool = True,
    max_depth: int = 10,
    skip_stdlib: bool = True,
    extract_classes: bool = True,
    code_context_lines: int = 5,
    enhanced_context: bool = True,
    include_line_numbers: bool = True,
    max_code_lines: int = 100,
    config=None  # For backward compatibility
) -> Dict[str, Any]:
    """Extract comprehensive failure information including fixtures and enhanced code context.

    Supports both new signature: extract_failure_info(test_func, exception, args, kwargs, ...)
    And legacy signature: extract_failure_info(exception, frame, config=...)

    Args:
        test_func_or_exception: The test function that failed OR exception (for backward compatibility)
        exception_or_frame: The exception that was raised OR frame (for backward compatibility)
        args: Arguments passed to the test function
        kwargs: Keyword arguments passed to the test function
        frame_locals: Local variables from the test frame
        include_locals: Whether to include local variables in the output
        include_fixtures: Whether to extract fixture information
        max_depth: Maximum traceback depth to analyze
        skip_stdlib: Whether to skip standard library frames
        extract_classes: Whether to extract class source for methods
        code_context_lines: Number of context lines around failure points
        enhanced_context: Whether to use enhanced CodeContextExtractor
        include_line_numbers: Whether to include line numbers in source
        max_code_lines: Maximum lines of code per frame
        config: OutputConfig for backward compatibility

    Returns:
        Dictionary containing comprehensive failure information with enhanced code context
    """
    
    # Handle backward compatibility: extract_failure_info(exception, frame, config=...)
    if isinstance(test_func_or_exception, Exception) and hasattr(exception_or_frame, 'f_code'):
        # Legacy signature detected
        exception = test_func_or_exception
        frame = exception_or_frame
        
        # Apply config if provided
        if config:
            enhanced_context = getattr(config, 'enhanced_context', True)
            code_context_lines = getattr(config, 'code_context_lines', 5)
            include_line_numbers = getattr(config, 'include_line_numbers', True)
            max_code_lines = getattr(config, 'max_code_lines', 100)
        
        # Try to extract test function from frame
        test_func = None
        try:
            import types
            test_func = types.FunctionType(frame.f_code, frame.f_globals)
        except:
            pass
        
        return _extract_failure_info_legacy(exception, frame, config, enhanced_context, 
                                          code_context_lines, include_line_numbers, max_code_lines)
    
    # New signature: proceed with normal processing
    test_func = test_func_or_exception
    exception = exception_or_frame

    # Get test source
    test_source = inspect.getsource(test_func)
    test_file = inspect.getfile(test_func)

    # Extract fixtures if requested
    fixtures = []
    if include_fixtures:
        extractor = FixtureExtractor()
        fixtures = extractor.get_fixture_info(test_func, frame_locals)

    # Extract traceback information
    tb = exception.__traceback__
    extracted_code = []
    seen_functions = set()
    depth = 0

    while tb is not None and depth < max_depth:
        frame = tb.tb_frame
        filename = frame.f_code.co_filename
        func_name = frame.f_code.co_name

        # Skip test file itself and optionally stdlib
        skip = (
            filename == test_file
            or filename.startswith("<")
            or (
                skip_stdlib
                and ("site-packages" in filename or filename.startswith(sys.prefix))
            )
        )

        if not skip:
            func_id = f"{filename}:{func_name}"

            if func_id not in seen_functions:
                seen_functions.add(func_id)

                # Extract function source with enhanced context if enabled
                if enhanced_context:
                    try:
                        context_extractor = CodeContextExtractor()
                        enhanced_source_info = (
                            context_extractor.extract_function_source_with_context(
                                frame,
                                context_lines=code_context_lines,
                                include_line_numbers=include_line_numbers,
                            )
                        )

                        if (
                            enhanced_source_info
                            and len(enhanced_source_info.get("source", "").splitlines())
                            <= max_code_lines
                        ):
                            func_source = enhanced_source_info["source"]
                            code_info = {
                                "file": filename,
                                "function": func_name,
                                "line": tb.tb_lineno,
                                "source": func_source,
                                "enhanced_context": enhanced_source_info,
                            }
                        else:
                            # Fallback to simple extraction if enhanced fails or too large
                            func_source = extract_function_source(frame)
                            code_info = {
                                "file": filename,
                                "function": func_name,
                                "line": tb.tb_lineno,
                                "source": func_source,
                            }
                    except Exception:
                        # Fallback to simple extraction on any error
                        func_source = extract_function_source(frame)
                        code_info = {
                            "file": filename,
                            "function": func_name,
                            "line": tb.tb_lineno,
                            "source": func_source,
                        }
                else:
                    # Use simple extraction when enhanced context is disabled
                    func_source = extract_function_source(frame)
                    code_info = {
                        "file": filename,
                        "function": func_name,
                        "line": tb.tb_lineno,
                        "source": func_source,
                    }

                # Extract class if this is a method
                class_source = None
                if extract_classes and "self" in frame.f_locals:
                    obj = frame.f_locals["self"]
                    try:
                        class_source = inspect.getsource(obj.__class__)
                    except (OSError, TypeError, AttributeError):
                        # OSError: source file not available
                        # TypeError: obj is not a class or built-in
                        # AttributeError: obj doesn't have __class__
                        pass

                if class_source:
                    code_info["class_source"] = class_source

                if include_locals:
                    # Filter out non-serializable locals
                    safe_locals = {}
                    for k, v in frame.f_locals.items():
                        try:
                            json.dumps(v)
                            safe_locals[k] = v
                        except (TypeError, ValueError, OverflowError):
                            # TypeError: object not JSON serializable
                            # ValueError: circular reference or invalid value
                            # OverflowError: value too large for JSON
                            safe_locals[k] = f"<{type(v).__name__} object>"
                    code_info["locals"] = safe_locals

                extracted_code.append(code_info)

        tb = tb.tb_next
        depth += 1

    # Create failure record
    failure_data = {
        "timestamp": datetime.now().isoformat(),
        "test_name": test_func.__name__,
        "test_module": test_func.__module__,
        "test_file": test_file,
        "test_source": test_source,
        "test_args": repr(args),
        "test_kwargs": repr(kwargs),
        "exception_type": type(exception).__name__,
        "exception_message": str(exception),
        "exception_traceback": traceback.format_exc(),
        "extracted_code": extracted_code,
    }

    if fixtures:
        failure_data["fixtures"] = fixtures

    return failure_data


def extract_function_source(frame) -> Optional[str]:
    """Extract complete function source from a frame."""
    try:
        # Try to get function object directly
        func_name = frame.f_code.co_name
        # Look in frame locals/globals for the function
        func = frame.f_locals.get(func_name) or frame.f_globals.get(func_name)
        if func and callable(func):
            return inspect.getsource(func)

        # Parse source file with AST
        filename = frame.f_code.co_filename
        if not Path(filename).exists() or filename.startswith("<"):
            return None

        with open(filename, "r") as f:
            source = f.read()

        tree = ast.parse(source)
        lineno = frame.f_lineno

        # Find the smallest function/class containing this line
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                if hasattr(node, "lineno") and hasattr(node, "end_lineno"):
                    if node.lineno <= lineno <= (node.end_lineno or node.lineno):
                        # Extract source for this node
                        lines = source.splitlines()
                        return "\n".join(lines[node.lineno - 1 : node.end_lineno])

        return None
    except Exception:
        return None


def save_single_failure(failure_data: Dict[str, Any], filename: str):
    """Save a single failure to a file."""
    failures = []
    if Path(filename).exists():
        try:
            with open(filename, "r") as f:
                failures = json.load(f)
        except (json.JSONDecodeError, ValueError):
            # If file exists but contains invalid JSON, start fresh
            failures = []

    failures.append(failure_data)

    with open(filename, "w") as f:
        json.dump(failures, f, indent=2, default=str)


# Convenience functions
def save_failure_report(
    filename: str = "test_failures_report.json", format: str = "json"
):
    """Save all collected failures to a file."""
    extractor = FailureExtractor()
    config = OutputConfig(output=filename, format=format)
    extractor.save_report(config)


class OutputFormat(Enum):
    """Supported output formats."""

    JSON = "json"
    MARKDOWN = "md"
    YAML = "yaml"
    XML = "xml"
    CSV = "csv"
    CUSTOM = "custom"


class OutputFormatter(ABC):
    """Base class for output formatters."""

    @abstractmethod
    def format(self, failures: List[Dict[str, Any]]) -> str:
        """Format failure data for output."""
        pass

    @abstractmethod
    def get_extension(self) -> str:
        """Get default file extension."""
        pass


class JSONFormatter(OutputFormatter):
    """JSON output formatter."""

    def format(self, failures: List[Dict[str, Any]]) -> str:
        return json.dumps(failures, indent=2, default=str)

    def get_extension(self) -> str:
        return ".json"


class MarkdownFormatter(OutputFormatter):
    """Markdown output formatter."""

    def format(self, failures: List[Dict[str, Any]]) -> str:
        output = ["# Test Failure Report\n"]
        output.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        output.append(f"Total Failures: {len(failures)}\n\n")

        # Table of contents
        if len(failures) >= 3:
            output.append("## Table of Contents\n")
            for i, failure in enumerate(failures, 1):
                test_name = failure["test_name"]
                anchor = test_name.lower().replace("_", "-")
                output.append(f"- [Failure {i}: {test_name}](#{anchor}-{i})\n")
            output.append("\n")

        for i, failure in enumerate(failures, 1):
            anchor = failure["test_name"].lower().replace("_", "-")
            output.append(
                f"## Failure {i}: `{failure['test_name']}` {{#{anchor}-{i}}}\n\n"
            )

            if "test_module" in failure:
                output.append(f"**Module:** `{failure['test_module']}`  \n")
            if "test_file" in failure:
                output.append(f"**File:** `{failure['test_file']}`  \n")
            if "timestamp" in failure:
                output.append(f"**Time:** {failure['timestamp']}  \n\n")
            else:
                output.append("\n")

            # Test code
            if "test_source" in failure:
                output.append("### Test Code\n")
                if failure.get("enhanced_context") and failure.get(
                    "test_source_with_context"
                ):
                    output.append(
                        self._format_markdown_code_context(
                            failure["test_source_with_context"]
                        )
                    )
                else:
                    output.append("```python\n")
                    output.append(failure["test_source"])
                    output.append("```\n\n")

            # Fixtures
            if failure.get("fixtures"):
                output.append("### Fixtures Used\n")
                for fixture in failure["fixtures"]:
                    output.append(f"#### `{fixture['name']}` ")
                    if fixture["type"] == "builtin":
                        output.append("(built-in)\n")
                        output.append(f"> {fixture['description']}\n\n")
                    else:
                        output.append(f"(scope: {fixture.get('scope', 'function')})\n")
                        if fixture.get("file"):
                            output.append(f"**File:** `{fixture['file']}`  \n")
                        if fixture.get("dependencies"):
                            deps = ", ".join(f"`{d}`" for d in fixture["dependencies"])
                            output.append(f"**Dependencies:** {deps}  \n")
                        if fixture.get("enhanced_source"):
                            output.append("\n")
                            output.append(
                                self._format_markdown_code_context(
                                    fixture["enhanced_source"]
                                )
                            )
                        else:
                            output.append("\n```python\n")
                            output.append(
                                fixture.get("source", "# Source not available")
                            )
                            output.append("```\n\n")

            # Tested code (optional)
            if failure.get("extracted_code"):
                output.append("### Tested Code\n")
                for code in failure["extracted_code"]:
                    func_info = (
                        f"`{code['file']}` - `{code['function']}()` line {code['line']}"
                    )
                    output.append(f"#### {func_info}\n")
                    if code.get("source"):
                        output.append("```python\n")
                        output.append(code["source"])
                        output.append("```\n")
                    output.append("\n")

            # Error details
            # Error details (optional)
            if "exception_type" in failure or "exception_message" in failure:
                output.append("### Error Details\n")
                if "exception_type" in failure:
                    output.append(f"**Type:** `{failure['exception_type']}`  \n")
                if "exception_message" in failure:
                    output.append(f"**Message:** {failure['exception_message']}  \n\n")
                else:
                    output.append("\n")

            if failure.get("exception_traceback"):
                output.append("<details>\n<summary>Full Traceback</summary>\n\n```\n")
                output.append(failure["exception_traceback"])
                output.append("```\n</details>\n\n")

            output.append("---\n\n")

        return "".join(output)

    def _format_markdown_code_context(self, source_info: Dict[str, Any]) -> str:
        """Format source code with enhanced context for Markdown."""
        if not isinstance(source_info, dict):
            return f"```python\n{source_info}\n```\n\n"

        lines = source_info.get("lines", [])
        start_line = source_info.get("start_line", 1)
        include_line_numbers = source_info.get("include_line_numbers", True)

        if include_line_numbers:
            output = ["```python"]
            for i, line in enumerate(lines):
                line_num = start_line + i
                # Use comment format to show line numbers in markdown
                output.append(f"# Line {line_num}")
                output.append(line)
            output.append("```\n\n")
            return "\n".join(output)
        else:
            return f"```python\n" + "\n".join(lines) + "\n```\n\n"

    def get_extension(self) -> str:
        return ".md"


class XMLFormatter(OutputFormatter):
    """XML output formatter."""

    def format(self, failures: List[Dict[str, Any]]) -> str:
        xml = ['<?xml version="1.0" encoding="UTF-8"?>']
        xml.append("<testFailureReport>")
        xml.append("  <metadata>")
        xml.append(f"    <generated>{datetime.now().isoformat()}</generated>")
        xml.append(f"    <totalFailures>{len(failures)}</totalFailures>")
        xml.append("  </metadata>")
        xml.append("  <failures>")

        for failure in failures:
            xml.append("    <failure>")
            xml.append(
                f"      <testName>{self._escape_xml(failure['test_name'])}</testName>"
            )
            xml.append(
                f"      <module>{self._escape_xml(failure['test_module'])}</module>"
            )
            xml.append(f"      <file>{self._escape_xml(failure['test_file'])}</file>")
            xml.append(f"      <timestamp>{failure['timestamp']}</timestamp>")
            escaped_type = self._escape_xml(failure["exception_type"])
            xml.append(f"      <exceptionType>{escaped_type}</exceptionType>")
            escaped_msg = self._escape_xml(failure["exception_message"])
            xml.append(f"      <exceptionMessage>{escaped_msg}</exceptionMessage>")
            xml.append("      <testSource><![CDATA[")
            xml.append(failure["test_source"])
            xml.append("]]></testSource>")
            xml.append("    </failure>")

        xml.append("  </failures>")
        xml.append("</testFailureReport>")
        return "\n".join(xml)

    def _escape_xml(self, text: str) -> str:
        """Escape XML special characters."""
        return (
            text.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;")
            .replace("'", "&apos;")
        )

    def get_extension(self) -> str:
        return ".xml"


class CSVFormatter(OutputFormatter):
    """CSV output formatter for basic failure information."""

    def format(self, failures: List[Dict[str, Any]]) -> str:
        output = io.StringIO()
        writer = csv.writer(output)

        # Header
        writer.writerow(
            [
                "Test Name",
                "Module",
                "File",
                "Timestamp",
                "Exception Type",
                "Exception Message",
                "Line Number",
            ]
        )

        # Data rows
        for failure in failures:
            # Get first line number from extracted code
            line_no = ""
            if failure.get("extracted_code"):
                line_no = str(failure["extracted_code"][0].get("line", ""))

            writer.writerow(
                [
                    failure["test_name"],
                    failure["test_module"],
                    failure["test_file"],
                    failure["timestamp"],
                    failure["exception_type"],
                    failure["exception_message"],
                    line_no,
                ]
            )

        return output.getvalue()

    def get_extension(self) -> str:
        return ".csv"


class YAMLFormatter(OutputFormatter):
    """YAML output formatter for structured data."""

    def format(self, failures: List[Dict[str, Any]]) -> str:
        try:
            import yaml
        except ImportError:
            raise ImportError(
                "PyYAML is required for YAML output format. "
                "Install it with: pip install PyYAML"
            ) from None

        # Structure the data for YAML output
        output_data = {
            "test_failure_report": {
                "metadata": {
                    "generated": datetime.now().isoformat(),
                    "total_failures": len(failures),
                },
                "failures": [],
            }
        }

        for failure in failures:
            failure_data = {
                "test_info": {
                    "name": failure["test_name"],
                    "module": failure["test_module"],
                    "file": failure["test_file"],
                    "timestamp": failure["timestamp"],
                },
                "exception": {
                    "type": failure["exception_type"],
                    "message": failure["exception_message"],
                },
                "test_source": failure["test_source"],
            }

            # Add test arguments if present
            if failure.get("test_args") and failure["test_args"] != "()":
                failure_data["test_info"]["args"] = failure["test_args"]
            if failure.get("test_kwargs") and failure["test_kwargs"] != "{}":
                failure_data["test_info"]["kwargs"] = failure["test_kwargs"]

            # Add fixtures if present
            if failure.get("fixtures"):
                failure_data["fixtures"] = []
                for fixture in failure["fixtures"]:
                    fixture_data = {"name": fixture["name"], "type": fixture["type"]}
                    if fixture["type"] == "builtin":
                        fixture_data["description"] = fixture["description"]
                    else:
                        if fixture.get("scope"):
                            fixture_data["scope"] = fixture["scope"]
                        if fixture.get("file"):
                            fixture_data["file"] = fixture["file"]
                        if fixture.get("dependencies"):
                            fixture_data["dependencies"] = fixture["dependencies"]
                        if fixture.get("source"):
                            fixture_data["source"] = fixture["source"]
                    failure_data["fixtures"].append(fixture_data)

            # Add extracted code if present
            if failure.get("extracted_code"):
                failure_data["extracted_code"] = []
                for code in failure["extracted_code"]:
                    code_data = {
                        "file": code["file"],
                        "function": code["function"],
                        "line": code["line"],
                    }
                    if code.get("source"):
                        code_data["source"] = code["source"]
                    if code.get("class_source"):
                        code_data["class_source"] = code["class_source"]
                    if code.get("locals"):
                        code_data["locals"] = code["locals"]
                    failure_data["extracted_code"].append(code_data)

            # Add full traceback if present
            if failure.get("exception_traceback"):
                failure_data["exception"]["traceback"] = failure["exception_traceback"]

            output_data["test_failure_report"]["failures"].append(failure_data)

        return yaml.dump(
            output_data, default_flow_style=False, sort_keys=False, indent=2
        )

    def get_extension(self) -> str:
        return ".yaml"


class FormatterRegistry:
    """Registry for output formatters."""

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


class OutputConfig:
    """Configuration for output handling and report generation.

    This class manages all configuration options for generating test failure
    reports, including output format, file paths, append behavior, content
    filtering options, and enhanced code inclusion settings.

    Attributes:
        filename (Optional[str]): Path to output file, None for stdout
        format (OutputFormat): Output format for the report
        append (bool): Whether to append to existing file
        include_passed (bool): Whether to include passed tests in report
        max_failures (Optional[int]): Maximum number of failures to include
        include_source (bool): Whether to include source code in reports
        include_fixtures (bool): Whether to include fixture information
        code_context_lines (int): Number of context lines around failure points
        max_code_lines (int): Maximum lines of code to include per failure
        include_line_numbers (bool): Whether to include line numbers in source code
        enhanced_context (bool): Whether to use enhanced CodeContextExtractor
        include_traceback (bool): Whether to include traceback information
        include_metadata (bool): Whether to include metadata in reports
        timestamp_format (str): Format string for timestamps
    """

    def __init__(
        self,
        output: Union[str, Path, OutputFormat, None] = None,
        format: Union[str, OutputFormat, None] = None,
        append: bool = False,
        include_passed: bool = False,
        max_failures: Optional[int] = None,
        include_source: bool = True,
        include_fixtures: bool = True,
        code_context_lines: int = 5,
        max_code_lines: int = 100,
        include_line_numbers: bool = True,
        enhanced_context: bool = True,
        # Additional parameters for backward compatibility
        include_traceback: bool = True,
        include_metadata: bool = True,
        timestamp_format: str = "%Y-%m-%dT%H:%M:%S",
    ):
        """Initialize output configuration with validation.

        Creates a new output configuration with automatic format detection
        from file extensions and comprehensive parameter validation.

        Args:
            output: Output destination - file path (str/Path) or format enum.
                If None, outputs to stdout with JSON format.
            format: Explicit format specification, overrides format detection
                from file extension. Can be OutputFormat enum or string.
            append: If True, append to existing file instead of overwriting
            include_passed: If True, include passed tests in the report
            max_failures: Maximum number of failures to include in report
            include_source: If True, include source code in failure reports
            include_fixtures: If True, include fixture information in reports
            code_context_lines: Number of lines to include before/after failure points
            max_code_lines: Maximum total lines of code per failure (performance limit)
            include_line_numbers: If True, add line numbers to source code display
            enhanced_context: If True, use enhanced CodeContextExtractor for better context

        Raises:
            ValueError: If output format cannot be determined or is invalid
            TypeError: If parameters have incorrect types

        Example:
            >>> # Output to JSON file
            >>> config = OutputConfig("failures.json")
            >>> print(config.format)
            OutputFormat.JSON

            >>> # Explicit format override
            >>> config = OutputConfig("report.txt", format="markdown")
            >>> print(config.format)
            OutputFormat.MARKDOWN

            >>> # Append mode with filtering
            >>> config = OutputConfig(
            ...     "results.json",
            ...     append=True,
            ...     max_failures=50
            ... )
            >>> print(config.append)
            True
        """
        # Convert and validate parameters
        # Strict validation for core parameters (per test expectations)
        append = self._validate_bool_strict(append, "append")
        include_passed = self._validate_bool_strict(include_passed, "include_passed")
        include_source = self._convert_to_bool(include_source)
        include_fixtures = self._convert_to_bool(include_fixtures)
        include_line_numbers = self._convert_to_bool(include_line_numbers)
        enhanced_context = self._convert_to_bool(enhanced_context)
        include_traceback = self._convert_to_bool(include_traceback)
        include_metadata = self._convert_to_bool(include_metadata)
        
        code_context_lines = self._convert_to_int(code_context_lines, "code_context_lines")
        max_code_lines = self._convert_to_int(max_code_lines, "max_code_lines")
        
        if max_failures is not None:
            max_failures = self._validate_int_strict(max_failures, "max_failures")
        
        self._validate_parameters(
            output,
            format,
            append,
            include_passed,
            max_failures,
            include_source,
            include_fixtures,
            code_context_lines,
            max_code_lines,
            include_line_numbers,
            enhanced_context,
        )

        self.append = append
        self.include_passed = include_passed
        self.max_failures = max_failures
        self.include_source = include_source
        self.include_fixtures = include_fixtures
        self.code_context_lines = code_context_lines
        self.max_code_lines = max_code_lines
        self.include_line_numbers = include_line_numbers
        self.enhanced_context = enhanced_context
        # Additional parameters for backward compatibility
        self.include_traceback = include_traceback
        self.include_metadata = include_metadata
        self.timestamp_format = timestamp_format

        # Determine output file and format
        if output is None:
            self.filename = None
            self.format = OutputFormat.JSON
        elif isinstance(output, OutputFormat):
            # Use explicit format parameter if provided, otherwise use output format
            if format is not None:
                if isinstance(format, str):
                    format_aliases = {"markdown": "md", "yml": "yaml"}
                    actual_format = format_aliases.get(format, format)
                    self.format = OutputFormat(actual_format)
                else:
                    self.format = format
            else:
                self.format = output
            formatter = FormatterRegistry.get_formatter(self.format)
            self.filename = f"test_failures{formatter.get_extension()}"
        elif isinstance(output, (str, Path)):
            self.filename = str(output)
            # Detect format from extension or use provided format
            if format:
                if isinstance(format, str):
                    # Handle format aliases
                    format_aliases = {"markdown": "md", "yml": "yaml"}
                    actual_format = format_aliases.get(format, format)

                    try:
                        self.format = OutputFormat(actual_format)
                    except ValueError:
                        all_valid = [f.value for f in OutputFormat] + list(
                            format_aliases.keys()
                        )
                        raise ValueError(
                            f"Invalid format string: {format}. "
                            f"Valid formats: {all_valid}"
                        ) from None
                elif isinstance(format, OutputFormat):
                    self.format = format
                else:
                    raise TypeError(
                        f"Format must be string or OutputFormat, got {type(format)}"
                    )
            else:
                self.format = FormatterRegistry.detect_format(self.filename)
        else:
            raise TypeError(
                f"Output must be None, string, Path, or OutputFormat, "
                f"got {type(output)}"
            )

    def _convert_to_bool(self, value):
        """Convert value to boolean with flexible interpretation."""
        if value is None:
            raise TypeError("Boolean parameter cannot be None")
        if isinstance(value, bool):
            return value
        if isinstance(value, int):
            return bool(value)
        if isinstance(value, str):
            lower_val = value.lower()
            if lower_val in ('true', '1', 'yes', 'on'):
                return True
            elif lower_val in ('false', '0', 'no', 'off'):
                return False
            else:
                raise ValueError(f"Cannot convert '{value}' to boolean")
        return bool(value)
    
    def _validate_bool_strict(self, value, param_name):
        """Strict boolean validation - only accepts actual bool values."""
        if not isinstance(value, bool):
            raise TypeError(f"{param_name} must be bool, got {type(value).__name__}")
        return value
    
    def _validate_int_strict(self, value, param_name):
        """Strict integer validation - only accepts actual int values or None."""
        if value is not None and not isinstance(value, int):
            raise TypeError(f"{param_name} must be int or None, got {type(value).__name__}")
        return value
    
    def _convert_to_int(self, value, param_name):
        """Convert value to integer with validation."""
        if isinstance(value, int):
            return value
        if isinstance(value, str):
            try:
                return int(value)
            except ValueError:
                raise TypeError(f"Cannot convert '{value}' to integer for {param_name}")
        raise TypeError(f"{param_name} must be int or string, got {type(value)}")

    def _validate_parameters(
        self,
        output: Union[str, Path, OutputFormat, None],
        format: Union[str, OutputFormat, None],
        append: bool,
        include_passed: bool,
        max_failures: Optional[int],
        include_source: bool,
        include_fixtures: bool,
        code_context_lines: int,
        max_code_lines: int,
        include_line_numbers: bool,
        enhanced_context: bool,
    ) -> None:
        """Validate all parameters for type and value correctness."""

        # Validate append parameter
        if not isinstance(append, bool):
            raise TypeError(f"append must be bool, got {type(append)}")

        # Validate include_passed parameter
        if not isinstance(include_passed, bool):
            raise TypeError(f"include_passed must be bool, got {type(include_passed)}")

        # Validate max_failures parameter
        if max_failures is not None:
            if not isinstance(max_failures, int):
                raise TypeError(
                    f"max_failures must be int or None, got {type(max_failures)}"
                )
            if max_failures <= 0:
                raise ValueError(f"max_failures must be positive, got {max_failures}")

        # Validate include_source parameter
        if not isinstance(include_source, bool):
            raise TypeError(f"include_source must be bool, got {type(include_source)}")

        # Validate include_fixtures parameter
        if not isinstance(include_fixtures, bool):
            raise TypeError(
                f"include_fixtures must be bool, got {type(include_fixtures)}"
            )

        # Validate code_context_lines parameter
        if not isinstance(code_context_lines, int):
            raise TypeError(
                f"code_context_lines must be int, got {type(code_context_lines)}"
            )
        if code_context_lines < 0:
            raise ValueError(
                f"code_context_lines must be non-negative, got {code_context_lines}"
            )

        # Validate max_code_lines parameter
        if not isinstance(max_code_lines, int):
            raise TypeError(f"max_code_lines must be int, got {type(max_code_lines)}")
        if max_code_lines <= 0:
            raise ValueError(f"max_code_lines must be positive, got {max_code_lines}")

        # Validate include_line_numbers parameter
        if not isinstance(include_line_numbers, bool):
            raise TypeError(
                f"include_line_numbers must be bool, got {type(include_line_numbers)}"
            )

        # Validate enhanced_context parameter
        if not isinstance(enhanced_context, bool):
            raise TypeError(
                f"enhanced_context must be bool, got {type(enhanced_context)}"
            )

        # Validate output parameter
        if output is not None and not isinstance(output, (str, Path, OutputFormat)):
            raise TypeError(
                f"output must be None, string, Path, or OutputFormat, "
                f"got {type(output)}"
            )

        # Validate format parameter
        if format is not None and not isinstance(format, (str, OutputFormat)):
            raise TypeError(
                f"format must be None, string, or OutputFormat, got {type(format)}"
            )

        # Validate string format values (allow common aliases)
        if isinstance(format, str):
            valid_formats = [f.value for f in OutputFormat]
            format_aliases = {"markdown": "md", "yml": "yaml"}

            # Check if format is valid directly or through alias
            if format not in valid_formats and format not in format_aliases:
                all_valid = valid_formats + list(format_aliases.keys())
                raise ValueError(
                    f"Invalid format string: {format}. Valid formats: {all_valid}"
                )

        # Validate file path if provided
        if isinstance(output, (str, Path)):
            path_str = str(output)
            if not path_str.strip():
                raise ValueError("Output file path cannot be empty")

            # Check for invalid characters (basic validation)
            invalid_chars = ["<", ">", ":", '"', "|", "?", "*"]
            if any(char in path_str for char in invalid_chars):
                raise ValueError(
                    f"Output file path contains invalid characters: {path_str}"
                )

            # Note: Don't validate parent directory existence in config validation
            # as this is a configuration object that should be created before
            # directories exist. Directory creation should be handled during actual
            # file writing operations

        # Validate format consistency with output
        if isinstance(output, (str, Path)) and isinstance(format, (str, OutputFormat)):
            detected_format = FormatterRegistry.detect_format(str(output))

            if isinstance(format, str):
                # Handle format aliases before validation
                format_aliases = {"markdown": "md", "yml": "yaml"}
                actual_format = format_aliases.get(format, format)
                try:
                    provided_format = OutputFormat(actual_format)
                except ValueError:
                    # This should have been caught earlier, but handle gracefully
                    provided_format = detected_format
            else:
                provided_format = format

            if detected_format != provided_format:
                import warnings

                warnings.warn(
                    f"Format mismatch: file extension suggests {detected_format.value} "
                    f"but format parameter specifies {provided_format.value}. "
                    f"Using specified format: {provided_format.value}",
                    UserWarning,
                    stacklevel=2,
                )

    def __str__(self):
        """Return string representation of OutputConfig."""
        return (
            f"OutputConfig(filename={self.filename}, format={self.format.value}, "
            f"include_source={self.include_source}, include_fixtures={self.include_fixtures}, "
            f"code_context_lines={self.code_context_lines}, enhanced_context={self.enhanced_context})"
        )


# Update the main extractor classes
class FailureExtractor:
    """Enhanced thread-safe singleton to collect test failures with flexible output.
    
    This class implements a singleton pattern to provide centralized collection
    of test failure data across the application. It maintains thread-safe access
    to failure collections and supports configurable memory limits for large
    test suites.
    
    Attributes:
        failures (List[Dict[str, Any]]): Collection of test failure data
        passed (List[Dict[str, Any]]): Collection of passed test data (optional)
        fixture_extractor (FixtureExtractor): Instance for extracting fixture context
    
    Example:
        >>> extractor = FailureExtractor()
        >>> failure_data = {
        ...     'test_name': 'test_example',
        ...     'test_module': 'test_module',
        ...     'exception_type': 'AssertionError',
        ...     'exception_message': 'Test failed',
        ...     'timestamp': '2024-01-01T12:00:00'
        ... }
        >>> extractor.add_failure(failure_data)
        >>> print(len(extractor.failures))
        1
    """

    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                # Double-checked locking pattern
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance.failures = []
                    cls._instance.passed = []
                    cls._instance.fixture_extractor = FixtureExtractor()
                    cls._instance._data_lock = threading.Lock()
                    cls._instance._max_failures = None  # No limit by default
                    cls._instance._max_passed = None  # No limit by default
        return cls._instance

    def add_failure(self, failure_data: Dict[str, Any]):
        """Add a test failure to the collection.

        Stores test failure data in the internal collection with thread-safe
        access. Automatically enforces memory limits if configured.

        Args:
            failure_data: Dictionary containing failure information with keys:
                - 'test_name': Name of the failed test
                - 'test_module': Module containing the test
                - 'test_file': File path of the test
                - 'exception_type': Type of exception raised
                - 'exception_message': Exception message
                - 'timestamp': When the failure occurred
                - Additional context data from fixture extraction

        Example:
            >>> extractor = FailureExtractor()
            >>> failure_data = {
            ...     'test_name': 'test_example',
            ...     'test_module': 'test_module',
            ...     'exception_type': 'AssertionError',
            ...     'exception_message': 'Test failed',
            ...     'timestamp': '2024-01-01T12:00:00'
            ... }
            >>> extractor.add_failure(failure_data)
            >>> print(len(extractor.failures))
            1
        """
        with self._data_lock:
            self.failures.append(failure_data)
            # Enforce memory limit if set
            if (
                self._max_failures is not None
                and len(self.failures) > self._max_failures
            ):
                # Remove oldest entries to stay within limit
                self.failures = self.failures[-self._max_failures :]

    def add_passed(self, test_data: Dict[str, Any]):
        """Add a passed test to the collection.

        Stores passed test data in the internal collection with thread-safe
        access. Used when include_passed=True in configuration. Automatically
        enforces memory limits if configured.

        Args:
            test_data: Dictionary containing test information with keys:
                - 'test_name': Name of the passed test
                - 'test_module': Module containing the test
                - 'test_file': File path of the test
                - 'timestamp': When the test passed
                - Additional context data from fixture extraction

        Example:
            >>> extractor = FailureExtractor()
            >>> test_data = {
            ...     'test_name': 'test_successful',
            ...     'test_module': 'test_module',
            ...     'test_file': '/path/to/test.py',
            ...     'timestamp': '2024-01-01T12:00:00'
            ... }
            >>> extractor.add_passed(test_data)
            >>> print(len(extractor.passed))
            1
        """
        with self._data_lock:
            self.passed.append(test_data)
            # Enforce memory limit if set
            if self._max_passed is not None and len(self.passed) > self._max_passed:
                # Remove oldest entries to stay within limit
                self.passed = self.passed[-self._max_passed :]

    def save_report(self, config: OutputConfig):
        """Save report with specified configuration."""
        data = self._prepare_data(config)

        if not data:
            # No data to report - remove file if it exists and is empty
            if config.filename and Path(config.filename).exists():
                try:
                    if Path(config.filename).stat().st_size == 0:
                        Path(config.filename).unlink()
                except (OSError, FileNotFoundError):
                    pass  # File already gone or permission issue
            return

        formatter = FormatterRegistry.get_formatter(config.format)
        content = formatter.format(data)

        mode = "a" if config.append else "w"
        with open(config.filename, mode) as f:
            if config.append and config.format == OutputFormat.JSON:
                # Special handling for JSON append
                self._append_json(f, data)
            else:
                f.write(content)

    def _prepare_data(self, config: OutputConfig) -> List[Dict[str, Any]]:
        """Prepare data based on configuration."""
        with self._data_lock:
            data = self.failures.copy()

            if config.include_passed:
                for passed in self.passed:
                    passed["status"] = "passed"
                data.extend(self.passed)

            if config.max_failures and len(data) > config.max_failures:
                data = data[: config.max_failures]

            return data

    def _append_json(self, file, new_data):
        """Append to existing JSON file."""
        file.seek(0)
        try:
            existing = json.load(file)
            if isinstance(existing, list):
                existing.extend(new_data)
            else:
                existing = [existing] + new_data
            file.seek(0)
            file.truncate()
            json.dump(existing, file, indent=2, default=str)
        except (json.JSONDecodeError, ValueError, EOFError):
            # json.JSONDecodeError: invalid JSON in file
            # ValueError: JSON decode error in older Python versions
            # EOFError: empty file
            file.seek(0)
            file.truncate()
            json.dump(new_data, file, indent=2, default=str)

    def set_memory_limits(
        self, max_failures: Optional[int] = None, max_passed: Optional[int] = None
    ):
        """Set memory limits for stored test data.

        Args:
            max_failures: Maximum number of failures to keep (None for unlimited)
            max_passed: Maximum number of passed tests to keep (None for unlimited)
        """
        with self._data_lock:
            if max_failures is not None and max_failures <= 0:
                raise ValueError("max_failures must be positive")
            if max_passed is not None and max_passed <= 0:
                raise ValueError("max_passed must be positive")

            self._max_failures = max_failures
            self._max_passed = max_passed

            # Trim existing data if needed
            if (
                self._max_failures is not None
                and len(self.failures) > self._max_failures
            ):
                self.failures = self.failures[-self._max_failures :]
            if self._max_passed is not None and len(self.passed) > self._max_passed:
                self.passed = self.passed[-self._max_passed :]

    def get_memory_limits(self) -> Dict[str, Optional[int]]:
        """Get current memory limits."""
        return {"max_failures": self._max_failures, "max_passed": self._max_passed}

    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about stored data."""
        with self._data_lock:
            return {
                "failures_count": len(self.failures),
                "passed_count": len(self.passed),
                "total_count": len(self.failures) + len(self.passed),
                "max_failures_limit": self._max_failures,
                "max_passed_limit": self._max_passed,
                "failures_at_limit": self._max_failures is not None
                and len(self.failures) == self._max_failures,
                "passed_at_limit": self._max_passed is not None
                and len(self.passed) == self._max_passed,
            }

    def reset(self):
        """Reset all stored data and memory limits to defaults."""
        with self._data_lock:
            self.failures = []
            self.passed = []
            self._max_failures = None
            self._max_passed = None

    def clear(self):
        """Clear stored data but keep memory limits."""
        with self._data_lock:
            self.failures = []
            self.passed = []


def extract_on_failure(
    output: Union[str, Path, OutputFormat, OutputConfig, None] = None,
    format: Union[str, OutputFormat, None] = None,
    include_locals: bool = False,
    include_fixtures: bool = True,
    max_depth: int = 10,
    skip_stdlib: bool = True,
    extract_classes: bool = True,
    append: bool = False,
    custom_formatter: Optional[OutputFormatter] = None,
    code_context_lines: int = 5,
    enhanced_context: bool = True,
    include_line_numbers: bool = True,
    max_code_lines: int = 100,
):
    """
    Enhanced decorator with flexible output options.

    Args:
        output: Output configuration - can be:
            - str/Path: File path (format detected from extension)
            - OutputFormat: Format type (uses default filename)
            - OutputConfig: Full configuration object
            - None: Use global collection
        format: Override format detection (when output is a path)
        include_locals: Include local variables
        include_fixtures: Extract fixture definitions
        max_depth: Maximum traceback depth
        skip_stdlib: Skip standard library modules
        extract_classes: Extract class definitions
        append: Append to existing file instead of overwriting
        custom_formatter: Custom formatter instance
        code_context_lines: Number of context lines around failure points
        enhanced_context: Whether to use enhanced CodeContextExtractor
        include_line_numbers: Whether to include line numbers in source code
        max_code_lines: Maximum lines of code per failure frame

    Examples:
        @extract_on_failure("failures.json")
        @extract_on_failure("report.md")
        @extract_on_failure(output="results.xml", format="xml")
        @extract_on_failure(OutputFormat.YAML)
        @extract_on_failure(output=OutputConfig("report.xml", append=True))
    """

    def decorator(test_func: Callable) -> Callable:
        # Handle configuration
        if isinstance(output, OutputConfig):
            config = output
        else:
            config = OutputConfig(output, format, append)

        # Register custom formatter if provided
        if custom_formatter:
            FormatterRegistry.register_formatter(OutputFormat.CUSTOM, custom_formatter)
            if config.format is None:
                config.format = OutputFormat.CUSTOM

        @functools.wraps(test_func)
        def wrapper(*args, **kwargs):
            try:
                # Get current frame for fixtures
                frame = inspect.currentframe()
                frame_locals = frame.f_locals if frame else {}

                result = test_func(*args, **kwargs)

                # Optionally track passed tests
                if config.include_passed:
                    passed_data = {
                        "timestamp": datetime.now().isoformat(),
                        "test_name": test_func.__name__,
                        "test_module": test_func.__module__,
                        "status": "passed",
                    }
                    FailureExtractor().add_passed(passed_data)

                return result

            except Exception as e:
                # Extract failure information
                failure_data = extract_failure_info(
                    test_func,
                    e,
                    args,
                    kwargs,
                    frame_locals=frame_locals,
                    include_locals=include_locals,
                    include_fixtures=include_fixtures,
                    max_depth=max_depth,
                    skip_stdlib=skip_stdlib,
                    extract_classes=extract_classes,
                    code_context_lines=code_context_lines,
                    enhanced_context=enhanced_context,
                    include_line_numbers=include_line_numbers,
                    max_code_lines=max_code_lines,
                )

                # Save to file if output specified
                if config.filename:
                    save_with_config(failure_data, config)
                else:
                    # Use global collection
                    FailureExtractor().add_failure(failure_data)

                # Re-raise for pytest
                raise

        wrapper._extract_on_failure = True
        wrapper._output_config = config
        return wrapper

    # Handle both @extract_on_failure and @extract_on_failure()
    if callable(output):
        func = output
        output = None
        return decorator(func)

    return decorator


def save_with_config(data: Dict[str, Any], config: OutputConfig):
    """Save single failure with configuration."""
    formatter = FormatterRegistry.get_formatter(config.format)

    if config.append and config.filename and Path(config.filename).exists():
        # Read existing data
        with open(config.filename, "r") as f:
            if config.format == OutputFormat.JSON:
                try:
                    existing = json.load(f)
                    if isinstance(existing, list):
                        existing.append(data)
                    else:
                        existing = [existing, data]
                    data_to_save = existing
                except (json.JSONDecodeError, ValueError, EOFError):
                    # json.JSONDecodeError: invalid JSON in file
                    # ValueError: JSON decode error in older Python versions
                    # EOFError: empty file
                    data_to_save = [data]
            else:
                # For non-JSON formats, just append
                existing_content = f.read()

        if config.format == OutputFormat.JSON and "data_to_save" in locals():
            content = formatter.format(data_to_save)
        else:
            content = formatter.format([data] if not isinstance(data, list) else data)

        with open(config.filename, "w") as f:
            if config.format != OutputFormat.JSON and config.append:
                f.write(existing_content)
                f.write("\n")
            f.write(content)
    else:
        # New file
        content = formatter.format([data])
        with open(config.filename, "w") as f:
            f.write(content)


# =============================================================================
# Phase 3: Intelligent Failure Analysis
# =============================================================================

@dataclass
class FailurePattern:
    """Represents a detected failure pattern."""
    pattern_id: str
    signature: str
    frequency: int
    confidence: float
    examples: List[str] = field(default_factory=list)
    first_seen: datetime = field(default_factory=datetime.now)
    last_seen: datetime = field(default_factory=datetime.now)
    pattern_type: str = "error_message"  # error_message, stack_trace, location
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'pattern_id': self.pattern_id,
            'signature': self.signature,
            'frequency': self.frequency,
            'confidence': self.confidence,
            'examples': self.examples[:5],  # Limit examples for size
            'first_seen': self.first_seen.isoformat(),
            'last_seen': self.last_seen.isoformat(),
            'pattern_type': self.pattern_type
        }

@dataclass 
class CauseCandidate:
    """Represents a potential root cause for a failure."""
    cause_type: str  # dependency, change, pattern
    description: str
    confidence: float
    evidence: List[str] = field(default_factory=list)
    
@dataclass
class RootCauseAnalysis:
    """Analysis of potential root causes for a failure."""
    failure_id: str
    potential_causes: List[CauseCandidate] = field(default_factory=list)
    confidence_score: float = 0.0
    dependency_path: List[str] = field(default_factory=list)
    analysis_timestamp: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'failure_id': self.failure_id,
            'potential_causes': [
                {
                    'cause_type': cause.cause_type,
                    'description': cause.description,
                    'confidence': cause.confidence,
                    'evidence': cause.evidence
                }
                for cause in self.potential_causes
            ],
            'confidence_score': self.confidence_score,
            'dependency_path': self.dependency_path,
            'analysis_timestamp': self.analysis_timestamp.isoformat()
        }

@dataclass
class FailureImpact:
    """Analysis of failure impact and blast radius."""
    failure_id: str
    priority_score: float
    blast_radius: int  # Number of potentially affected components
    affected_components: List[str] = field(default_factory=list)
    criticality: str = "medium"  # low, medium, high, critical
    urgency: str = "medium"  # low, medium, high
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'failure_id': self.failure_id,
            'priority_score': self.priority_score,
            'blast_radius': self.blast_radius,
            'affected_components': self.affected_components,
            'criticality': self.criticality,
            'urgency': self.urgency
        }

@dataclass
class AnalysisInsight:
    """Actionable insight generated from failure analysis."""
    insight_id: str
    insight_type: str  # pattern, trend, fix_suggestion
    title: str
    description: str
    confidence: float
    priority: int  # 1-5, higher is more important
    related_failures: List[str] = field(default_factory=list)
    recommended_actions: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'insight_id': self.insight_id,
            'insight_type': self.insight_type,
            'title': self.title,
            'description': self.description,
            'confidence': self.confidence,
            'priority': self.priority,
            'related_failures': self.related_failures,
            'recommended_actions': self.recommended_actions,
            'created_at': self.created_at.isoformat()
        }


class PatternDetector:
    """Detects patterns in test failures."""
    
    def __init__(self, similarity_threshold: float = 0.8):
        self.similarity_threshold = similarity_threshold
        self.patterns: Dict[str, FailurePattern] = {}
        
    def _compute_signature(self, text: str, pattern_type: str = "error_message") -> str:
        """Compute a normalized signature for pattern matching."""
        if pattern_type == "error_message":
            # Normalize error messages by removing specific values
            normalized = re.sub(r'\b\d+\b', '<NUM>', text)  # Replace numbers
            normalized = re.sub(r'\'[^\']*\'', '<STR>', normalized)  # Replace quoted strings
            normalized = re.sub(r'"[^"]*"', '<STR>', normalized)  # Replace double quoted strings
            normalized = re.sub(r'\b[a-f0-9]{8,}\b', '<HEX>', normalized, flags=re.IGNORECASE)  # Replace hex
            normalized = re.sub(r'\s+', ' ', normalized)  # Normalize whitespace
            return normalized.strip().lower()
        
        elif pattern_type == "stack_trace":
            # Extract just the function call chain, ignore line numbers and file paths
            lines = text.split('\n')
            functions = []
            for line in lines:
                line = line.strip()
                if 'in ' in line and '(' in line:
                    # Extract function name from traceback line
                    match = re.search(r'in (\w+)', line)
                    if match:
                        functions.append(match.group(1))
            return ' -> '.join(functions)
        
        elif pattern_type == "location":
            # Normalize file paths and focus on relative structure
            normalized = re.sub(r'^.*?(?=tests/|src/)', '', text)  # Remove absolute path prefix
            normalized = re.sub(r':\d+', ':LINE', normalized)  # Replace line numbers
            return normalized
        
        return text.lower().strip()
    
    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """Calculate similarity between two text strings."""
        return difflib.SequenceMatcher(None, text1, text2).ratio()
    
    def detect_patterns(self, failures: List[Dict[str, Any]]) -> List[FailurePattern]:
        """Detect patterns in a list of failures."""
        # Group failures by pattern type
        error_groups = defaultdict(list)
        stack_groups = defaultdict(list)
        location_groups = defaultdict(list)
        
        for failure in failures:
            # Error message patterns
            if 'error_message' in failure:
                signature = self._compute_signature(failure['error_message'], "error_message")
                error_groups[signature].append(failure)
            
            # Stack trace patterns
            if 'traceback' in failure:
                signature = self._compute_signature(failure['traceback'], "stack_trace")
                stack_groups[signature].append(failure)
            
            # Location patterns
            if 'filename' in failure and 'line_number' in failure:
                location = f"{failure['filename']}:{failure['line_number']}"
                signature = self._compute_signature(location, "location")
                location_groups[signature].append(failure)
        
        patterns = []
        
        # Create patterns from groups with multiple failures
        for pattern_type, groups in [
            ("error_message", error_groups),
            ("stack_trace", stack_groups), 
            ("location", location_groups)
        ]:
            for signature, group_failures in groups.items():
                if len(group_failures) >= 2:  # Pattern needs at least 2 occurrences
                    pattern_id = hashlib.md5(f"{pattern_type}:{signature}".encode()).hexdigest()[:8]
                    
                    # Calculate confidence based on frequency and consistency
                    confidence = min(0.95, 0.5 + (len(group_failures) * 0.1))
                    
                    # Extract examples
                    examples = []
                    for failure in group_failures[:3]:  # Take first 3 as examples
                        if pattern_type == "error_message" and 'error_message' in failure:
                            examples.append(failure['error_message'])
                        elif pattern_type == "stack_trace" and 'traceback' in failure:
                            examples.append(failure['traceback'][:200] + "..." if len(failure['traceback']) > 200 else failure['traceback'])
                        elif pattern_type == "location":
                            examples.append(f"{failure.get('filename', 'unknown')}:{failure.get('line_number', 0)}")
                    
                    pattern = FailurePattern(
                        pattern_id=pattern_id,
                        signature=signature,
                        frequency=len(group_failures),
                        confidence=confidence,
                        examples=examples,
                        pattern_type=pattern_type,
                        first_seen=datetime.now(),
                        last_seen=datetime.now()
                    )
                    
                    patterns.append(pattern)
                    self.patterns[pattern_id] = pattern
        
        # Sort by frequency and confidence
        patterns.sort(key=lambda p: (p.frequency, p.confidence), reverse=True)
        return patterns
    
    def classify_failure(self, failure: Dict[str, Any]) -> str:
        """Classify a failure into categories."""
        error_msg = failure.get('error_message', '').lower()
        traceback = failure.get('traceback', '').lower()
        
        # Assertion failures
        if 'assertionerror' in error_msg or 'assertion' in error_msg:
            return 'assertion'
        
        # Timeout failures
        if 'timeout' in error_msg or 'timeout' in traceback:
            return 'timeout'
        
        # Import/Module errors
        if 'modulenotfounderror' in error_msg or 'importerror' in error_msg:
            return 'import'
        
        # Setup/Teardown errors
        if 'setup' in traceback or 'teardown' in traceback or 'fixture' in traceback:
            return 'setup'
        
        # Permission/Access errors
        if 'permission' in error_msg or 'access' in error_msg:
            return 'permission'
        
        # Network/Connection errors
        if 'connection' in error_msg or 'network' in error_msg or 'socket' in error_msg:
            return 'network'
        
        # Type errors
        if 'typeerror' in error_msg:
            return 'type'
        
        # Value errors
        if 'valueerror' in error_msg:
            return 'value'
        
        # Default to generic exception
        return 'exception'


class RootCauseAnalyzer:
    """Analyzes root causes of failures using dependency graphs."""
    
    def __init__(self, context_extractor: Optional[CodeContextExtractor] = None):
        self.context_extractor = context_extractor or CodeContextExtractor()
        
    def analyze_root_cause(self, failure: Dict[str, Any], failures_context: List[Dict[str, Any]] = None) -> RootCauseAnalysis:
        """Analyze potential root causes for a failure."""
        failure_id = failure.get('test_name', f"failure_{int(time.time())}")
        
        # Get dependency information from Phase 2
        potential_causes = []
        dependency_path = []
        
        # Extract frame information for dependency analysis
        if 'frames' in failure and failure['frames']:
            frame_info = failure['frames'][0]  # Most recent frame
            filename = frame_info.get('filename', '')
            
            # Analyze dependencies using Phase 2 capabilities
            if filename:
                dependencies = self.context_extractor.analyze_dependencies(filename)
                if dependencies:
                    dependency_path = list(dependencies.get('imports', []))
                    
                    # Dependency-based cause analysis
                    for dep in dependencies.get('imports', [])[:5]:  # Limit to top 5
                        potential_causes.append(CauseCandidate(
                            cause_type="dependency",
                            description=f"Failure may be related to dependency: {dep}",
                            confidence=0.6,
                            evidence=[f"Import found: {dep}"]
                        ))
                
                # Check execution trace for clues
                try:
                    execution_context = self.context_extractor.combine_coverage_with_dependencies(frame_info)
                    if execution_context.get('dependency_analysis', {}).get('dependencies'):
                        trace_deps = execution_context['dependency_analysis']['dependencies']
                        for dep in list(trace_deps)[:3]:
                            potential_causes.append(CauseCandidate(
                                cause_type="execution_path",
                                description=f"Execution trace shows dependency on: {dep}",
                                confidence=0.7,
                                evidence=[f"Execution dependency: {dep}"]
                            ))
                except Exception:
                    # Graceful fallback if execution context fails
                    pass
        
        # Pattern-based cause analysis
        error_message = failure.get('error_message', '')
        if error_message:
            # Common error pattern analysis
            if 'modulenotfounderror' in error_message.lower():
                module_match = re.search(r"No module named '([^']+)'", error_message)
                if module_match:
                    potential_causes.append(CauseCandidate(
                        cause_type="missing_dependency",
                        description=f"Missing module: {module_match.group(1)}",
                        confidence=0.9,
                        evidence=[error_message]
                    ))
            
            elif 'assertionerror' in error_message.lower():
                potential_causes.append(CauseCandidate(
                    cause_type="assertion_failure",
                    description="Test assertion failed - likely logic error or changed behavior",
                    confidence=0.8,
                    evidence=[error_message]
                ))
            
            elif 'attributeerror' in error_message.lower():
                attr_match = re.search(r"'([^']+)' object has no attribute '([^']+)'", error_message)
                if attr_match:
                    potential_causes.append(CauseCandidate(
                        cause_type="api_change",
                        description=f"Possible API change: {attr_match.group(1)}.{attr_match.group(2)} no longer exists",
                        confidence=0.75,
                        evidence=[error_message]
                    ))
        
        # Cross-failure correlation analysis
        if failures_context:
            similar_failures = self._find_similar_failures(failure, failures_context)
            if len(similar_failures) >= 2:
                potential_causes.append(CauseCandidate(
                    cause_type="systemic_issue",
                    description=f"Systemic issue detected - {len(similar_failures)} similar failures found",
                    confidence=0.8,
                    evidence=[f"Similar failure in {f.get('test_name', 'unknown')}" for f in similar_failures[:3]]
                ))
        
        # Calculate overall confidence
        confidence_score = 0.0
        if potential_causes:
            confidence_score = sum(cause.confidence for cause in potential_causes) / len(potential_causes)
        
        # Sort causes by confidence
        potential_causes.sort(key=lambda c: c.confidence, reverse=True)
        
        return RootCauseAnalysis(
            failure_id=failure_id,
            potential_causes=potential_causes,
            confidence_score=confidence_score,
            dependency_path=dependency_path,
            analysis_timestamp=datetime.now()
        )
    
    def _find_similar_failures(self, target_failure: Dict[str, Any], all_failures: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Find failures similar to the target failure."""
        similar = []
        target_error = target_failure.get('error_message', '').lower()
        target_type = target_failure.get('error_type', '').lower()
        
        for failure in all_failures:
            if failure == target_failure:
                continue
                
            similarity_score = 0.0
            
            # Error message similarity
            other_error = failure.get('error_message', '').lower()
            if target_error and other_error:
                error_similarity = difflib.SequenceMatcher(None, target_error, other_error).ratio()
                similarity_score += error_similarity * 0.6
            
            # Error type similarity
            other_type = failure.get('error_type', '').lower()
            if target_type and other_type and target_type == other_type:
                similarity_score += 0.4
            
            # Location similarity
            target_file = target_failure.get('filename', '')
            other_file = failure.get('filename', '')
            if target_file and other_file and target_file == other_file:
                similarity_score += 0.3
            
            if similarity_score >= 0.7:  # Threshold for similarity
                similar.append(failure)
        
        return similar


class ImpactAnalyzer:
    """Analyzes failure impact and calculates priority scores."""
    
    def __init__(self, context_extractor: Optional[CodeContextExtractor] = None):
        self.context_extractor = context_extractor or CodeContextExtractor()
        
    def analyze_impact(self, failure: Dict[str, Any], all_failures: List[Dict[str, Any]] = None) -> FailureImpact:
        """Analyze the impact and priority of a failure."""
        failure_id = failure.get('test_name', f"failure_{int(time.time())}")
        
        # Calculate blast radius using dependency information
        blast_radius = self._calculate_blast_radius(failure)
        
        # Determine criticality based on failure characteristics
        criticality = self._assess_criticality(failure)
        
        # Determine urgency based on failure type and frequency
        urgency = self._assess_urgency(failure, all_failures or [])
        
        # Calculate affected components
        affected_components = self._identify_affected_components(failure)
        
        # Calculate overall priority score (0-10 scale)
        priority_score = self._calculate_priority_score(criticality, urgency, blast_radius)
        
        return FailureImpact(
            failure_id=failure_id,
            priority_score=priority_score,
            blast_radius=blast_radius,
            affected_components=affected_components,
            criticality=criticality,
            urgency=urgency
        )
    
    def _calculate_blast_radius(self, failure: Dict[str, Any]) -> int:
        """Calculate the potential blast radius of a failure."""
        blast_radius = 1  # Base impact
        
        # Check if failure involves dependencies
        if 'frames' in failure and failure['frames']:
            frame_info = failure['frames'][0]
            filename = frame_info.get('filename', '')
            
            if filename:
                try:
                    dependencies = self.context_extractor.analyze_dependencies(filename)
                    if dependencies and 'imports' in dependencies:
                        # More imports = potentially larger blast radius
                        blast_radius += len(dependencies['imports'])
                    
                    # Check if this is a utility/core file (likely higher impact)
                    if any(pattern in filename.lower() for pattern in ['util', 'core', 'base', 'common', '__init__']):
                        blast_radius *= 2
                except Exception:
                    # Graceful fallback if dependency analysis fails
                    pass
        
        # Check error type impact
        error_message = failure.get('error_message', '').lower()
        if any(pattern in error_message for pattern in ['modulenotfounderror', 'importerror']):
            blast_radius *= 1.5  # Import errors can cascade
        
        return min(int(blast_radius), 50)  # Cap at reasonable maximum
    
    def _assess_criticality(self, failure: Dict[str, Any]) -> str:
        """Assess the criticality level of a failure."""
        error_message = failure.get('error_message', '').lower()
        filename = failure.get('filename', '').lower()
        
        # Critical: Core system failures
        if any(pattern in error_message for pattern in ['modulenotfounderror', 'importerror', 'syntaxerror']):
            return 'critical'
        
        # Critical: Core/infrastructure files
        if any(pattern in filename for pattern in ['__init__', 'setup', 'config', 'core']):
            return 'critical'
        
        # High: Security or data integrity issues
        if any(pattern in error_message for pattern in ['permission', 'access', 'security', 'integrity']):
            return 'high'
        
        # High: Performance-critical failures
        if any(pattern in error_message for pattern in ['timeout', 'memory', 'performance']):
            return 'high'
        
        # Medium: Logic errors
        if any(pattern in error_message for pattern in ['assertionerror', 'valueerror', 'typeerror']):
            return 'medium'
        
        # Low: Everything else
        return 'low'
    
    def _assess_urgency(self, failure: Dict[str, Any], all_failures: List[Dict[str, Any]]) -> str:
        """Assess the urgency of fixing a failure."""
        error_message = failure.get('error_message', '').lower()
        
        # High urgency: Blocking failures
        if any(pattern in error_message for pattern in ['modulenotfounderror', 'importerror', 'syntaxerror']):
            return 'high'
        
        # Check frequency among all failures
        if all_failures:
            similar_count = sum(1 for f in all_failures 
                              if f.get('error_message', '').lower() == error_message)
            if similar_count >= 3:
                return 'high'  # Frequent occurrence = high urgency
            elif similar_count >= 2:
                return 'medium'
        
        # Medium: Test logic issues
        if any(pattern in error_message for pattern in ['assertionerror']):
            return 'medium'
        
        return 'low'
    
    def _identify_affected_components(self, failure: Dict[str, Any]) -> List[str]:
        """Identify components potentially affected by the failure."""
        components = []
        
        filename = failure.get('filename', '')
        if filename:
            # Extract component from file path
            parts = filename.split('/')
            if len(parts) > 1:
                # Get the module/package name
                if 'tests' in parts:
                    # For test files, infer the component being tested
                    test_idx = parts.index('tests')
                    if test_idx + 1 < len(parts):
                        components.append(parts[test_idx + 1])
                else:
                    # For source files
                    if 'src' in parts:
                        src_idx = parts.index('src')
                        if src_idx + 1 < len(parts):
                            components.append(parts[src_idx + 1])
                    else:
                        components.append(parts[-2] if len(parts) > 1 else parts[0])
        
        # Add error-type based components
        error_message = failure.get('error_message', '').lower()
        if 'database' in error_message or 'sql' in error_message:
            components.append('database')
        if 'network' in error_message or 'connection' in error_message:
            components.append('network')
        if 'auth' in error_message or 'permission' in error_message:
            components.append('authentication')
        
        return list(set(components))  # Remove duplicates
    
    def _calculate_priority_score(self, criticality: str, urgency: str, blast_radius: int) -> float:
        """Calculate overall priority score (0-10 scale)."""
        # Base scores
        criticality_scores = {'low': 2, 'medium': 5, 'high': 7, 'critical': 10}
        urgency_scores = {'low': 1, 'medium': 3, 'high': 5}
        
        criticality_score = criticality_scores.get(criticality, 2)
        urgency_score = urgency_scores.get(urgency, 1)
        
        # Normalize blast radius (assume max 50)
        blast_score = min(blast_radius / 10.0, 3.0)
        
        # Weighted combination
        priority = (criticality_score * 0.5) + (urgency_score * 0.3) + (blast_score * 0.2)
        
        return round(min(priority, 10.0), 2)


class TrendAnalyzer:
    """Analyzes failure trends over time."""
    
    def __init__(self, storage_path: Optional[str] = None):
        self.storage_path = storage_path or "failextract_analysis.db"
        
    def analyze_trends(self, days_back: int = 30) -> Dict[str, Any]:
        """Analyze failure trends over the specified time period."""
        try:
            conn = sqlite3.connect(self.storage_path)
            cursor = conn.cursor()
            
            # Get failure history for the time period
            cutoff_date = (datetime.now() - timedelta(days=days_back)).isoformat()
            
            cursor.execute('''
                SELECT error_type, timestamp, COUNT(*) as count
                FROM failure_history 
                WHERE timestamp > ?
                GROUP BY error_type, DATE(timestamp)
                ORDER BY timestamp
            ''', (cutoff_date,))
            
            trend_data = cursor.fetchall()
            conn.close()
            
            if not trend_data:
                return {
                    'trend_analysis': 'insufficient_data',
                    'message': 'Not enough historical data for trend analysis',
                    'days_analyzed': 0,
                    'total_failures': 0
                }
            
            # Process trend data
            daily_counts = defaultdict(lambda: defaultdict(int))
            error_type_totals = defaultdict(int)
            
            for error_type, timestamp, count in trend_data:
                date = timestamp.split('T')[0]  # Extract date part
                daily_counts[date][error_type] += count
                error_type_totals[error_type] += count
            
            # Detect trends
            trends = self._detect_trends(daily_counts, error_type_totals)
            
            # Generate trend insights
            trend_insights = self._generate_trend_insights(trends, days_back)
            
            return {
                'trend_analysis': 'completed',
                'days_analyzed': days_back,
                'total_failures': sum(error_type_totals.values()),
                'error_type_distribution': dict(error_type_totals),
                'trends': trends,
                'insights': trend_insights,
                'analysis_timestamp': datetime.now().isoformat()
            }
            
        except Exception:
            return {
                'trend_analysis': 'failed',
                'message': 'Error analyzing trends - storage may not be available',
                'days_analyzed': 0,
                'total_failures': 0
            }
    
    def _detect_trends(self, daily_counts: Dict[str, Dict[str, int]], 
                      error_type_totals: Dict[str, int]) -> Dict[str, Any]:
        """Detect trends in the failure data."""
        trends = {
            'increasing': [],
            'decreasing': [],
            'stable': [],
            'emerging': [],
            'resolved': []
        }
        
        # Convert daily counts to time series
        dates = sorted(daily_counts.keys())
        if len(dates) < 3:
            return trends
        
        # Analyze each error type
        for error_type, total_count in error_type_totals.items():
            if total_count < 3:  # Skip error types with very few occurrences
                continue
                
            # Get daily counts for this error type
            daily_series = [daily_counts[date].get(error_type, 0) for date in dates]
            
            # Simple trend detection using moving averages
            first_half_avg = sum(daily_series[:len(daily_series)//2]) / (len(daily_series)//2)
            second_half_avg = sum(daily_series[len(daily_series)//2:]) / (len(daily_series) - len(daily_series)//2)
            
            change_ratio = (second_half_avg - first_half_avg) / (first_half_avg + 0.1)  # Avoid division by zero
            
            # Classify trend
            if change_ratio > 0.3:
                trends['increasing'].append({
                    'error_type': error_type,
                    'change_ratio': round(change_ratio, 2),
                    'recent_avg': round(second_half_avg, 2),
                    'total_count': total_count
                })
            elif change_ratio < -0.3:
                trends['decreasing'].append({
                    'error_type': error_type,
                    'change_ratio': round(change_ratio, 2),
                    'recent_avg': round(second_half_avg, 2),
                    'total_count': total_count
                })
            else:
                trends['stable'].append({
                    'error_type': error_type,
                    'change_ratio': round(change_ratio, 2),
                    'recent_avg': round(second_half_avg, 2),
                    'total_count': total_count
                })
            
            # Check for emerging (new in recent period) or resolved (absent in recent period)
            recent_count = sum(daily_series[len(daily_series)//2:])
            early_count = sum(daily_series[:len(daily_series)//2])
            
            if early_count == 0 and recent_count > 0:
                trends['emerging'].append({
                    'error_type': error_type,
                    'recent_count': recent_count,
                    'total_count': total_count
                })
            elif early_count > 0 and recent_count == 0:
                trends['resolved'].append({
                    'error_type': error_type,
                    'early_count': early_count,
                    'total_count': total_count
                })
        
        # Sort by significance
        for trend_type in trends:
            if trend_type in ['increasing', 'decreasing', 'stable']:
                trends[trend_type].sort(key=lambda x: abs(x['change_ratio']), reverse=True)
            else:
                trends[trend_type].sort(key=lambda x: x['total_count'], reverse=True)
        
        return trends
    
    def _generate_trend_insights(self, trends: Dict[str, Any], days_back: int) -> List[Dict[str, Any]]:
        """Generate insights from trend analysis."""
        insights = []
        
        # Insight: Increasing trends
        if trends['increasing']:
            worst_trend = trends['increasing'][0]
            insights.append({
                'type': 'increasing_trend',
                'title': f"Worsening Trend Detected: {worst_trend['error_type']}",
                'description': f"Failure rate increased by {abs(worst_trend['change_ratio']*100):.1f}% over {days_back} days",
                'severity': 'high' if worst_trend['change_ratio'] > 0.5 else 'medium',
                'recommendations': [
                    f"Investigate {worst_trend['error_type']} failures immediately",
                    "Check for recent changes that might be causing the increase",
                    "Consider reverting recent changes if correlation found"
                ]
            })
        
        # Insight: Emerging issues
        if trends['emerging']:
            emerging = trends['emerging'][0]
            insights.append({
                'type': 'emerging_issue',
                'title': f"New Issue Detected: {emerging['error_type']}",
                'description': f"New failure type appeared recently: {emerging['recent_count']} occurrences",
                'severity': 'medium',
                'recommendations': [
                    f"Investigate new {emerging['error_type']} failures",
                    "Check if related to recent deployments or changes",
                    "Monitor closely to prevent escalation"
                ]
            })
        
        # Insight: Resolved issues
        if trends['resolved']:
            resolved = trends['resolved'][0]
            insights.append({
                'type': 'resolved_issue',
                'title': f"Issue Appears Resolved: {resolved['error_type']}",
                'description': f"Failure type no longer occurring (was {resolved['early_count']} occurrences)",
                'severity': 'positive',
                'recommendations': [
                    "Document what resolved this issue for future reference",
                    "Verify the fix is permanent, not just temporary",
                    "Apply similar solutions to related issues if applicable"
                ]
            })
        
        # Insight: Overall trend assessment
        total_increasing = len(trends['increasing'])
        total_decreasing = len(trends['decreasing'])
        total_stable = len(trends['stable'])
        
        if total_increasing > total_decreasing + 1:
            insights.append({
                'type': 'overall_trend',
                'title': "Overall Quality Degradation",
                'description': f"More failure types increasing ({total_increasing}) than decreasing ({total_decreasing})",
                'severity': 'high',
                'recommendations': [
                    "Review recent changes and deployment processes",
                    "Implement additional quality gates",
                    "Consider increasing test coverage"
                ]
            })
        elif total_decreasing > total_increasing + 1:
            insights.append({
                'type': 'overall_trend',
                'title': "Overall Quality Improvement",
                'description': f"More failure types decreasing ({total_decreasing}) than increasing ({total_increasing})",
                'severity': 'positive',
                'recommendations': [
                    "Continue current quality practices",
                    "Document successful improvement strategies",
                    "Share learnings with team"
                ]
            })
        
        return insights


class FailureAnalyzer:
    """Main orchestrator for intelligent failure analysis."""
    
    def __init__(self, storage_path: Optional[str] = None):
        self.pattern_detector = PatternDetector()
        self.root_cause_analyzer = RootCauseAnalyzer()
        self.impact_analyzer = ImpactAnalyzer()
        self.trend_analyzer = TrendAnalyzer(storage_path)
        self.storage_path = storage_path or "failextract_analysis.db"
        self._ensure_storage()
        
    def _ensure_storage(self):
        """Ensure analysis storage is initialized."""
        try:
            conn = sqlite3.connect(self.storage_path)
            cursor = conn.cursor()
            
            # Create tables for storing analysis data
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS failure_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    test_name TEXT,
                    error_type TEXT,
                    error_message TEXT,
                    stack_trace_hash TEXT,
                    filename TEXT,
                    line_number INTEGER,
                    timestamp TEXT,
                    metadata TEXT
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS patterns (
                    pattern_id TEXT PRIMARY KEY,
                    signature TEXT,
                    frequency INTEGER,
                    confidence REAL,
                    pattern_type TEXT,
                    first_seen TEXT,
                    last_seen TEXT,
                    examples TEXT
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS insights (
                    insight_id TEXT PRIMARY KEY,
                    insight_type TEXT,
                    title TEXT,
                    description TEXT,
                    confidence REAL,
                    priority INTEGER,
                    related_failures TEXT,
                    recommended_actions TEXT,
                    created_at TEXT
                )
            ''')
            
            conn.commit()
            conn.close()
        except Exception:
            # Fallback to in-memory storage if file system issues
            pass
    
    def analyze_failures(self, failures: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Perform comprehensive analysis on a list of failures."""
        if not failures:
            return {
                'patterns': [],
                'root_causes': [],
                'impacts': [],
                'insights': [],
                'summary': {
                    'total_failures': 0,
                    'patterns_detected': 0,
                    'insights_generated': 0
                }
            }
        
        # Detect patterns
        patterns = self.pattern_detector.detect_patterns(failures)
        
        # Analyze root causes and impacts for each failure
        root_causes = []
        impacts = []
        
        for failure in failures:
            # Root cause analysis
            root_cause = self.root_cause_analyzer.analyze_root_cause(failure, failures)
            root_causes.append(root_cause.to_dict())
            
            # Impact analysis 
            impact = self.impact_analyzer.analyze_impact(failure, failures)
            impacts.append(impact.to_dict())
        
        # Store failure history
        self._store_failure_history(failures)
        
        # Generate enhanced insights using all analysis data
        insights = self._generate_enhanced_insights(failures, patterns, root_causes, impacts)
        
        # Update pattern storage
        self._store_patterns(patterns)
        
        # Calculate priority-sorted failures
        priority_sorted = sorted(impacts, key=lambda x: x['priority_score'], reverse=True)
        
        return {
            'patterns': [pattern.to_dict() for pattern in patterns],
            'root_causes': root_causes,
            'impacts': impacts,
            'insights': [insight.to_dict() for insight in insights],
            'priority_ranking': priority_sorted[:10],  # Top 10 priority failures
            'summary': {
                'total_failures': len(failures),
                'patterns_detected': len(patterns),
                'insights_generated': len(insights),
                'most_common_type': self._get_most_common_failure_type(failures),
                'highest_priority_failure': priority_sorted[0]['failure_id'] if priority_sorted else None,
                'average_priority_score': sum(i['priority_score'] for i in impacts) / len(impacts) if impacts else 0,
                'critical_failures': len([i for i in impacts if i['criticality'] == 'critical']),
                'analysis_timestamp': datetime.now().isoformat()
            }
        }
    
    def _store_failure_history(self, failures: List[Dict[str, Any]]):
        """Store failure history for trend analysis."""
        try:
            conn = sqlite3.connect(self.storage_path)
            cursor = conn.cursor()
            
            for failure in failures:
                stack_trace_hash = hashlib.md5(
                    failure.get('traceback', '').encode()
                ).hexdigest()
                
                cursor.execute('''
                    INSERT INTO failure_history 
                    (test_name, error_type, error_message, stack_trace_hash, 
                     filename, line_number, timestamp, metadata)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    failure.get('test_name', ''),
                    self.pattern_detector.classify_failure(failure),
                    failure.get('error_message', '')[:500],  # Limit length
                    stack_trace_hash,
                    failure.get('filename', ''),
                    failure.get('line_number', 0),
                    datetime.now().isoformat(),
                    json.dumps({k: v for k, v in failure.items() 
                               if k not in ['traceback', 'error_message']})[:1000]
                ))
            
            conn.commit()
            conn.close()
        except Exception:
            # Fail silently if storage issues
            pass
    
    def _store_patterns(self, patterns: List[FailurePattern]):
        """Store detected patterns."""
        try:
            conn = sqlite3.connect(self.storage_path)
            cursor = conn.cursor()
            
            for pattern in patterns:
                cursor.execute('''
                    INSERT OR REPLACE INTO patterns 
                    (pattern_id, signature, frequency, confidence, pattern_type,
                     first_seen, last_seen, examples)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    pattern.pattern_id,
                    pattern.signature,
                    pattern.frequency,
                    pattern.confidence,
                    pattern.pattern_type,
                    pattern.first_seen.isoformat(),
                    pattern.last_seen.isoformat(),
                    json.dumps(pattern.examples)
                ))
            
            conn.commit()
            conn.close()
        except Exception:
            pass
    
    def _generate_basic_insights(self, failures: List[Dict[str, Any]], 
                                patterns: List[FailurePattern]) -> List[AnalysisInsight]:
        """Generate basic insights from failure analysis."""
        insights = []
        
        # Insight: High-frequency patterns
        high_freq_patterns = [p for p in patterns if p.frequency >= 3 and p.confidence > 0.7]
        if high_freq_patterns:
            insight = AnalysisInsight(
                insight_id=f"high_freq_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                insight_type="pattern",
                title=f"High-Frequency Failure Pattern Detected",
                description=f"Found {len(high_freq_patterns)} patterns occurring multiple times. "
                           f"Most frequent: '{high_freq_patterns[0].signature}' ({high_freq_patterns[0].frequency} occurrences)",
                confidence=0.9,
                priority=4,
                related_failures=[p.pattern_id for p in high_freq_patterns],
                recommended_actions=[
                    "Investigate the most frequent pattern first",
                    "Look for common root causes across similar failures",
                    "Consider adding specific test cases to prevent regression"
                ]
            )
            insights.append(insight)
        
        # Insight: Failure type distribution
        failure_types = Counter()
        for failure in failures:
            failure_types[self.pattern_detector.classify_failure(failure)] += 1
        
        if len(failure_types) > 1:
            most_common = failure_types.most_common(1)[0]
            insight = AnalysisInsight(
                insight_id=f"types_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                insight_type="analysis",
                title="Failure Type Analysis",
                description=f"Most common failure type: {most_common[0]} ({most_common[1]} occurrences). "
                           f"Total failure types: {len(failure_types)}",
                confidence=0.8,
                priority=3,
                recommended_actions=[
                    f"Focus on resolving {most_common[0]} failures first",
                    "Check if failures are related to specific test categories",
                    "Review test setup and teardown for common issues"
                ]
            )
            insights.append(insight)
        
        # Insight: Location clustering
        location_groups = defaultdict(int)
        for failure in failures:
            if 'filename' in failure:
                location_groups[failure['filename']] += 1
        
        hot_files = [(file, count) for file, count in location_groups.items() if count >= 2]
        if hot_files:
            hot_files.sort(key=lambda x: x[1], reverse=True)
            insight = AnalysisInsight(
                insight_id=f"hotspots_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                insight_type="location",
                title="Failure Hotspots Detected",
                description=f"Found {len(hot_files)} files with multiple failures. "
                           f"Top hotspot: {hot_files[0][0]} ({hot_files[0][1]} failures)",
                confidence=0.85,
                priority=4,
                recommended_actions=[
                    "Review code quality in hotspot files",
                    "Consider refactoring complex or error-prone code",
                    "Add additional test coverage for hotspot areas"
                ]
            )
            insights.append(insight)
        
        return insights
    
    def _generate_enhanced_insights(self, failures: List[Dict[str, Any]], 
                                   patterns: List[FailurePattern],
                                   root_causes: List[Dict[str, Any]],
                                   impacts: List[Dict[str, Any]]) -> List[AnalysisInsight]:
        """Generate enhanced insights using all analysis data."""
        insights = []
        
        # Start with basic insights
        basic_insights = self._generate_basic_insights(failures, patterns)
        insights.extend(basic_insights)
        
        # Enhanced insight: Root cause correlation
        cause_types = defaultdict(int)
        high_confidence_causes = []
        
        for root_cause in root_causes:
            if root_cause['confidence_score'] > 0.7:
                high_confidence_causes.append(root_cause)
                for cause in root_cause['potential_causes']:
                    cause_types[cause['cause_type']] += 1
        
        if high_confidence_causes:
            most_common_cause = max(cause_types.items(), key=lambda x: x[1])
            insight = AnalysisInsight(
                insight_id=f"root_cause_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                insight_type="root_cause",
                title=f"Primary Root Cause Identified: {most_common_cause[0]}",
                description=f"Root cause analysis identified {most_common_cause[0]} as the most common cause type "
                           f"({most_common_cause[1]} occurrences with high confidence)",
                confidence=0.85,
                priority=5,
                related_failures=[rc['failure_id'] for rc in high_confidence_causes],
                recommended_actions=[
                    f"Focus on resolving {most_common_cause[0]} issues first",
                    "Review and address the underlying causes systematically",
                    "Implement preventive measures for this cause type"
                ]
            )
            insights.append(insight)
        
        # Enhanced insight: Priority-based recommendations
        critical_failures = [impact for impact in impacts if impact['criticality'] == 'critical']
        if critical_failures:
            avg_critical_priority = sum(f['priority_score'] for f in critical_failures) / len(critical_failures)
            insight = AnalysisInsight(
                insight_id=f"critical_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                insight_type="priority",
                title=f"Critical Failures Require Immediate Attention",
                description=f"Found {len(critical_failures)} critical failures with average priority score {avg_critical_priority:.1f}",
                confidence=0.9,
                priority=5,
                related_failures=[f['failure_id'] for f in critical_failures],
                recommended_actions=[
                    "Address critical failures before any other work",
                    "Implement hotfixes if necessary",
                    "Review deployment and rollback procedures"
                ]
            )
            insights.append(insight)
        
        # Enhanced insight: Component analysis
        component_impact = defaultdict(lambda: {'count': 0, 'total_priority': 0.0})
        for impact in impacts:
            for component in impact['affected_components']:
                component_impact[component]['count'] += 1
                component_impact[component]['total_priority'] += impact['priority_score']
        
        if component_impact:
            # Find most impacted component
            most_impacted = max(component_impact.items(), 
                              key=lambda x: (x[1]['count'], x[1]['total_priority']))
            
            avg_priority = most_impacted[1]['total_priority'] / most_impacted[1]['count']
            
            insight = AnalysisInsight(
                insight_id=f"component_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                insight_type="component",
                title=f"Component Under Stress: {most_impacted[0]}",
                description=f"Component '{most_impacted[0]}' has {most_impacted[1]['count']} failures "
                           f"with average priority {avg_priority:.1f}",
                confidence=0.8,
                priority=4,
                recommended_actions=[
                    f"Review {most_impacted[0]} component architecture and implementation",
                    "Consider additional testing for this component",
                    "Evaluate if component needs refactoring or redesign"
                ]
            )
            insights.append(insight)
        
        # Enhanced insight: Dependency-based recommendations
        dependency_failures = []
        for root_cause in root_causes:
            for cause in root_cause['potential_causes']:
                if cause['cause_type'] in ['dependency', 'missing_dependency']:
                    dependency_failures.append(root_cause['failure_id'])
        
        if len(dependency_failures) >= 2:
            insight = AnalysisInsight(
                insight_id=f"dependencies_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                insight_type="dependency",
                title="Dependency Issues Detected",
                description=f"Found {len(dependency_failures)} failures related to dependencies",
                confidence=0.75,
                priority=4,
                related_failures=dependency_failures,
                recommended_actions=[
                    "Review project dependencies and versions",
                    "Update dependency management and lock files",
                    "Consider containerization for dependency isolation"
                ]
            )
            insights.append(insight)
        
        # Enhanced insight: Trend-based recommendations (if historical data available)
        try:
            trend_analysis = self.trend_analyzer.analyze_trends()
            if trend_analysis['trend_analysis'] == 'completed':
                trend_insights_data = trend_analysis.get('insights', [])
                for trend_insight in trend_insights_data:
                    insight = AnalysisInsight(
                        insight_id=f"trend_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{trend_insight['type']}",
                        insight_type="trend",
                        title=trend_insight['title'],
                        description=trend_insight['description'],
                        confidence=0.8,
                        priority=4 if trend_insight['severity'] == 'high' else 3,
                        recommended_actions=trend_insight['recommendations']
                    )
                    insights.append(insight)
        except Exception:
            # Graceful fallback if trend analysis fails
            pass
        
        # Sort insights by priority and confidence
        insights.sort(key=lambda x: (x.priority, x.confidence), reverse=True)
        
        return insights
    
    def _get_most_common_failure_type(self, failures: List[Dict[str, Any]]) -> str:
        """Get the most common failure type."""
        failure_types = Counter()
        for failure in failures:
            failure_types[self.pattern_detector.classify_failure(failure)] += 1
        
        if failure_types:
            return failure_types.most_common(1)[0][0]
        return "unknown"


# Convenience function for session-level reporting
def generate_session_report(
    output: Union[str, OutputFormat] = "test_failures_report.md",
    format: Optional[Union[str, OutputFormat]] = None,
    clear: bool = True,
):
    """Generate a report for all collected failures."""
    config = OutputConfig(output, format)
    extractor = FailureExtractor()

    if extractor.failures:
        extractor.save_report(config)

    if clear:
        extractor.clear()
