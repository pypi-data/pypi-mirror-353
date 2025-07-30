"""Code context extraction for test failures."""

import ast
import functools
import importlib.util
import inspect
import sys
import threading
import difflib
import hashlib
import re
import time
from collections import defaultdict, Counter
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Set, Union, Tuple, NamedTuple


class CodeContextExtractor:
    """Extract and manage code context for test failures.

    This class provides intelligent code context extraction with configurable
    depth and context lines. It implements caching for performance and thread-safe
    operation consistent with FailExtract's singleton patterns.

    Features:
    - Configurable context lines before/after failure points
    - Intelligent source code caching with memory management
    - Thread-safe operation for concurrent test execution
    - Enhanced error handling for edge cases
    - Integration with existing source extraction functions

    Attributes:
        _source_cache (Dict[str, tuple]): Cache for source files with modification time
        _lock (threading.RLock): Thread safety lock for cache operations
        _max_cache_size (int): Maximum number of cached source files
    """

    _instance = None
    _lock = threading.RLock()

    def __new__(cls):
        """Implement thread-safe singleton pattern."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        """Initialize the CodeContextExtractor with cache and configuration."""
        if hasattr(self, "_initialized"):
            return

        self._source_cache: Dict[str, tuple] = {}  # file_path -> (content, mtime)
        self._cache_lock = threading.RLock()
        self._max_cache_size = 50  # Maximum cached files
        
        # Phase 2.1: Static analysis caches
        self._import_cache: Dict[str, List[Dict[str, Any]]] = {}  # file_path -> imports
        self._dependency_cache: Dict[str, Set[str]] = {}  # file_path -> dependencies
        self._ast_cache: Dict[str, ast.AST] = {}  # file_path -> parsed AST
        
        # Phase 2.2: Execution tracing (optimized)
        self._execution_trace: List[Dict[str, Any]] = []  # Execution trace log
        self._trace_enabled = False
        self._trace_filters: Set[str] = set()  # Files to trace
        self._trace_start_time: Optional[float] = None
        self._max_trace_entries = 1000
        
        # Performance optimizations
        self._trace_mode = 'static'  # 'static' (no runtime), 'profile' (functions), 'trace' (lines)
        self._sample_rate = 1  # 1 = no sampling, 10 = sample every 10th call
        self._sample_counter = 0
        
        # Pre-compiled filters for ultra-fast exclusion
        self._excluded_prefixes = ('<', sys.prefix, '/usr/lib/python', '/usr/local/lib/python')
        self._excluded_patterns = frozenset(['site-packages', 'dist-packages'])
        
        # Phase 2.4: Coverage integration
        self._coverage_data: Optional[Dict[str, Any]] = None
        self._coverage_available = self._check_coverage_availability()
        
        self._initialized = True

    def extract_function_source_with_context(
        self, frame, context_lines: int = 5, include_line_numbers: bool = True, max_lines: Optional[int] = None
    ) -> Dict[str, Any]:
        """Extract function source with configurable context lines.

        Enhanced version of extract_function_source that provides context lines
        around the failure point and additional metadata for better presentation.

        Args:
            frame: Frame object containing the execution context
            context_lines: Number of lines to include before/after the failure line
            include_line_numbers: Whether to include line number information
            max_lines: Maximum number of lines to return (None for no limit)

        Returns:
            Dictionary containing:
            - 'source': Source code with context (string)
            - 'lines': Source code lines (list of strings)
            - 'failure_line': Line number where failure occurred
            - 'start_line': Starting line number of the extracted context
            - 'end_line': Ending line number of the extracted context
            - 'filename': Path to the source file
            - 'function_name': Name of the function containing the failure
            - 'context_type': Type of context ('function', 'class', 'module')
            - 'include_line_numbers': Whether line numbers were included
            - 'error': Error message if extraction failed

        Example:
            >>> extractor = CodeContextExtractor()
            >>> context = extractor.extract_function_source_with_context(frame, context_lines=3)
            >>> print(context['source'])
            def test_example():
                x = 1
                y = 2
                assert x == y  # <- Failure line
                return True
        """
        # Handle invalid frame
        if frame is None or not hasattr(frame, 'f_code') or frame.f_code is None:
            return {
                'lines': [],
                'source': '',
                'error': 'Invalid frame object',
                'include_line_numbers': include_line_numbers
            }
        
        try:
            filename = frame.f_code.co_filename
            if not filename or filename.startswith("<") or not Path(filename).exists():
                return {
                    'lines': [],
                    'source': '',
                    'error': f'File not found: {filename}',
                    'include_line_numbers': include_line_numbers
                }

            failure_line = frame.f_lineno
            function_name = frame.f_code.co_name

            # Get source content from cache or file
            source_lines = self._get_source_lines(filename)
            if not source_lines:
                return {
                    'lines': [],
                    'source': '',
                    'error': f'Could not read source file: {filename}',
                    'include_line_numbers': include_line_numbers
                }

            # Try to find the function/class containing this line using AST
            context_info = self._find_context_with_ast(
                filename, failure_line, source_lines
            )
            if not context_info:
                # Fallback: use simple line-based context
                context_info = self._get_simple_context(
                    failure_line, source_lines, context_lines
                )
                context_info["context_type"] = "module"
                context_info["function_name"] = function_name

            # Add context lines around the identified region
            start_line = max(1, context_info["start_line"] - context_lines)
            end_line = min(len(source_lines), context_info["end_line"] + context_lines)

            # Extract the source with context
            context_source_lines = source_lines[start_line - 1 : end_line]
            
            # Apply max_lines limit if specified
            if max_lines is not None and len(context_source_lines) > max_lines:
                context_source_lines = context_source_lines[:max_lines]
                end_line = start_line + max_lines - 1

            # Create lines list (without line numbers for tests)
            lines = context_source_lines.copy()

            # Add line numbers if requested for source string
            if include_line_numbers:
                numbered_lines = []
                for i, line in enumerate(context_source_lines, start=start_line):
                    marker = " -> " if i == failure_line else "    "
                    numbered_lines.append(f"{i:4d}{marker}{line}")
                source_with_context = "\n".join(numbered_lines)
            else:
                source_with_context = "\n".join(context_source_lines)

            return {
                "source": source_with_context,
                "lines": lines,  # List of strings without line numbers
                "failure_line": failure_line,
                "start_line": start_line,
                "end_line": end_line,
                "filename": filename,
                "function_name": context_info.get("function_name", function_name),
                "context_type": context_info.get("context_type", "function"),
                "total_lines": len(source_lines),
                "context_lines_before": context_lines,
                "context_lines_after": context_lines,
                "include_line_numbers": include_line_numbers,
            }

        except Exception as e:
            return {
                'lines': [],
                'source': '',
                'error': f'Exception during extraction: {str(e)}',
                'include_line_numbers': include_line_numbers
            }

    def _get_source_lines(self, filename: str) -> Optional[List[str]]:
        """Get source lines from cache or file with thread safety."""
        with self._cache_lock:
            try:
                file_path = Path(filename)
                if not file_path.exists():
                    return None

                current_mtime = file_path.stat().st_mtime

                # Check cache
                if filename in self._source_cache:
                    cached_content, cached_mtime = self._source_cache[filename]
                    if cached_mtime == current_mtime:
                        return cached_content

                # Read file and update cache
                with open(filename, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()
                source_lines = content.splitlines()

                # Manage cache size
                if len(self._source_cache) >= self._max_cache_size:
                    # Remove oldest entry (simple FIFO eviction)
                    oldest_key = next(iter(self._source_cache))
                    del self._source_cache[oldest_key]

                self._source_cache[filename] = (source_lines, current_mtime)
                return source_lines

            except Exception:
                return None

    def _find_context_with_ast(
        self, filename: str, failure_line: int, source_lines: List[str]
    ) -> Optional[Dict[str, Any]]:
        """Find the function/class context using AST parsing."""
        try:
            source_content = "\n".join(source_lines)
            tree = ast.parse(source_content)

            # Find the smallest containing function/class
            best_match = None
            best_size = float("inf")

            for node in ast.walk(tree):
                if isinstance(
                    node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)
                ):
                    if hasattr(node, "lineno") and hasattr(node, "end_lineno"):
                        start_line = node.lineno
                        end_line = node.end_lineno or start_line

                        if start_line <= failure_line <= end_line:
                            size = end_line - start_line
                            if size < best_size:
                                best_size = size
                                context_type = (
                                    "class"
                                    if isinstance(node, ast.ClassDef)
                                    else "function"
                                )
                                best_match = {
                                    "start_line": start_line,
                                    "end_line": end_line,
                                    "function_name": node.name,
                                    "context_type": context_type,
                                }

            return best_match

        except Exception:
            return None

    def _get_simple_context(
        self, failure_line: int, source_lines: List[str], context_lines: int
    ) -> Dict[str, Any]:
        """Get simple line-based context as fallback."""
        start_line = max(1, failure_line - context_lines)
        end_line = min(len(source_lines), failure_line + context_lines)

        return {
            "start_line": start_line,
            "end_line": end_line,
            "context_type": "module",
            "function_name": "unknown",
        }

    def clear_cache(self):
        """Clear all caches including source, imports, dependencies, AST, execution trace, and coverage."""
        with self._cache_lock:
            self._source_cache.clear()
            self._import_cache.clear()
            self._dependency_cache.clear()
            self._ast_cache.clear()
            self._execution_trace.clear()
            self._trace_enabled = False
            self._coverage_data = None
            # Clear trace hooks
            sys.settrace(None)
            sys.setprofile(None)
    
    def _reset_coverage_availability(self):
        """Reset coverage availability check for testing purposes."""
        self._coverage_available = self._check_coverage_availability()

    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics for debugging and monitoring."""
        with self._cache_lock:
            coverage_files = 0
            if self._coverage_data and 'coverage_data' in self._coverage_data:
                coverage_files = len(self._coverage_data['coverage_data'])
            
            return {
                "cached_files": len(self._source_cache),
                "max_cache_size": self._max_cache_size,
                "cache_files": list(self._source_cache.keys()),
                "cached_imports": len(self._import_cache),
                "cached_dependencies": len(self._dependency_cache),
                "cached_asts": len(self._ast_cache),
                "execution_trace_entries": len(self._execution_trace),
                "trace_enabled": self._trace_enabled,
                "trace_mode": getattr(self, '_trace_mode', 'static'),
                "sample_rate": getattr(self, '_sample_rate', 1),
                "coverage_available": self._coverage_available,
                "coverage_files": coverage_files,
                "coverage_loaded": self._coverage_data is not None,
            }

    def analyze_imports(self, filename: str) -> List[Dict[str, Any]]:
        """Analyze imports in a Python file using static analysis.
        
        Extracts and categorizes all import statements from a Python file,
        providing detailed information about each import including line numbers,
        module names, aliases, and import types.
        
        Args:
            filename: Path to the Python file to analyze
            
        Returns:
            List of dictionaries containing import information with keys:
            - 'type': Import type ('import', 'from_import')
            - 'module': Module name being imported
            - 'names': List of imported names (for from imports)
            - 'alias': Alias used (as clause)
            - 'line': Line number of the import statement
            - 'level': Relative import level (0 for absolute)
            
        Example:
            >>> extractor = CodeContextExtractor()
            >>> imports = extractor.analyze_imports("test_file.py")
            >>> print(imports[0])
            {'type': 'import', 'module': 'os', 'names': [], 'alias': None, 'line': 1, 'level': 0}
        """
        with self._cache_lock:
            # Check cache first
            if filename in self._import_cache:
                cached_imports, cached_mtime = self._import_cache[filename]
                try:
                    current_mtime = Path(filename).stat().st_mtime
                    if cached_mtime == current_mtime:
                        return cached_imports
                except (OSError, FileNotFoundError):
                    # File no longer exists or permission error
                    del self._import_cache[filename]
                    return []
            
            try:
                # Get or parse AST
                tree = self._get_ast(filename)
                if not tree:
                    return []
                
                imports = []
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            imports.append({
                                'type': 'import',
                                'module': alias.name,
                                'names': [],
                                'alias': alias.asname,
                                'line': node.lineno,
                                'level': 0,
                            })
                    
                    elif isinstance(node, ast.ImportFrom):
                        module_name = node.module or ''
                        names = [alias.name for alias in node.names] if node.names else []
                        
                        imports.append({
                            'type': 'from_import',
                            'module': module_name,
                            'names': names,
                            'alias': None,  # from imports use individual aliases
                            'line': node.lineno,
                            'level': node.level,
                        })
                
                # Cache the results with size limiting
                current_mtime = Path(filename).stat().st_mtime
                
                # Manage cache size for imports
                if len(self._import_cache) >= self._max_cache_size:
                    # Remove oldest entry (simple FIFO eviction)
                    oldest_key = next(iter(self._import_cache))
                    del self._import_cache[oldest_key]
                
                self._import_cache[filename] = (imports, current_mtime)
                
                return imports
                
            except Exception:
                return []

    def analyze_dependencies(self, filename: str, max_depth: int = 3) -> Dict[str, Any]:
        """Analyze file dependencies and create dependency graph.
        
        Performs recursive dependency analysis starting from a file to build
        a comprehensive dependency graph including direct imports, transitive
        dependencies, and circular dependency detection.
        
        Args:
            filename: Path to the Python file to analyze
            max_depth: Maximum recursion depth for dependency analysis
            
        Returns:
            Dictionary containing dependency analysis with keys:
            - 'direct_imports': List of directly imported modules
            - 'dependency_graph': Nested dict of dependencies by depth level
            - 'circular_dependencies': List of detected circular dependencies
            - 'unresolved_modules': List of modules that couldn't be resolved
            - 'total_dependencies': Count of all unique dependencies
            
        Example:
            >>> extractor = CodeContextExtractor()
            >>> deps = extractor.analyze_dependencies("test_file.py")
            >>> print(deps['total_dependencies'])
            15
        """
        with self._cache_lock:
            # Check cache
            cache_key = f"{filename}:{max_depth}"
            if cache_key in self._dependency_cache:
                return self._dependency_cache[cache_key]
            
            try:
                dependency_graph = {}
                visited = set()
                circular_deps = []
                unresolved = set()
                
                def _analyze_recursive(file_path: str, depth: int, path_stack: List[str]):
                    if depth > max_depth or file_path in path_stack:
                        if file_path in path_stack:
                            # Circular dependency detected
                            cycle_start = path_stack.index(file_path)
                            cycle = path_stack[cycle_start:] + [file_path]
                            circular_deps.append(cycle)
                        return set()
                    
                    if file_path in visited:
                        return dependency_graph.get(file_path, set())
                    
                    visited.add(file_path)
                    imports = self.analyze_imports(file_path)
                    dependencies = set()
                    
                    for import_info in imports:
                        module_name = import_info['module']
                        if not module_name:
                            continue
                            
                        # Try to resolve module to file path
                        resolved_path = self._resolve_module_path(module_name, file_path)
                        if resolved_path and Path(resolved_path).exists():
                            # Treat standard library modules as unresolved for dependency analysis
                            if self._is_standard_library_path(resolved_path):
                                unresolved.add(module_name)
                            else:
                                # Only add dependency if it's within depth limit
                                if depth + 1 <= max_depth:
                                    dependencies.add(resolved_path)
                                    # Recurse into dependencies
                                    sub_deps = _analyze_recursive(
                                        resolved_path, depth + 1, path_stack + [file_path]
                                    )
                                    dependencies.update(sub_deps)
                        else:
                            unresolved.add(module_name)
                    
                    dependency_graph[file_path] = dependencies
                    return dependencies
                
                # Start analysis
                direct_deps = _analyze_recursive(filename, 0, [])
                
                # Get direct imports for summary
                direct_imports = [imp['module'] for imp in self.analyze_imports(filename)]
                
                result = {
                    'direct_imports': direct_imports,
                    'dependency_graph': dependency_graph,
                    'circular_dependencies': circular_deps,
                    'unresolved_modules': list(unresolved),
                    'total_dependencies': len(direct_deps),
                }
                
                # Manage cache size for dependencies
                if len(self._dependency_cache) >= self._max_cache_size:
                    # Remove oldest entry (simple FIFO eviction)
                    oldest_key = next(iter(self._dependency_cache))
                    del self._dependency_cache[oldest_key]
                
                self._dependency_cache[cache_key] = result
                return result
                
            except Exception:
                return {
                    'direct_imports': [],
                    'dependency_graph': {},
                    'circular_dependencies': [],
                    'unresolved_modules': [],
                    'total_dependencies': 0,
                }

    def get_function_dependencies(self, frame) -> Dict[str, Any]:
        """Get dependencies specific to a function's execution context.
        
        Analyzes the imports and dependencies relevant to a specific function's
        execution, providing contextual dependency information for failure analysis.
        
        Args:
            frame: Frame object containing the execution context
            
        Returns:
            Dictionary containing function-specific dependency information
        """
        try:
            filename = frame.f_code.co_filename
            if not filename or filename.startswith("<") or not Path(filename).exists():
                return {}
            
            # Get file-level dependencies
            file_deps = self.analyze_dependencies(filename, max_depth=2)
            
            # Get function-specific imports (variables in scope)
            function_imports = []
            for name, obj in frame.f_globals.items():
                if hasattr(obj, '__module__') and obj.__module__ and obj.__module__ != 'builtins':
                    function_imports.append({
                        'name': name,
                        'module': obj.__module__,
                        'type': type(obj).__name__,
                    })
            
            return {
                'file_dependencies': file_deps,
                'function_imports': function_imports[:20],  # Limit for performance
                'filename': filename,
                'function_name': frame.f_code.co_name,
            }
            
        except Exception:
            return {}

    def _get_ast(self, filename: str) -> Optional[ast.AST]:
        """Get parsed AST for a file with caching."""
        try:
            # Check AST cache
            if filename in self._ast_cache:
                return self._ast_cache[filename]
            
            source_lines = self._get_source_lines(filename)
            if not source_lines:
                return None
            
            source_content = "\n".join(source_lines)
            tree = ast.parse(source_content, filename=filename)
            
            # Cache AST (limit cache size)
            if len(self._ast_cache) >= self._max_cache_size:
                # Remove oldest entry
                oldest_key = next(iter(self._ast_cache))
                del self._ast_cache[oldest_key]
            
            self._ast_cache[filename] = tree
            return tree
            
        except Exception:
            return None

    def _is_standard_library_path(self, file_path: str) -> bool:
        """Check if a file path belongs to the standard library."""
        if not file_path:
            return False
        try:
            path_obj = Path(file_path)
            system_paths = ['/usr/lib', '/usr/local/lib', sys.prefix]
            return any(str(path_obj).startswith(sys_path) for sys_path in system_paths)
        except Exception:
            return False

    def _resolve_module_path(self, module_name: str, current_file: str) -> Optional[str]:
        """Resolve a module name to its file path, prioritizing local files."""
        try:
            current_dir = Path(current_file).parent
            
            # Handle relative imports first
            if module_name.startswith('.'):
                # Simple relative import resolution
                parts = module_name.lstrip('.').split('.')
                if parts and parts[0]:
                    target_path = current_dir / (parts[0] + '.py')
                    if target_path.exists():
                        return str(target_path)
                return None
            
            # PRIORITY 1: Check for local files first (most important for tests)
            local_patterns = [
                current_dir / f"{module_name}.py",                                    # Same directory
                current_dir / module_name / "__init__.py",                          # Package in subdirectory
                current_dir.parent / f"{module_name}.py",                          # Parent directory
                current_dir.parent / "src" / f"{module_name}.py",                  # Common src layout
                current_dir.parent / "src" / module_name / "__init__.py",          # Package in src
                current_dir / ".." / f"{module_name}.py",                          # Relative parent
            ]
            
            # Handle dotted module names (e.g., package.module)
            if '.' in module_name:
                parts = module_name.split('.')
                # Try package/module.py structure
                local_patterns.extend([
                    current_dir / parts[0] / f"{parts[1]}.py",
                    current_dir.parent / parts[0] / f"{parts[1]}.py",
                    current_dir.parent / "src" / parts[0] / f"{parts[1]}.py",
                ])
            
            # Check all local patterns first
            for path in local_patterns:
                try:
                    if path.exists() and path.is_file():
                        return str(path.resolve())  # Return absolute path
                except (OSError, RuntimeError):
                    # Handle permission errors or circular symlinks
                    continue
            
            # PRIORITY 2: Try importlib for system modules only after local search fails
            try:
                spec = importlib.util.find_spec(module_name)
                if spec and spec.origin:
                    # Only accept .py files, not compiled extensions or built-ins
                    if (spec.origin.endswith('.py') and 
                        not spec.origin.endswith('.so') and 
                        not spec.origin.startswith('<')):
                        # Avoid system libraries in common test scenarios
                        origin_path = Path(spec.origin)
                        # Skip if it's clearly a system library
                        system_paths = ['/usr/lib', '/usr/local/lib', sys.prefix]
                        if not any(str(origin_path).startswith(sys_path) for sys_path in system_paths):
                            return spec.origin
            except (ImportError, ModuleNotFoundError, ValueError, AttributeError):
                pass
            
            # PRIORITY 3: Last resort - try sys.path search
            for sys_path in sys.path:
                if sys_path:  # Skip empty path entries
                    try:
                        potential_file = Path(sys_path) / f"{module_name}.py"
                        if potential_file.exists() and potential_file.is_file():
                            return str(potential_file.resolve())
                        
                        potential_package = Path(sys_path) / module_name / "__init__.py"
                        if potential_package.exists() and potential_package.is_file():
                            return str(potential_package.resolve())
                    except (OSError, RuntimeError):
                        continue
            
            return None
            
        except Exception:
            return None

    def start_execution_trace(self, file_filters: Optional[List[str]] = None, 
                            max_trace_entries: int = 1000,
                            mode: str = 'static',
                            sample_rate: int = 1) -> None:
        """Start optimized execution tracing for dependency analysis.
        
        Enables execution tracing to track function calls and imports during
        test execution. This provides runtime dependency information to complement
        static analysis.
        
        Args:
            file_filters: List of file paths/patterns to trace (None for all files)
            max_trace_entries: Maximum number of trace entries to keep
            mode: 'static' (no runtime, 0% overhead), 'profile' (functions), 'trace' (lines)
            sample_rate: Sample every Nth call (1=no sampling, 10=sample 10%)
            
        Note:
            Defaults to 'static' mode for 0% overhead. Use 'profile' for <10%
            overhead with runtime dependency tracking.
        """
        import time
        
        with self._cache_lock:
            self._execution_trace.clear()
            self._trace_mode = mode
            self._max_trace_entries = max_trace_entries
            self._sample_rate = sample_rate
            self._sample_counter = 0
            
            if file_filters:
                self._trace_filters = set(file_filters)
            else:
                self._trace_filters.clear()
            
            # Static mode: no runtime tracing (0% overhead)
            if mode == 'static':
                self._trace_enabled = False
                self._trace_start_time = None
                return
            
            # Runtime modes
            self._trace_enabled = True
            self._trace_start_time = time.time()
            
            # Use profile for function-level only (much faster)
            if mode == 'profile':
                sys.setprofile(self._optimized_profile_function)
            else:
                # Fallback to line-level tracing (slower)
                sys.settrace(self._trace_function)

    def stop_execution_trace(self) -> List[Dict[str, Any]]:
        """Stop execution tracing and return collected trace data.
        
        Returns:
            List of trace entries with execution information
        """
        with self._cache_lock:
            self._trace_enabled = False
            # Clear both trace and profile hooks
            sys.settrace(None)
            sys.setprofile(None)
            
            trace_data = self._execution_trace.copy()
            return trace_data

    def _optimized_profile_function(self, frame, event: str, arg) -> None:
        """Ultra-lightweight profile function optimized for <10% overhead.
        
        Uses sys.setprofile() for function-level only tracing, avoiding
        line-by-line overhead. Includes pre-compiled filters and sampling.
        """
        # Fast path: check if tracing is enabled (avoid attribute lookup)
        if not self._trace_enabled:
            return
        
        # Even faster sampling check
        if self._sample_rate > 1:
            self._sample_counter += 1
            if self._sample_counter % self._sample_rate:
                return
        
        # Get filename once
        filename = frame.f_code.co_filename
        
        # Ultra-fast exclusion - check most common patterns first
        if (filename.startswith('<') or 
            filename.startswith(self._excluded_prefixes[1]) or  # sys.prefix
            'site-packages' in filename):
            return
        
        # Skip non-call events early
        if event != 'call':
            return
        
        # Only apply file filters if they exist (avoid set operations when possible)
        if self._trace_filters:
            if not any(filter_path in filename for filter_path in self._trace_filters):
                return
        
        # Minimal trace entry - avoid dictionary creation overhead
        if len(self._execution_trace) < self._max_trace_entries:
            # Use tuple for minimal memory and creation overhead
            self._execution_trace.append({
                'event': 'call',
                'filename': filename,
                'function': frame.f_code.co_name,
                'line': frame.f_lineno,
                'timestamp': 0
            })

    def _trace_function(self, frame, event: str, arg) -> Optional[Callable]:
        """Fallback trace function for line-level tracing (slower).
        
        Used when mode='trace' is requested. Has higher overhead due to
        line-by-line tracing but provides more detailed information.
        """
        if not self._trace_enabled:
            return None
        
        try:
            filename = frame.f_code.co_filename
            
            # Fast exclusion using pre-compiled patterns
            if filename.startswith(self._excluded_prefixes):
                return None
            
            if any(pattern in filename for pattern in self._excluded_patterns):
                return None
            
            # Filter based on file filters if specified
            if self._trace_filters:
                if not any(filter_path in filename for filter_path in self._trace_filters):
                    return None
            
            # Only trace important events to minimize overhead
            if event in ('call', 'return', 'exception'):
                import time
                
                trace_entry = {
                    'event': event,
                    'filename': filename,
                    'function': frame.f_code.co_name,
                    'line': frame.f_lineno,
                    'timestamp': time.time() - (self._trace_start_time or 0),
                }
                
                # Add exception info for exception events
                if event == 'exception' and arg:
                    trace_entry['exception_type'] = type(arg[1]).__name__
                    trace_entry['exception_message'] = str(arg[1])
                
                # Add return value info for return events (limited)
                if event == 'return' and arg is not None:
                    try:
                        trace_entry['return_type'] = type(arg).__name__
                    except:
                        pass
                
                with self._cache_lock:
                    self._execution_trace.append(trace_entry)
                    
                    # Limit trace size for memory management
                    if len(self._execution_trace) > self._max_trace_entries:
                        self._execution_trace = self._execution_trace[-self._max_trace_entries:]
            
            return self._trace_function
            
        except Exception:
            # Tracing should never break execution
            return None

    def get_execution_summary(self) -> Dict[str, Any]:
        """Get summary of execution trace data.
        
        Returns:
            Dictionary containing execution trace analysis
        """
        with self._cache_lock:
            if not self._execution_trace:
                return {'total_events': 0, 'files_traced': [], 'functions_called': []}
            
            files_traced = set()
            functions_called = set()
            events_by_type = {}
            exceptions = []
            
            for entry in self._execution_trace:
                files_traced.add(entry['filename'])
                functions_called.add(f"{entry['filename']}:{entry['function']}")
                
                event_type = entry['event']
                events_by_type[event_type] = events_by_type.get(event_type, 0) + 1
                
                if event_type == 'exception':
                    exceptions.append({
                        'type': entry.get('exception_type'),
                        'message': entry.get('exception_message'),
                        'location': f"{entry['filename']}:{entry['line']}",
                    })
            
            return {
                'total_events': len(self._execution_trace),
                'files_traced': list(files_traced),
                'functions_called': list(functions_called)[:50],  # Limit for readability
                'events_by_type': events_by_type,
                'exceptions': exceptions,
                'trace_enabled': self._trace_enabled,
                'trace_mode': getattr(self, '_trace_mode', 'static'),
                'sample_rate': getattr(self, '_sample_rate', 1),
            }

    def integrate_trace_with_dependencies(self, frame) -> Dict[str, Any]:
        """Integrate execution trace data with static dependency analysis.
        
        Combines static analysis results with runtime execution information
        to provide comprehensive dependency context for failure analysis.
        
        Args:
            frame: Frame object containing the execution context
            
        Returns:
            Dictionary containing integrated dependency and execution information
        """
        try:
            filename = frame.f_code.co_filename
            if not filename or filename.startswith("<"):
                return {}
            
            # Get static dependencies
            static_deps = self.get_function_dependencies(frame)
            
            # Get execution trace summary
            exec_summary = self.get_execution_summary()
            
            # Find relevant trace entries for this file
            relevant_traces = []
            for entry in self._execution_trace:
                if entry['filename'] == filename:
                    relevant_traces.append(entry)
            
            return {
                'static_analysis': static_deps,
                'execution_trace': {
                    'summary': exec_summary,
                    'relevant_entries': relevant_traces[-20:],  # Last 20 entries
                },
                'integration_timestamp': self._trace_start_time,
                'trace_active': self._trace_enabled,
            }
            
        except Exception:
            return {}

    def build_dependency_graph(self, root_file: str, max_depth: int = 3) -> 'DependencyGraph':
        """Build a comprehensive dependency graph starting from a root file.
        
        Creates a structured dependency graph that can be used for visualization,
        analysis, and understanding test code relationships.
        
        Args:
            root_file: Starting file for dependency analysis
            max_depth: Maximum depth for dependency traversal
            
        Returns:
            DependencyGraph object containing the complete graph structure
        """
        return DependencyGraph.build_from_file(root_file, max_depth, self)

    def _check_coverage_availability(self) -> bool:
        """Check if coverage.py is available for integration."""
        try:
            import importlib
            importlib.import_module('coverage')
            return True
        except ImportError:
            return False

    def integrate_coverage_data(self, coverage_data_file: Optional[str] = None) -> Dict[str, Any]:
        """Integrate with coverage.py data when available.
        
        Loads and processes coverage data to provide insights into which code
        paths were executed during test runs. This complements static analysis
        with runtime execution information.
        
        Args:
            coverage_data_file: Path to coverage data file (None for auto-detect)
            
        Returns:
            Dictionary containing coverage integration results
        """
        if not self._coverage_available:
            return {
                'available': False,
                'error': 'coverage.py not available',
                'files_analyzed': 0,
                'coverage_data': {},
            }
        
        try:
            import coverage
            
            # Load coverage data
            cov = coverage.Coverage(data_file=coverage_data_file)
            cov.load()
            
            coverage_info = {
                'available': True,
                'data_file': coverage_data_file or cov.config.data_file,
                'files_analyzed': 0,
                'coverage_data': {},
                'summary': {},
            }
            
            # Get coverage data for all measured files
            measured_files = cov.get_data().measured_files()
            coverage_info['files_analyzed'] = len(measured_files)
            
            for filename in measured_files:
                try:
                    # Get line coverage data
                    analysis = cov.analysis2(filename)
                    if analysis:
                        statements, excluded, missing, missing_branches = analysis
                        
                        coverage_info['coverage_data'][filename] = {
                            'statements': list(statements),
                            'excluded': list(excluded) if excluded else [],
                            'missing': list(missing) if missing else [],
                            'missing_branches': list(missing_branches) if missing_branches else [],
                            'coverage_percent': (
                                (len(statements) - len(missing)) / len(statements) * 100
                                if statements else 0
                            ),
                        }
                except Exception:
                    # Skip files that can't be analyzed
                    continue
            
            # Generate summary statistics
            total_statements = sum(
                len(data['statements']) 
                for data in coverage_info['coverage_data'].values()
            )
            total_missing = sum(
                len(data['missing']) 
                for data in coverage_info['coverage_data'].values()
            )
            
            coverage_info['summary'] = {
                'total_files': len(coverage_info['coverage_data']),
                'total_statements': total_statements,
                'total_missing': total_missing,
                'overall_coverage': (
                    (total_statements - total_missing) / total_statements * 100
                    if total_statements > 0 else 0
                ),
            }
            
            self._coverage_data = coverage_info
            return coverage_info
            
        except Exception as e:
            return {
                'available': True,
                'error': f'Failed to load coverage data: {str(e)}',
                'files_analyzed': 0,
                'coverage_data': {},
            }

    def get_coverage_for_file(self, filename: str) -> Optional[Dict[str, Any]]:
        """Get coverage information for a specific file.
        
        Args:
            filename: Path to the file to get coverage for
            
        Returns:
            Coverage information dictionary or None if not available
        """
        if not self._coverage_data or 'coverage_data' not in self._coverage_data:
            return None
        
        return self._coverage_data['coverage_data'].get(filename)

    def get_executed_lines_for_function(self, frame) -> Dict[str, Any]:
        """Get coverage information for the specific function context.
        
        Analyzes coverage data to determine which lines were executed
        in the context of the failing function.
        
        Args:
            frame: Frame object containing the execution context
            
        Returns:
            Dictionary containing function-specific coverage information
        """
        try:
            filename = frame.f_code.co_filename
            if not filename or filename.startswith("<"):
                return {}
            
            # Get file coverage data
            file_coverage = self.get_coverage_for_file(filename)
            if not file_coverage:
                return {'coverage_available': False}
            
            # Get function line range
            enhanced_context = self.extract_function_source_with_context(frame, context_lines=0)
            if not enhanced_context:
                return {'coverage_available': True, 'function_context': False}
            
            start_line = enhanced_context.get('start_line', 0)
            end_line = enhanced_context.get('end_line', 0)
            
            # Filter coverage data to function range
            function_statements = [
                line for line in file_coverage['statements']
                if start_line <= line <= end_line
            ]
            function_missing = [
                line for line in file_coverage['missing']
                if start_line <= line <= end_line
            ]
            function_executed = [
                line for line in function_statements
                if line not in function_missing
            ]
            
            return {
                'coverage_available': True,
                'function_context': True,
                'filename': filename,
                'function_name': frame.f_code.co_name,
                'line_range': {'start': start_line, 'end': end_line},
                'statements_in_function': function_statements,
                'executed_lines': function_executed,
                'missing_lines': function_missing,
                'function_coverage_percent': (
                    len(function_executed) / len(function_statements) * 100
                    if function_statements else 0
                ),
                'total_statements': len(function_statements),
                'executed_count': len(function_executed),
                'missing_count': len(function_missing),
            }
            
        except Exception:
            return {'coverage_available': False, 'error': 'Analysis failed'}

    def combine_coverage_with_dependencies(self, frame) -> Dict[str, Any]:
        """Combine coverage data with dependency analysis.
        
        Provides comprehensive analysis combining static dependencies,
        execution traces, and coverage data for complete context.
        
        Args:
            frame: Frame object containing the execution context
            
        Returns:
            Dictionary containing combined analysis results
        """
        try:
            # Get all analysis components
            dependencies = self.get_function_dependencies(frame)
            trace_integration = self.integrate_trace_with_dependencies(frame)
            function_coverage = self.get_executed_lines_for_function(frame)
            
            filename = frame.f_code.co_filename
            
            # Check for invalid filename - return error for filenames like <string>, <stdin>, etc.
            if filename and filename.startswith("<"):
                return {
                    'error': 'Invalid filename or file analysis failed',
                    'filename': filename,
                }
            
            # Get dependency coverage
            dependency_coverage = {}
            if dependencies and 'file_dependencies' in dependencies:
                for dep_file in dependencies['file_dependencies'].get('direct_imports', []):
                    # Try to resolve import to file path
                    resolved_path = self._resolve_module_path(dep_file, filename)
                    if resolved_path:
                        dep_coverage = self.get_coverage_for_file(resolved_path)
                        if dep_coverage:
                            dependency_coverage[dep_file] = {
                                'file_path': resolved_path,
                                'coverage_percent': dep_coverage['coverage_percent'],
                                'missing_lines': len(dep_coverage['missing']),
                                'total_statements': len(dep_coverage['statements']),
                            }
            
            return {
                'filename': filename,
                'function_name': frame.f_code.co_name,
                'analysis_components': {
                    'static_dependencies': dependencies,
                    'execution_trace': trace_integration,
                    'function_coverage': function_coverage,
                    'dependency_coverage': dependency_coverage,
                },
                'summary': {
                    'dependencies_analyzed': len(dependencies.get('file_dependencies', {}).get('direct_imports', [])),
                    'dependencies_with_coverage': len(dependency_coverage),
                    'function_coverage_available': function_coverage.get('coverage_available', False),
                    'execution_trace_available': trace_integration.get('trace_active', False),
                },
                'integration_timestamp': datetime.now().isoformat(),
            }
            
        except Exception:
            return {
                'error': 'Combined analysis failed',
                'filename': getattr(frame, 'f_code', {}).get('co_filename', 'unknown'),
            }


