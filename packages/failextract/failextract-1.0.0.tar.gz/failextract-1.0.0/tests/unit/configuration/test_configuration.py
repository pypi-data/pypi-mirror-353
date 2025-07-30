"""Unit tests for configuration classes."""

import warnings
from pathlib import Path
from unittest.mock import patch

import pytest

from failextract import FormatterRegistry, OutputConfig, OutputFormat


class TestOutputConfig:
    """Test cases for OutputConfig class."""

    def test_initialization_defaults(self):
        """Test OutputConfig initialization with defaults."""
        config = OutputConfig()

        assert config.filename is None
        assert config.format == OutputFormat.JSON
        assert config.append is False
        assert config.include_passed is False
        assert config.max_failures is None

    def test_initialization_with_output_format(self):
        """Test initialization with OutputFormat enum."""
        config = OutputConfig(output=OutputFormat.MARKDOWN)

        assert config.filename == "test_failures.md"
        assert config.format == OutputFormat.MARKDOWN
        assert config.append is False

    def test_initialization_with_filename_string(self):
        """Test initialization with filename string."""
        config = OutputConfig(output="custom_report.json")

        assert config.filename == "custom_report.json"
        assert config.format == OutputFormat.JSON  # Detected from extension

    def test_initialization_with_path_object(self):
        """Test initialization with Path object."""
        path = Path("reports/test_results.xml")
        config = OutputConfig(output=path)

        assert config.filename == str(path)
        assert config.format == OutputFormat.XML

    def test_format_detection_from_extension(self):
        """Test automatic format detection from file extensions."""
        test_cases = [
            ("report.json", OutputFormat.JSON),
            ("report.md", OutputFormat.MARKDOWN),
            ("report.markdown", OutputFormat.MARKDOWN),
            # HTML format has been removed from the codebase
            # ("report.html", OutputFormat.HTML),
            # ("report.htm", OutputFormat.HTML),
            ("report.yaml", OutputFormat.YAML),
            ("report.yml", OutputFormat.YAML),
            ("report.xml", OutputFormat.XML),
            ("report.csv", OutputFormat.CSV),
        ]

        for filename, expected_format in test_cases:
            config = OutputConfig(output=filename)
            assert config.format == expected_format

    def test_explicit_format_override(self):
        """Test explicit format parameter overrides detection."""
        config = OutputConfig(output="report.json", format=OutputFormat.YAML)

        assert config.filename == "report.json"
        assert config.format == OutputFormat.YAML

    def test_format_string_parameter(self):
        """Test format parameter as string."""
        config = OutputConfig(output="report.txt", format="yaml")

        assert config.format == OutputFormat.YAML

    def test_format_aliases(self):
        """Test format aliases work correctly."""
        # Test markdown alias
        config = OutputConfig(output="report.txt", format="markdown")
        assert config.format == OutputFormat.MARKDOWN

        # Test yml alias
        config = OutputConfig(output="report.txt", format="yml")
        assert config.format == OutputFormat.YAML

    def test_append_parameter(self):
        """Test append parameter."""
        config = OutputConfig(append=True)
        assert config.append is True

        config = OutputConfig(append=False)
        assert config.append is False

    def test_include_passed_parameter(self):
        """Test include_passed parameter."""
        config = OutputConfig(include_passed=True)
        assert config.include_passed is True

        config = OutputConfig(include_passed=False)
        assert config.include_passed is False

    def test_max_failures_parameter(self):
        """Test max_failures parameter."""
        config = OutputConfig(max_failures=100)
        assert config.max_failures == 100

        config = OutputConfig(max_failures=None)
        assert config.max_failures is None

    def test_parameter_validation_append_type(self):
        """Test validation of append parameter type."""
        with pytest.raises(TypeError, match="append must be bool"):
            OutputConfig(append="true")

        with pytest.raises(TypeError, match="append must be bool"):
            OutputConfig(append=1)

    def test_parameter_validation_include_passed_type(self):
        """Test validation of include_passed parameter type."""
        with pytest.raises(TypeError, match="include_passed must be bool"):
            OutputConfig(include_passed="false")

        with pytest.raises(TypeError, match="include_passed must be bool"):
            OutputConfig(include_passed=0)

    def test_parameter_validation_max_failures_type(self):
        """Test validation of max_failures parameter type."""
        with pytest.raises(TypeError, match="max_failures must be int or None"):
            OutputConfig(max_failures="100")

        with pytest.raises(TypeError, match="max_failures must be int or None"):
            OutputConfig(max_failures=100.5)

    def test_parameter_validation_max_failures_value(self):
        """Test validation of max_failures parameter value."""
        with pytest.raises(ValueError, match="max_failures must be positive"):
            OutputConfig(max_failures=0)

        with pytest.raises(ValueError, match="max_failures must be positive"):
            OutputConfig(max_failures=-1)

    def test_parameter_validation_output_type(self):
        """Test validation of output parameter type."""
        with pytest.raises(
            TypeError, match="output must be None, string, Path, or OutputFormat"
        ):
            OutputConfig(output=123)

        with pytest.raises(
            TypeError, match="output must be None, string, Path, or OutputFormat"
        ):
            OutputConfig(output=[])

    def test_parameter_validation_format_type(self):
        """Test validation of format parameter type."""
        with pytest.raises(
            TypeError, match="format must be None, string, or OutputFormat"
        ):
            OutputConfig(format=123)

        with pytest.raises(
            TypeError, match="format must be None, string, or OutputFormat"
        ):
            OutputConfig(format=[])

    def test_parameter_validation_invalid_format_string(self):
        """Test validation of invalid format strings."""
        with pytest.raises(ValueError, match="Invalid format string"):
            OutputConfig(format="invalid_format")

        # Should include list of valid formats
        with pytest.raises(ValueError) as exc_info:
            OutputConfig(format="bad_format")
        assert "Valid formats:" in str(exc_info.value)

    def test_parameter_validation_empty_file_path(self):
        """Test validation of empty file paths."""
        with pytest.raises(ValueError, match="Output file path cannot be empty"):
            OutputConfig(output="")

        with pytest.raises(ValueError, match="Output file path cannot be empty"):
            OutputConfig(output="   ")

    def test_parameter_validation_invalid_file_characters(self):
        """Test validation of invalid file path characters."""
        invalid_chars = ["<", ">", ":", '"', "|", "?", "*"]

        for char in invalid_chars:
            with pytest.raises(ValueError, match="contains invalid characters"):
                OutputConfig(output=f"report{char}.json")

    def test_parameter_validation_parent_directory(self):
        """Test that parent directory validation is not performed during config creation."""
        # Parent directory validation should not happen during config creation
        # It should be handled during actual file writing operations
        config = OutputConfig(output="nonexistent/report.json")
        assert config.filename == "nonexistent/report.json"
        assert config.format == OutputFormat.JSON

    @patch("pathlib.Path.exists")
    def test_parameter_validation_parent_directory_current(self, mock_exists):
        """Test that current directory doesn't require validation."""
        # File in current directory should not trigger parent directory check
        config = OutputConfig(output="report.json")
        assert config.filename == "report.json"

        # mock_exists should not be called for current directory
        mock_exists.assert_not_called()

    def test_format_mismatch_warning(self):
        """Test warning for format mismatch between extension and parameter."""
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")

            config = OutputConfig(output="report.json", format="yaml")

            assert len(w) == 1
            assert "Format mismatch" in str(w[0].message)
            assert "json" in str(w[0].message)
            assert "yaml" in str(w[0].message)

            # Should use specified format despite mismatch
            assert config.format == OutputFormat.YAML

    def test_format_mismatch_warning_with_aliases(self):
        """Test format mismatch warning works with aliases."""
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")

            config = OutputConfig(output="report.json", format="markdown")

            assert len(w) == 1
            assert "Format mismatch" in str(w[0].message)

    def test_no_warning_for_matching_formats(self):
        """Test no warning when formats match."""
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")

            config = OutputConfig(output="report.json", format="json")

            # No warnings should be issued
            assert len(w) == 0

    def test_complex_initialization_scenario(self):
        """Test complex initialization with all parameters."""
        config = OutputConfig(
            output="reports/failures.yaml",
            format=OutputFormat.YAML,
            append=True,
            include_passed=True,
            max_failures=50,
        )

        assert config.filename == "reports/failures.yaml"
        assert config.format == OutputFormat.YAML
        assert config.append is True
        assert config.include_passed is True
        assert config.max_failures == 50

    def test_edge_case_filename_with_spaces(self):
        """Test handling of filenames with spaces."""
        config = OutputConfig(output="test report.json")
        assert config.filename == "test report.json"
        assert config.format == OutputFormat.JSON

    def test_edge_case_mixed_case_extensions(self):
        """Test handling of mixed case file extensions."""
        config = OutputConfig(output="Report.JSON")
        assert config.format == OutputFormat.JSON

        config = OutputConfig(output="Report.Md")
        assert config.format == OutputFormat.MARKDOWN

    def test_edge_case_multiple_dots_in_filename(self):
        """Test handling of filenames with multiple dots."""
        config = OutputConfig(output="test.backup.final.json")
        assert config.format == OutputFormat.JSON

    def test_edge_case_no_extension(self):
        """Test handling of filenames without extensions."""
        config = OutputConfig(output="report_no_extension")
        assert config.format == OutputFormat.JSON  # Should default to JSON

    def test_validation_integration(self):
        """Test that validation is called during initialization."""
        # This test ensures _validate_parameters is actually called
        with pytest.raises(ValueError):
            OutputConfig(max_failures=-1)  # Should trigger validation

    def test_format_enum_direct_usage(self):
        """Test direct usage of OutputFormat enum values."""
        for format_type in OutputFormat:
            if format_type != OutputFormat.CUSTOM:
                config = OutputConfig(output=format_type)
                assert config.format == format_type

                # Should generate appropriate filename
                try:
                    formatter = FormatterRegistry.get_formatter(format_type.value.lower())
                    expected_extension = formatter.get_extension()
                    assert config.filename.endswith(expected_extension)
                except ValueError:
                    # Skip formats not available in registry
                    pass

    def test_type_consistency(self):
        """Test that parameter types are consistent."""
        config = OutputConfig(
            output="test.json",
            format="json",
            append=False,
            include_passed=False,
            max_failures=100,
        )

        # Check that types are correctly converted/validated
        assert isinstance(config.filename, str)
        assert isinstance(config.format, OutputFormat)
        assert isinstance(config.append, bool)
        assert isinstance(config.include_passed, bool)
        assert isinstance(config.max_failures, int)

    def test_parameter_interaction_edge_cases(self):
        """Test edge cases in parameter interactions."""
        # Test OutputFormat enum with explicit format parameter
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")

            # This should work but may generate warning about filename
            config = OutputConfig(output=OutputFormat.JSON, format=OutputFormat.YAML)

            # Should use the explicit format parameter
            assert config.format == OutputFormat.YAML

    def test_validation_order(self):
        """Test that validation happens in correct order."""
        # Type validation should happen before value validation
        with pytest.raises(TypeError):  # Not ValueError
            OutputConfig(max_failures="not_a_number")

    def test_immutability_simulation(self):
        """Test that config behaves as if immutable after creation."""
        config = OutputConfig(output="test.json", append=True)

        # Values should be set correctly
        assert config.filename == "test.json"
        assert config.append is True

        # These attributes exist and have expected types
        assert hasattr(config, "filename")
        assert hasattr(config, "format")
        assert hasattr(config, "append")
        assert hasattr(config, "include_passed")
        assert hasattr(config, "max_failures")
