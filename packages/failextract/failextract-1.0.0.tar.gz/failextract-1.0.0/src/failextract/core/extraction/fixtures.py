"""Fixture extraction for test failures."""

import ast
import inspect
import threading
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Set, Union


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


