"""Unit tests for MarkdownFormatter implementation."""

import pytest

from failextract import MarkdownFormatter, OutputFormatter


class TestMarkdownFormatter:
    """Test MarkdownFormatter implementation."""

    def test_initialization(self):
        """Test MarkdownFormatter initialization."""
        formatter = MarkdownFormatter()
        assert isinstance(formatter, OutputFormatter)

    def test_get_extension(self):
        """Test Markdown file extension."""
        formatter = MarkdownFormatter()
        assert formatter.get_extension() == ".md"

    def test_format_empty_list(self):
        """Test formatting empty failure list."""
        formatter = MarkdownFormatter()
        result = formatter.format([])

        # Should contain header and metadata
        assert "# Test Failure Report" in result
        assert "Total Failures: 0" in result
        assert "Generated:" in result

    def test_format_single_failure(self, sample_failure_data):
        """Test formatting single failure."""
        formatter = MarkdownFormatter()
        result = formatter.format([sample_failure_data])

        # Check structure
        assert "# Test Failure Report" in result
        assert "Total Failures: 1" in result
        assert f"## Failure 1: `{sample_failure_data['test_name']}`" in result
        assert "### Test Code" in result
        assert "### Error Details" in result

        # Check content
        assert sample_failure_data["test_name"] in result
        assert sample_failure_data["exception_type"] in result
        assert sample_failure_data["exception_message"] in result

    def test_format_with_fixtures(self):
        """Test formatting failure with fixtures."""
        formatter = MarkdownFormatter()

        failure_data = {
            "test_name": "test_with_fixtures",
            "test_module": "test_module",
            "test_file": "/path/to/test.py",
            "timestamp": "2024-01-01T12:00:00",
            "test_source": "def test_with_fixtures(tmp_path):\n    pass",
            "exception_type": "AssertionError",
            "exception_message": "Test failed",
            "extracted_code": [],
            "fixtures": [
                {
                    "name": "tmp_path",
                    "type": "builtin",
                    "description": "Temporary directory",
                },
                {
                    "name": "custom_fixture",
                    "type": "fixture",
                    "scope": "function",
                    "file": "/path/to/conftest.py",
                    "dependencies": ["request"],
                    "source": '@pytest.fixture\ndef custom_fixture():\n    return "value"',
                },
            ],
        }

        result = formatter.format([failure_data])

        # Should contain fixtures section
        assert "### Fixtures Used" in result
        assert "`tmp_path` (built-in)" in result
        assert "Temporary directory" in result
        assert "`custom_fixture` (scope: function)" in result
        assert "**Dependencies:** `request`" in result

    def test_format_with_extracted_code(self, sample_failure_data):
        """Test formatting with extracted code."""
        formatter = MarkdownFormatter()
        result = formatter.format([sample_failure_data])

        # Should contain tested code section
        assert "### Tested Code" in result

        # Check extracted code details
        for code in sample_failure_data["extracted_code"]:
            assert f"`{code['file']}`" in result
            assert f"`{code['function']}()`" in result
            assert f"line {code['line']}" in result

    def test_format_with_table_of_contents(self, multiple_failure_data):
        """Test table of contents generation for multiple failures."""
        formatter = MarkdownFormatter()
        result = formatter.format(multiple_failure_data)

        # Should have table of contents for multiple failures
        assert "## Table of Contents" in result

        for i, failure in enumerate(multiple_failure_data, 1):
            test_name = failure["test_name"]
            link_text = f"- [Failure {i}: {test_name}]"
            assert link_text in result

    def test_format_traceback_details(self, sample_failure_data):
        """Test traceback formatting in details section."""
        formatter = MarkdownFormatter()
        result = formatter.format([sample_failure_data])

        # Should have collapsible traceback
        assert "<details>" in result
        assert "<summary>Full Traceback</summary>" in result
        assert sample_failure_data["exception_traceback"] in result