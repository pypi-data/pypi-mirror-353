"""Core decorator functionality tests for extract_on_failure decorator."""

import json
from unittest.mock import Mock, patch

import pytest

from failextract import FailureExtractor, extract_on_failure


class TestExtractOnFailureDecoratorCore:
    """Core functionality tests for extract_on_failure decorator."""

    def test_decorator_with_exception_basic(self, temp_directory):
        """Test basic decorator functionality when exception occurs."""
        extractor = FailureExtractor()
        extractor.clear()

        @extract_on_failure
        def test_that_fails():
            raise ValueError("Test failure for coverage")

        # Should raise the original exception
        with pytest.raises(ValueError, match="Test failure for coverage"):
            test_that_fails()

        # Should have captured the failure
        assert len(extractor.failures) == 1
        failure = extractor.failures[0]
        assert failure["exception_type"] == "ValueError"
        assert failure["exception_message"] == "Test failure for coverage"

    def test_decorator_with_output_file(self, temp_directory):
        """Test decorator with output_file parameter."""
        output_file = temp_directory / "test_failures.json"

        @extract_on_failure(output=str(output_file))
        def test_that_fails():
            raise RuntimeError("File output test")

        # Should raise the original exception
        with pytest.raises(RuntimeError, match="File output test"):
            test_that_fails()

        # Should have written to file
        assert output_file.exists()
        with open(output_file, "r") as f:
            data = json.load(f)

        assert len(data) >= 1
        assert any(item["exception_type"] == "RuntimeError" for item in data)

    def test_decorator_bare_usage(self):
        """Test decorator used without parentheses."""
        extractor = FailureExtractor()
        extractor.clear()

        # Test bare decorator (callable as first argument)
        def test_function():
            raise TypeError("Bare decorator test")

        # Apply decorator directly
        decorated_func = extract_on_failure(test_function)

        # Should have the marker attribute
        assert hasattr(decorated_func, "_extract_on_failure")
        assert decorated_func._extract_on_failure is True

        # Should work when called
        with pytest.raises(TypeError, match="Bare decorator test"):
            decorated_func()

    def test_decorator_with_successful_function(self):
        """Test decorator when function succeeds (no exception)."""
        extractor = FailureExtractor()
        extractor.clear()

        @extract_on_failure
        def test_that_succeeds():
            return "success"

        # Should return normal result
        result = test_that_succeeds()
        assert result == "success"

        # Should not have captured any failures
        assert len(extractor.failures) == 0

    def test_decorator_exception_handling_chain(self):
        """Test decorator with complex exception handling."""
        extractor = FailureExtractor()
        extractor.clear()

        @extract_on_failure
        def test_exception_chain():
            try:
                raise ValueError("Original error")
            except ValueError as e:
                raise RuntimeError("Chained error") from e

        with pytest.raises(RuntimeError):
            test_exception_chain()

        # Should capture the final exception
        assert len(extractor.failures) == 1
        failure = extractor.failures[0]
        assert failure["exception_type"] == "RuntimeError"

    def test_decorator_wrapper_preserves_function_metadata(self):
        """Test that decorator wrapper preserves original function metadata."""

        def original_function():
            """Original docstring."""
            return "original"

        # Apply decorator
        decorated = extract_on_failure(original_function)

        # Should preserve function name and other metadata
        assert decorated.__name__ == "original_function"
        assert hasattr(decorated, "_extract_on_failure")

    def test_decorator_with_callable_first_argument(self):
        """Test decorator behavior with callable as first argument."""

        def test_func():
            raise Exception("Callable arg test")

        # When called with function as first argument (bare decorator)
        result = extract_on_failure(test_func)

        # Should return wrapped function
        assert callable(result)
        assert hasattr(result, "_extract_on_failure")

        # Function should still raise when called
        with pytest.raises(Exception):
            result()

    def test_decorator_both_output_file_and_extractor(self, temp_directory):
        """Test decorator behavior when both output_file and extractor are used."""
        output_file = temp_directory / "dual_output.json"
        extractor = FailureExtractor()
        extractor.clear()

        @extract_on_failure(output=str(output_file))
        def test_dual_output():
            raise KeyError("Dual output test")

        with pytest.raises(KeyError):
            test_dual_output()

        # Should write to file
        assert output_file.exists()

        # When output file is specified, failures go to file not singleton
        # So extractor should remain empty
        assert len(extractor.failures) == 0