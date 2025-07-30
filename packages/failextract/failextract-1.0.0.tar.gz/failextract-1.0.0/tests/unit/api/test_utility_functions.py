"""Unit tests for utility functions."""

import json
from pathlib import Path
from unittest.mock import Mock, mock_open, patch

import pytest

from failextract import (
    OutputConfig,
    OutputFormat,
    extract_failure_info,
    extract_function_source,
    extract_on_failure,
    generate_session_report,
    save_failure_report,
    save_single_failure,
    save_with_config,
)


class TestExtractFailureInfo:
    """Test cases for extract_failure_info function."""

    def test_basic_failure_extraction(self, mock_test_function, sample_failure_data):
        """Test basic failure information extraction."""
        exception = ValueError("Test error")

        with patch("inspect.getsource", return_value="def test_func(): pass"):
            with patch("inspect.getfile", return_value="/path/to/test.py"):
                result = extract_failure_info(mock_test_function, exception, (), {})

        # Check basic structure
        assert "timestamp" in result
        assert "test_name" in result
        assert "test_module" in result
        assert "test_file" in result
        assert "test_source" in result
        assert "exception_type" in result
        assert "exception_message" in result
        assert "exception_traceback" in result
        assert "extracted_code" in result

        # Check content
        assert result["test_name"] == mock_test_function.__name__
        assert result["test_module"] == mock_test_function.__module__
        assert result["exception_type"] == "ValueError"
        assert result["exception_message"] == "Test error"

    def test_failure_extraction_with_fixtures(self, mock_test_function):
        """Test failure extraction including fixtures."""
        exception = RuntimeError("Fixture test")
        frame_locals = {"fixture_var": "test_value"}

        with patch("inspect.getsource"), patch("inspect.getfile"):
            with patch(
                "failextract.failextract.FixtureExtractor"
            ) as mock_extractor_class:
                mock_extractor = Mock()
                mock_extractor.get_fixture_info.return_value = [
                    {"name": "test_fixture", "type": "custom"}
                ]
                mock_extractor_class.return_value = mock_extractor

                result = extract_failure_info(
                    mock_test_function,
                    exception,
                    (),
                    {},
                    frame_locals=frame_locals,
                    include_fixtures=True,
                )

        assert "fixtures" in result
        assert len(result["fixtures"]) == 1
        assert result["fixtures"][0]["name"] == "test_fixture"

    def test_failure_extraction_without_fixtures(self, mock_test_function):
        """Test failure extraction without fixtures."""
        exception = RuntimeError("No fixtures test")

        with patch("inspect.getsource"), patch("inspect.getfile"):
            result = extract_failure_info(
                mock_test_function, exception, (), {}, include_fixtures=False
            )

        assert "fixtures" not in result

    def test_failure_extraction_with_locals(self, mock_test_function):
        """Test failure extraction including local variables."""
        exception = RuntimeError("Locals test")

        # Create a real traceback by raising and catching an exception
        try:

            def test_function():
                local_var = "test_value"
                json_serializable = 42
                non_serializable = Mock()  # This should be converted to string
                raise RuntimeError("Locals test")

            test_function()
        except RuntimeError as e:
            # Use the real traceback
            exception.__traceback__ = e.__traceback__

        with patch("inspect.getsource"), patch("inspect.getfile"):
            with patch(
                "failextract.extract_function_source",
                return_value="def test_func(): pass",
            ):
                result = extract_failure_info(
                    mock_test_function,
                    exception,
                    (),
                    {},
                    include_locals=True,
                    skip_stdlib=False,  # Don't skip to ensure frame is processed
                )

        # Should have extracted code with locals
        assert len(result["extracted_code"]) > 0

        # Find the frame with the test_function locals
        found_locals = False
        for code_info in result["extracted_code"]:
            if "locals" in code_info:
                locals_data = code_info["locals"]
                if "local_var" in locals_data:
                    assert locals_data["local_var"] == "test_value"
                    assert locals_data["json_serializable"] == 42
                    found_locals = True
                    break

        assert found_locals, "Should find locals in extracted code"

    def test_failure_extraction_skip_stdlib(self, mock_test_function):
        """Test skipping standard library modules."""
        exception = RuntimeError("Stdlib test")

        # Create a real traceback from stdlib-like location by importing a stdlib module
        import json

        try:
            # This will create a traceback in a stdlib location
            json.loads("invalid json")
        except json.JSONDecodeError as e:
            exception.__traceback__ = e.__traceback__

        with patch("inspect.getsource"), patch("inspect.getfile"):
            result = extract_failure_info(
                mock_test_function, exception, (), {}, skip_stdlib=True
            )

        # Should skip stdlib frame - or at least have fewer frames than without skip_stdlib
        result_no_skip = extract_failure_info(
            mock_test_function, exception, (), {}, skip_stdlib=False
        )

        # With skip_stdlib=True should have fewer or equal frames
        assert len(result["extracted_code"]) <= len(result_no_skip["extracted_code"])

    def test_failure_extraction_max_depth(self, mock_test_function):
        """Test max depth limitation."""
        exception = RuntimeError("Depth test")

        # Create a deep call stack to get a real traceback chain
        def func5():
            raise RuntimeError("Depth test")

        def func4():
            func5()

        def func3():
            func4()

        def func2():
            func3()

        def func1():
            func2()

        def func0():
            func1()

        try:
            func0()
        except RuntimeError as e:
            exception.__traceback__ = e.__traceback__

        with patch("inspect.getsource"), patch("inspect.getfile"):
            with patch(
                "failextract.extract_function_source", return_value="def func(): pass"
            ):
                result = extract_failure_info(
                    mock_test_function,
                    exception,
                    (),
                    {},
                    max_depth=3,
                    skip_stdlib=False,
                )

        # Should limit to max_depth
        assert len(result["extracted_code"]) <= 3

    def test_failure_extraction_class_methods(self, mock_test_function):
        """Test extraction of class source for methods."""
        exception = RuntimeError("Class test")

        # Create a real class method exception
        class TestClass:
            def test_method(self):
                raise RuntimeError("Class test")

        try:
            TestClass().test_method()
        except RuntimeError as e:
            exception.__traceback__ = e.__traceback__

        with patch("inspect.getsource") as mock_getsource:
            with patch("inspect.getfile"):
                # Mock class source extraction
                mock_getsource.side_effect = [
                    "def test_func(): pass",  # For test function
                    "def test_method(self): pass",  # For extracted function
                    "class TestClass:\n    def test_method(self): pass",  # For class
                ]

                result = extract_failure_info(
                    mock_test_function,
                    exception,
                    (),
                    {},
                    extract_classes=True,
                    skip_stdlib=False,
                )

        # Should extract class source
        assert len(result["extracted_code"]) > 0
        code_info = result["extracted_code"][0]
        assert "class_source" in code_info

    def test_failure_extraction_args_kwargs(self, mock_test_function):
        """Test extraction of test arguments."""
        exception = RuntimeError("Args test")
        test_args = (1, 2, "test")
        test_kwargs = {"param": "value", "number": 42}

        with patch("inspect.getsource"), patch("inspect.getfile"):
            result = extract_failure_info(
                mock_test_function, exception, test_args, test_kwargs
            )

        assert result["test_args"] == repr(test_args)
        assert result["test_kwargs"] == repr(test_kwargs)


class TestExtractFunctionSource:
    """Test cases for extract_function_source function."""

    def test_extract_from_frame_locals(self):
        """Test extracting function source from frame locals."""

        def sample_function():
            """Sample function for testing."""
            return "test"

        mock_frame = Mock()
        mock_frame.f_code.co_name = "sample_function"
        mock_frame.f_locals = {"sample_function": sample_function}
        mock_frame.f_globals = {}

        with patch(
            "inspect.getsource",
            return_value='def sample_function():\n    return "test"',
        ):
            result = extract_function_source(mock_frame)

        assert result == 'def sample_function():\n    return "test"'

    def test_extract_from_frame_globals(self):
        """Test extracting function source from frame globals."""

        def global_function():
            pass

        mock_frame = Mock()
        mock_frame.f_code.co_name = "global_function"
        mock_frame.f_locals = {}
        mock_frame.f_globals = {"global_function": global_function}

        with patch("inspect.getsource", return_value="def global_function(): pass"):
            result = extract_function_source(mock_frame)

        assert result == "def global_function(): pass"

    def test_extract_with_ast_parsing(self):
        """Test extracting function source using AST parsing."""
        mock_frame = Mock()
        mock_frame.f_code.co_name = "test_function"
        mock_frame.f_code.co_filename = "/path/to/test.py"
        mock_frame.f_lineno = 5
        mock_frame.f_locals = {}
        mock_frame.f_globals = {}

        source_code = """
def other_function():
    pass

def test_function():
    # This is the target function
    return "test"

def another_function():
    pass
"""

        with patch("pathlib.Path.exists", return_value=True):
            with patch("builtins.open", mock_open(read_data=source_code)):
                with patch("ast.parse") as mock_parse:
                    # Create a real FunctionDef node
                    import ast

                    mock_node = ast.FunctionDef(
                        name="test_function",
                        args=ast.arguments(
                            posonlyargs=[],
                            args=[],
                            vararg=None,
                            kwonlyargs=[],
                            kw_defaults=[],
                            kwarg=None,
                            defaults=[],
                        ),
                        body=[ast.Return(value=ast.Constant(value="test"))],
                        decorator_list=[],
                        returns=None,
                        lineno=5,
                        end_lineno=7,
                    )

                    mock_tree = Mock()
                    mock_parse.return_value = mock_tree

                    # Mock ast.walk to return our function node
                    with patch("ast.walk", return_value=[mock_node]):
                        result = extract_function_source(mock_frame)

        # Should extract the function lines
        assert result is not None

    def test_extract_nonexistent_file(self):
        """Test handling of non-existent source files."""
        mock_frame = Mock()
        mock_frame.f_code.co_name = "test_function"
        mock_frame.f_code.co_filename = "/nonexistent/file.py"
        mock_frame.f_locals = {}
        mock_frame.f_globals = {}

        with patch("pathlib.Path.exists", return_value=False):
            result = extract_function_source(mock_frame)

        assert result is None

    def test_extract_built_in_file(self):
        """Test handling of built-in or special files."""
        mock_frame = Mock()
        mock_frame.f_code.co_name = "built_in_function"
        mock_frame.f_code.co_filename = "<built-in>"
        mock_frame.f_locals = {}
        mock_frame.f_globals = {}

        result = extract_function_source(mock_frame)
        assert result is None

    def test_extract_with_exception(self):
        """Test graceful handling of exceptions during extraction."""
        mock_frame = Mock()
        mock_frame.f_code.co_name = "problematic_function"
        mock_frame.f_locals = {}
        mock_frame.f_globals = {}

        # Force an exception during processing
        with patch("inspect.getsource", side_effect=Exception("Source error")):
            result = extract_function_source(mock_frame)

        assert result is None


class TestSaveSingleFailure:
    """Test cases for save_single_failure function."""

    def test_save_to_new_file(self, sample_failure_data, temp_output_file):
        """Test saving to a new file."""
        # Ensure file doesn't exist
        Path(temp_output_file).unlink(missing_ok=True)

        save_single_failure(sample_failure_data, temp_output_file)

        # Verify file was created and contains data
        assert Path(temp_output_file).exists()

        with open(temp_output_file, "r") as f:
            data = json.load(f)

        assert len(data) == 1
        assert data[0] == sample_failure_data

    def test_save_append_to_existing_file(self, sample_failure_data, temp_output_file):
        """Test appending to existing file."""
        # Create initial data
        initial_data = [{"test_name": "existing_test"}]
        with open(temp_output_file, "w") as f:
            json.dump(initial_data, f)

        # Append new failure
        save_single_failure(sample_failure_data, temp_output_file)

        # Verify both entries exist
        with open(temp_output_file, "r") as f:
            data = json.load(f)

        assert len(data) == 2
        assert data[0] == initial_data[0]
        assert data[1] == sample_failure_data

    def test_save_error_handling(self, sample_failure_data):
        """Test error handling for invalid file paths."""
        # Try to save to invalid path
        with pytest.raises((OSError, PermissionError)):
            save_single_failure(sample_failure_data, "/invalid/path/file.json")


class TestSaveFailureReport:
    """Test cases for save_failure_report function."""

    def test_save_json_report(
        self, clean_extractor, sample_failure_data, temp_output_file
    ):
        """Test saving JSON report."""
        extractor = clean_extractor
        extractor.add_failure(sample_failure_data)

        save_failure_report(temp_output_file, "json")

        assert Path(temp_output_file).exists()
        with open(temp_output_file, "r") as f:
            data = json.load(f)
        assert len(data) == 1

    def test_save_markdown_report(
        self, clean_extractor, sample_failure_data, temp_directory
    ):
        """Test saving Markdown report."""
        extractor = clean_extractor
        extractor.add_failure(sample_failure_data)

        md_file = temp_directory / "report.md"
        save_failure_report(str(md_file), "markdown")

        assert md_file.exists()
        content = md_file.read_text()
        assert "# Test Failure Report" in content

    def test_save_report_format_alias(
        self, clean_extractor, sample_failure_data, temp_directory
    ):
        """Test saving with format alias."""
        extractor = clean_extractor
        extractor.add_failure(sample_failure_data)

        md_file = temp_directory / "report.md"
        save_failure_report(str(md_file), "md")  # Using alias

        assert md_file.exists()


class TestExtractOnFailureDecorator:
    """Test cases for extract_on_failure decorator."""

    def test_decorator_basic_usage(self, temp_output_file):
        """Test basic decorator usage."""

        @extract_on_failure(temp_output_file)
        def test_function():
            raise ValueError("Test error")

        # Test function should still raise the exception
        with pytest.raises(ValueError, match="Test error"):
            test_function()

        # But failure should be saved
        assert Path(temp_output_file).exists()

    def test_decorator_without_arguments(self, clean_extractor):
        """Test decorator without arguments (uses global collection)."""

        @extract_on_failure
        def test_function():
            raise RuntimeError("Global collection test")

        extractor = clean_extractor
        initial_count = len(extractor.failures)

        with pytest.raises(RuntimeError):
            test_function()

        # Should add to global collection
        assert len(extractor.failures) == initial_count + 1

    def test_decorator_with_output_config(self, temp_output_file):
        """Test decorator with OutputConfig object."""
        config = OutputConfig(temp_output_file, OutputFormat.JSON)

        @extract_on_failure(config)
        def test_function():
            raise ValueError("Config test")

        with pytest.raises(ValueError):
            test_function()

        assert Path(temp_output_file).exists()

    def test_decorator_preserves_function_metadata(self):
        """Test that decorator preserves function metadata."""

        @extract_on_failure
        def test_function_with_metadata():
            """Test function docstring."""
            return "success"

        # Should preserve function name and docstring
        assert test_function_with_metadata.__name__ == "test_function_with_metadata"
        assert test_function_with_metadata.__doc__ == "Test function docstring."

        # Should add extraction marker
        assert hasattr(test_function_with_metadata, "_extract_on_failure")
        assert test_function_with_metadata._extract_on_failure is True

    def test_decorator_successful_execution(self):
        """Test decorator with successful function execution."""

        @extract_on_failure
        def successful_test():
            return "success"

        # Should not raise exception and return value
        result = successful_test()
        assert result == "success"

    def test_decorator_with_passed_tracking(self, clean_extractor):
        """Test decorator with passed test tracking."""
        config = OutputConfig(include_passed=True)

        @extract_on_failure(config)
        def passing_test():
            return "passed"

        extractor = clean_extractor
        initial_passed = len(extractor.passed)

        result = passing_test()

        assert result == "passed"
        assert len(extractor.passed) == initial_passed + 1


class TestSaveWithConfig:
    """Test cases for save_with_config function."""

    def test_save_with_json_config(self, sample_failure_data, temp_output_file):
        """Test saving with JSON configuration."""
        config = OutputConfig(temp_output_file, OutputFormat.JSON)
        save_with_config(sample_failure_data, config)

        assert Path(temp_output_file).exists()
        with open(temp_output_file, "r") as f:
            data = json.load(f)
        assert len(data) == 1

    def test_save_with_append_config(self, sample_failure_data, temp_output_file):
        """Test saving with append configuration."""
        # Create initial file
        initial_data = [{"test": "existing"}]
        with open(temp_output_file, "w") as f:
            json.dump(initial_data, f)

        config = OutputConfig(temp_output_file, OutputFormat.JSON, append=True)
        save_with_config(sample_failure_data, config)

        with open(temp_output_file, "r") as f:
            data = json.load(f)
        assert len(data) == 2


class TestGenerateSessionReport:
    """Test cases for generate_session_report function."""

    def test_generate_session_report_with_failures(
        self, clean_extractor, sample_failure_data, temp_directory
    ):
        """Test generating session report with failures."""
        extractor = clean_extractor
        extractor.add_failure(sample_failure_data)

        report_file = temp_directory / "session_report.md"
        generate_session_report(str(report_file), "markdown")

        assert report_file.exists()
        content = report_file.read_text()
        assert "Test Failure Report" in content

    def test_generate_session_report_no_failures(self, clean_extractor, temp_directory):
        """Test generating session report with no failures."""
        extractor = clean_extractor
        extractor.clear()  # Ensure no failures

        report_file = temp_directory / "empty_report.md"
        generate_session_report(str(report_file), "markdown")

        # File should not be created if no failures
        assert not report_file.exists()

    def test_generate_session_report_with_clear(
        self, clean_extractor, sample_failure_data, temp_directory
    ):
        """Test that generate_session_report clears data by default."""
        extractor = clean_extractor
        extractor.add_failure(sample_failure_data)

        initial_count = len(extractor.failures)
        assert initial_count > 0

        report_file = temp_directory / "clear_test.md"
        generate_session_report(str(report_file), "markdown", clear=True)

        # Data should be cleared
        assert len(extractor.failures) == 0

    def test_generate_session_report_without_clear(
        self, clean_extractor, sample_failure_data, temp_directory
    ):
        """Test that generate_session_report can preserve data."""
        extractor = clean_extractor
        extractor.add_failure(sample_failure_data)

        initial_count = len(extractor.failures)

        report_file = temp_directory / "no_clear_test.md"
        generate_session_report(str(report_file), "markdown", clear=False)

        # Data should be preserved
        assert len(extractor.failures) == initial_count
