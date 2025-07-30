"""Unit tests for FormatterRegistry functionality."""

import pytest

from failextract import (
    CSVFormatter,
    JSONFormatter,
    MarkdownFormatter,
    OutputFormatter,
    XMLFormatter,
    YAMLFormatter,
)
from failextract.core.formatters.base import OutputFormat
from failextract.core.formatters.registry import FormatterRegistry


class TestFormatterRegistry:
    """Test FormatterRegistry functionality."""

    def test_get_formatter_by_enum(self):
        """Test getting formatter by OutputFormat enum."""
        formatter = FormatterRegistry.get_formatter(OutputFormat.JSON)
        assert isinstance(formatter, JSONFormatter)

        formatter = FormatterRegistry.get_formatter(OutputFormat.MARKDOWN)
        assert isinstance(formatter, MarkdownFormatter)

    def test_get_formatter_by_string(self):
        """Test getting formatter by string name."""
        formatter = FormatterRegistry.get_formatter("json")
        assert isinstance(formatter, JSONFormatter)

        formatter = FormatterRegistry.get_formatter("markdown")
        assert isinstance(formatter, MarkdownFormatter)

        formatter = FormatterRegistry.get_formatter("md")
        assert isinstance(formatter, MarkdownFormatter)

    def test_get_formatter_by_extension(self):
        """Test getting formatter by file extension."""
        formatter = FormatterRegistry.get_formatter(".json")
        assert isinstance(formatter, JSONFormatter)

        formatter = FormatterRegistry.get_formatter(".md")
        assert isinstance(formatter, MarkdownFormatter)

        formatter = FormatterRegistry.get_formatter(".yaml")
        assert isinstance(formatter, YAMLFormatter)

        formatter = FormatterRegistry.get_formatter(".yml")
        assert isinstance(formatter, YAMLFormatter)

    def test_get_formatter_unknown_format(self):
        """Test error for unknown format."""
        with pytest.raises(ValueError, match="Unknown format type"):
            FormatterRegistry.get_formatter("unknown_format")

    def test_register_custom_formatter(self):
        """Test registering custom formatter."""

        class CustomFormatter(OutputFormatter):
            def format(self, failures):
                return "custom format"

            def get_extension(self):
                return ".custom"

        custom = CustomFormatter()
        FormatterRegistry.register_formatter(OutputFormat.CUSTOM, custom)

        formatter = FormatterRegistry.get_formatter(OutputFormat.CUSTOM)
        assert formatter is custom

    def test_detect_format_from_filename(self):
        """Test format detection from filename."""
        assert FormatterRegistry.detect_format("report.json") == OutputFormat.JSON
        assert FormatterRegistry.detect_format("report.md") == OutputFormat.MARKDOWN
        assert (
            FormatterRegistry.detect_format("report.markdown") == OutputFormat.MARKDOWN
        )
        assert FormatterRegistry.detect_format("report.yaml") == OutputFormat.YAML
        assert FormatterRegistry.detect_format("report.yml") == OutputFormat.YAML
        assert FormatterRegistry.detect_format("report.xml") == OutputFormat.XML
        assert FormatterRegistry.detect_format("report.csv") == OutputFormat.CSV

    def test_detect_format_unknown_extension(self):
        """Test format detection with unknown extension."""
        # Should default to JSON
        assert FormatterRegistry.detect_format("report.unknown") == OutputFormat.JSON
        assert FormatterRegistry.detect_format("no_extension") == OutputFormat.JSON

    def test_detect_format_case_insensitive(self):
        """Test format detection is case insensitive."""
        assert FormatterRegistry.detect_format("REPORT.JSON") == OutputFormat.JSON
        assert FormatterRegistry.detect_format("Report.Md") == OutputFormat.MARKDOWN

    def test_all_formatters_registered(self):
        """Test that all output formats have registered formatters."""
        for format_type in OutputFormat:
            if (
                format_type != OutputFormat.CUSTOM
            ):  # CUSTOM is for user-defined formatters
                formatter = FormatterRegistry.get_formatter(format_type)
                assert isinstance(formatter, OutputFormatter)

    def test_formatter_consistency(self):
        """Test that formatters are consistent across calls."""
        formatter1 = FormatterRegistry.get_formatter(OutputFormat.JSON)
        formatter2 = FormatterRegistry.get_formatter(OutputFormat.JSON)

        # Should be the same instance (registry reuses instances)
        assert formatter1 is formatter2