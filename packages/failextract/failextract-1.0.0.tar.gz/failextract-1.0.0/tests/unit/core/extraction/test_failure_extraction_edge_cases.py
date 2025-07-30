"""Edge case tests for failure extraction functionality."""

import ast
from unittest.mock import Mock, mock_open, patch

import pytest

from failextract import extract_failure_info, extract_function_source


class TestFailureExtractionEdgeCases:
    """Test edge cases for failure extraction functionality."""

    def test_extract_failure_info_edge_cases(self):
        """Test extract_failure_info edge cases."""

        def test_func():
            pass

        exception = ValueError("Test error")

        # Test with extract_classes=True but no self in frame
        with patch("inspect.getsource"), patch("inspect.getfile"):
            result = extract_failure_info(
                test_func, exception, (), {}, extract_classes=True
            )
            assert "extracted_code" in result

        # Test with include_locals=True using a simpler approach
        with patch("inspect.getsource"), patch("inspect.getfile"):
            with patch(
                "failextract.extract_function_source", return_value="def test(): pass"
            ):
                result = extract_failure_info(
                    test_func, exception, (), {}, include_locals=True, skip_stdlib=False
                )
                assert "extracted_code" in result
                # Verify the result has expected structure
                assert isinstance(result.get("extracted_code", []), list)

    def test_extract_function_source_edge_cases(self):
        """Test extract_function_source edge cases."""

        # Test with function in locals
        def sample_func():
            pass

        mock_frame = Mock()
        mock_frame.f_code.co_name = "sample_func"
        mock_frame.f_locals = {"sample_func": sample_func}
        mock_frame.f_globals = {}

        with patch("inspect.getsource", return_value="def sample_func(): pass"):
            result = extract_function_source(mock_frame)
            assert result == "def sample_func(): pass"

        # Test with function in globals
        mock_frame.f_locals = {}
        mock_frame.f_globals = {"sample_func": sample_func}

        with patch("inspect.getsource", return_value="def sample_func(): pass"):
            result = extract_function_source(mock_frame)
            assert result == "def sample_func(): pass"

    def test_ast_parsing_edge_cases(self):
        """Test AST parsing edge cases."""
        mock_frame = Mock()
        mock_frame.f_code.co_name = "test_function"
        mock_frame.f_code.co_filename = "/test.py"
        mock_frame.f_lineno = 5
        mock_frame.f_locals = {}
        mock_frame.f_globals = {}

        source_code = """
def test_function():
    pass

class TestClass:
    def method(self):
        pass
"""

        with patch("pathlib.Path.exists", return_value=True):
            with patch("builtins.open", mock_open(read_data=source_code)):
                # Test when AST parsing fails
                with patch("ast.parse", side_effect=SyntaxError("Invalid syntax")):
                    result = extract_function_source(mock_frame)
                    assert result is None