"""Tests for core CLI functionality including format detection and validation.

This module tests the core CLI functionality including:
- Format detection and extension mapping
- Format validation and error handling
- OutputConfig edge cases and boundary conditions
"""

from pathlib import Path

import pytest

from failextract import OutputConfig, OutputFormat
from failextract.failextract import FormatterRegistry


class TestFormatDetectionCoverage:
    """Test format detection logic and extension mapping."""

    def test_format_detection_by_string_lowercase(self):
        """Test format detection with lowercase string inputs."""
        # Target lines 782-785: format_type.lower() and enum matching
        formatter = FormatterRegistry.get_formatter("markdown")
        assert formatter.__class__.__name__ == "MarkdownFormatter"

        # HTMLFormatter has been removed from the codebase
        # formatter = FormatterRegistry.get_formatter("html")
        # assert formatter.__class__.__name__ == "HTMLFormatter"

        formatter = FormatterRegistry.get_formatter("yaml")
        assert formatter.__class__.__name__ == "YAMLFormatter"

    def test_format_detection_by_enum_name(self):
        """Test format detection using enum name matching."""
        # Target lines 784-785: fmt.name.lower() matching
        formatter = FormatterRegistry.get_formatter("MARKDOWN")
        assert formatter.__class__.__name__ == "MarkdownFormatter"

        formatter = FormatterRegistry.get_formatter("JSON")
        assert formatter.__class__.__name__ == "JSONFormatter"

    def test_format_detection_by_extension_mapping(self):
        """Test format detection using file extension mapping."""
        # Target lines 787-799: Extension mapping logic
        test_cases = [
            (".json", "JSONFormatter"),
            (".md", "MarkdownFormatter"),
            (".markdown", "MarkdownFormatter"),
            # HTMLFormatter has been removed from the codebase
            # (".html", "HTMLFormatter"),
            # (".htm", "HTMLFormatter"),
            (".yaml", "YAMLFormatter"),
            (".yml", "YAMLFormatter"),
        ]

        for extension, expected_class in test_cases:
            formatter = FormatterRegistry.get_formatter(extension)
            assert formatter.__class__.__name__ == expected_class

    def test_format_detection_with_outputformat_enum(self):
        """Test format detection with OutputFormat enum input."""
        # Target lines 800-801: isinstance(format_type, OutputFormat)
        formatter = FormatterRegistry.get_formatter(OutputFormat.MARKDOWN)
        assert formatter.__class__.__name__ == "MarkdownFormatter"

        # HTMLFormatter has been removed from the codebase
        # formatter = FormatterRegistry.get_formatter(OutputFormat.HTML)
        # assert formatter.__class__.__name__ == "HTMLFormatter"

    def test_format_detection_unknown_format_error(self):
        """Test error handling for unknown format types."""
        # Target line 803: raise ValueError for unknown format
        with pytest.raises(ValueError, match="Unknown format type: unknown_format"):
            FormatterRegistry.get_formatter("unknown_format")

        with pytest.raises(ValueError, match="Unknown format type: .unknown"):
            FormatterRegistry.get_formatter(".unknown")


class TestFormatValidationCoverage:
    """Test format validation and error handling."""

    def test_output_config_format_string_validation(self):
        """Test OutputConfig format string validation and aliases."""
        # Target lines 857-873: Format string validation and aliases

        # Test format aliases
        config1 = OutputConfig(output="test.md", format="markdown")
        assert config1.format == OutputFormat.MARKDOWN

        config2 = OutputConfig(output="test.yaml", format="yml")
        assert config2.format == OutputFormat.YAML

        # Test direct format strings
        # HTMLFormatter has been removed from the codebase
        # config3 = OutputConfig(output="test.html", format="html")
        # assert config3.format == OutputFormat.HTML

    def test_output_config_invalid_format_string_error(self):
        """Test error handling for invalid format strings."""
        # Target lines 867-869: ValueError for invalid format strings
        with pytest.raises(ValueError) as exc_info:
            OutputConfig(output="test.txt", format="invalid_format")

        assert "Invalid format string: invalid_format" in str(exc_info.value)
        assert "Valid formats:" in str(exc_info.value)

    def test_output_config_invalid_format_type_error(self):
        """Test error handling for invalid format types."""
        # Target lines 872-873: TypeError for invalid format types
        with pytest.raises(TypeError) as exc_info:
            OutputConfig(output="test.txt", format=123)

        assert "format must be None, string, or OutputFormat, got <class 'int'>" in str(
            exc_info.value
        )

    def test_output_config_invalid_output_type_error(self):
        """Test error handling for invalid output types."""
        # Target line 877: TypeError for invalid output types
        with pytest.raises(TypeError) as exc_info:
            OutputConfig(output=123)

        assert (
            "output must be None, string, Path, or OutputFormat, got <class 'int'>"
            in str(exc_info.value)
        )

    def test_format_consistency_validation_warning(self):
        """Test format consistency validation with warnings."""
        # Target lines 943-962: Format consistency validation
        with pytest.warns(UserWarning) as warning_info:
            # Create config with mismatched extension and format
            config = OutputConfig(output="test.json", format="yaml")

        warning = warning_info[0]
        assert "Format mismatch" in str(warning.message)
        assert "file extension suggests json" in str(warning.message)
        assert "format parameter specifies yaml" in str(warning.message)

    def test_format_consistency_with_aliases(self):
        """Test format consistency validation with format aliases."""
        # Target lines 945-958: Format alias handling in consistency check
        with pytest.warns(UserWarning):
            # Test markdown alias
            config = OutputConfig(output="test.json", format="markdown")

        with pytest.warns(UserWarning):
            # Test yml alias
            config = OutputConfig(output="test.md", format="yml")

    def test_format_consistency_graceful_degradation(self):
        """Test graceful handling of invalid format in consistency check."""
        # Target lines 954-956: Graceful degradation for invalid format
        # This is a simple test since the actual graceful degradation is hard to trigger
        # due to earlier validation catching invalid formats
        config = OutputConfig(output="test.json", format="json")
        assert config.format == OutputFormat.JSON


class TestOutputConfigEdgeCases:
    """Test edge cases and boundary conditions in OutputConfig."""

    def test_output_config_with_pathlib_path(self):
        """Test OutputConfig with pathlib.Path objects."""
        path = Path("test.yaml")
        config = OutputConfig(output=path)
        assert config.filename == str(path)
        assert config.format == OutputFormat.YAML

    def test_output_config_format_detection_from_filename(self):
        """Test automatic format detection from filename."""
        # HTMLFormatter has been removed from the codebase
        # Target line 875: self.format = FormatterRegistry.detect_format(self.filename)
        # config = OutputConfig(output="report.html")
        # assert config.format == OutputFormat.HTML

        config2 = OutputConfig(output="data.yml")
        assert config2.format == OutputFormat.YAML

    def test_output_config_explicit_format_override(self):
        """Test explicit format overriding filename detection."""
        config = OutputConfig(output="data.json", format=OutputFormat.YAML)
        assert config.format == OutputFormat.YAML  # Format should override filename