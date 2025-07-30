"""Pytest configuration and shared fixtures for failextract testing."""

import json
import tempfile
import os
import sys
from pathlib import Path
from unittest.mock import Mock

import pytest

# Set development environment flag to bypass graceful degradation
os.environ['FAILEXTRACT_DEV_MODE'] = '1'

# Add src to Python path for direct imports during testing
src_path = Path(__file__).parent.parent / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

from failextract import FailureExtractor, OutputFormat


@pytest.fixture(scope="session", autouse=True)
def ensure_clean_session():
    """Ensure clean state at the start and end of test session."""
    # Clean state at session start
    FailureExtractor._instance = None
    yield
    # Clean state at session end
    if FailureExtractor._instance is not None:
        FailureExtractor._instance.reset()
        FailureExtractor._instance = None


@pytest.fixture
def clean_extractor():
    """Provide a clean FailureExtractor instance for each test."""
    # Reset singleton state completely
    FailureExtractor._instance = None
    extractor = FailureExtractor()
    extractor.reset()

    # Ensure clean state before test
    assert len(extractor.failures) == 0
    assert len(extractor.passed) == 0
    assert extractor._max_failures is None
    assert extractor._max_passed is None

    yield extractor

    # Clean up after test - comprehensive cleanup
    extractor.reset()
    FailureExtractor._instance = None


@pytest.fixture
def sample_failure_data():
    """Sample failure data for testing."""
    return {
        "timestamp": "2024-01-01T12:00:00",
        "test_name": "test_sample_failure",
        "test_module": "test_module",
        "test_file": "/path/to/test_file.py",
        "test_source": "def test_sample_failure():\n    assert False",
        "test_args": "()",
        "test_kwargs": "{}",
        "exception_type": "AssertionError",
        "exception_message": "Test failed",
        "exception_traceback": "Traceback (most recent call last):\n  File...",
        "extracted_code": [
            {
                "file": "/path/to/module.py",
                "function": "failing_function",
                "line": 42,
                "source": 'def failing_function():\n    raise AssertionError("Test failed")',
            }
        ],
        "fixtures": [
            {
                "name": "tmp_path",
                "type": "builtin",
                "description": "Temporary directory unique to test invocation",
            }
        ],
    }


@pytest.fixture
def multiple_failure_data(sample_failure_data):
    """Multiple failure entries for testing collections."""
    failures = []
    for i in range(3):
        failure = sample_failure_data.copy()
        failure["test_name"] = f"test_failure_{i}"
        failure["timestamp"] = f"2024-01-0{i + 1}T12:00:00"
        failures.append(failure)
    return failures


@pytest.fixture
def temp_output_file():
    """Temporary file for output testing."""
    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".json") as f:
        temp_path = f.name
    yield temp_path
    # Cleanup
    Path(temp_path).unlink(missing_ok=True)


@pytest.fixture
def temp_directory():
    """Temporary directory for file operations."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield Path(temp_dir)


@pytest.fixture
def mock_test_function():
    """Mock test function for testing."""

    def sample_test_function():
        """Sample test function."""
        pass

    sample_test_function.__name__ = "test_sample"
    sample_test_function.__module__ = "test_module"
    return sample_test_function


@pytest.fixture
def mock_frame():
    """Mock frame object for testing frame inspection."""
    frame = Mock()
    frame.f_code.co_filename = "/path/to/test.py"
    frame.f_code.co_name = "test_function"
    frame.f_lineno = 42
    frame.f_locals = {"local_var": "value"}
    frame.f_globals = {"global_var": "value"}
    return frame


@pytest.fixture
def sample_conftest_content():
    """Sample conftest.py content for testing."""
    return '''
import pytest

@pytest.fixture
def sample_fixture():
    """Sample fixture for testing."""
    return "fixture_value"

@pytest.fixture(scope="module")
def module_fixture():
    """Module-scoped fixture."""
    return "module_value"

@pytest.fixture
def dependent_fixture(sample_fixture):
    """Fixture that depends on another fixture."""
    return f"dependent_{sample_fixture}"
'''


@pytest.fixture
def sample_test_file_content():
    """Sample test file content."""
    return '''
import pytest

def test_simple():
    """Simple test function."""
    assert True

def test_with_fixture(sample_fixture):
    """Test using a fixture."""
    assert sample_fixture == "fixture_value"

class TestClass:
    """Test class with methods."""
    
    def test_method(self):
        """Test method in class."""
        assert True
    
    def test_method_with_fixture(self, module_fixture):
        """Test method using fixture."""
        assert module_fixture == "module_value"
'''


@pytest.fixture
def expected_json_output(sample_failure_data):
    """Expected JSON output for testing."""
    return json.dumps([sample_failure_data], indent=2, default=str)


@pytest.fixture
def expected_markdown_output():
    """Expected markdown output structure."""
    return """# Test Failure Report

Generated: """


@pytest.fixture
def concurrent_test_data():
    """Data for concurrent testing."""
    return {
        "num_threads": 5,
        "operations_per_thread": 10,
        "test_data": [
            {"test_name": f"concurrent_test_{i}", "result": f"result_{i}"}
            for i in range(50)
        ],
    }


@pytest.fixture(scope="session")
def test_session_data():
    """Session-level test data."""
    return {
        "session_id": "test_session_123",
        "start_time": "2024-01-01T00:00:00",
        "test_environment": "pytest",
    }


# Parametrized fixtures for testing multiple formats
@pytest.fixture(
    params=[
        OutputFormat.JSON,
        OutputFormat.MARKDOWN,
        # HTML format has been removed from the codebase
        # OutputFormat.HTML,
        OutputFormat.YAML,
        OutputFormat.XML,
        OutputFormat.CSV,
    ]
)
def output_format(request):
    """Parametrized fixture for testing all output formats."""
    return request.param


@pytest.fixture(params=[True, False])
def bool_parameter(request):
    """Parametrized boolean fixture."""
    return request.param


# Mock fixtures for external dependencies
@pytest.fixture
def mock_yaml_module(monkeypatch):
    """Mock PyYAML module for testing YAML functionality."""
    mock_yaml = Mock()
    mock_yaml.dump.return_value = "mocked: yaml\noutput: test"
    monkeypatch.setattr("yaml", mock_yaml, raising=False)
    return mock_yaml


@pytest.fixture
def mock_file_system(monkeypatch, temp_directory):
    """Mock file system operations."""

    def mock_exists(path):
        return str(path).endswith(".py")

    def mock_open(path, mode="r"):
        if "conftest" in str(path):
            return Mock(read=lambda: "# Mock conftest content")
        return Mock(read=lambda: "# Mock file content")

    monkeypatch.setattr(Path, "exists", mock_exists)
    return temp_directory


@pytest.fixture
def performance_test_data():
    """Large dataset for performance testing."""
    failures = []
    for i in range(100):
        failure = {
            "timestamp": f"2024-01-01T{i:02d}:00:00",
            "test_name": f"performance_test_{i}",
            "test_module": f"test_module_{i % 10}",
            "test_file": f"/path/to/test_{i}.py",
            "test_source": f"def performance_test_{i}():\n    assert False",
            "exception_type": "AssertionError",
            "exception_message": f"Performance test {i} failed",
            "extracted_code": [
                {
                    "file": f"/path/to/code_{i}.py",
                    "function": f"function_{i}",
                    "line": i + 1,
                    "source": f"def function_{i}():\n    # Function {i} implementation\n    pass",
                }
            ],
        }
        failures.append(failure)
    return failures
