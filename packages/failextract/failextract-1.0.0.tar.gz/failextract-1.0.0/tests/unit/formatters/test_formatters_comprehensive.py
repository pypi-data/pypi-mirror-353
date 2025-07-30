"""Comprehensive formatter coverage tests targeting lines 439-502, 511-585, 676-760."""

from unittest.mock import patch

import pytest

from failextract import MarkdownFormatter, YAMLFormatter


class TestFormatterCoverage:
    """Comprehensive tests to achieve 70% coverage through formatter testing."""

    @pytest.fixture
    def basic_failure_data(self):
        """Basic failure data for testing."""
        return {
            "timestamp": "2025-12-03T12:00:00",
            "test_name": "test_example",
            "test_module": "test_module",
            "test_file": "/path/to/test_file.py",
            "test_source": "def test_example():\n    assert False",
            "test_args": "()",
            "test_kwargs": "{}",
            "exception_type": "ValueError",
            "exception_message": "Test error message",
            "exception_traceback": 'Traceback (most recent call last):\n  File "/path/to/test.py", line 2\n    assert False\nValueError: Test error message',
            "extracted_code": [
                {
                    "file": "/path/to/module.py",
                    "function": "failing_function",
                    "line": 42,
                    "source": 'def failing_function():\n    raise ValueError("Test error")',
                }
            ],
        }

    @pytest.fixture
    def complex_failure_data(self):
        """Complex failure data with fixtures and locals."""
        return {
            "timestamp": "2025-12-03T12:00:00",
            "test_name": "test_complex",
            "test_module": "test_complex_module",
            "test_file": "/path/to/complex_test.py",
            "test_source": 'def test_complex(fixture1):\n    local_var = "test"\n    assert False',
            "test_args": "()",
            "test_kwargs": "{}",
            "exception_type": "AssertionError",
            "exception_message": "Complex test failure",
            "exception_traceback": "Traceback...",
            "extracted_code": [],
            "fixtures": [
                {
                    "name": "fixture1",
                    "type": "function",
                    "scope": "function",
                    "source": '@pytest.fixture\ndef fixture1():\n    return "test_value"',
                }
            ],
            "local_variables": {"local_var": "test", "fixture1": "test_value"},
            "extracted_classes": [
                "class TestClass:\n    def method(self):\n        pass"
            ],
        }

    # ==================== MARKDOWN FORMATTER TESTS ====================
    # Targeting lines 439-502 (63 lines)

    def test_markdown_formatter_basic(self, basic_failure_data):
        """Test basic MarkdownFormatter functionality."""
        formatter = MarkdownFormatter()
        result = formatter.format([basic_failure_data])

        # Check header and metadata
        assert "# Test Failure Report" in result
        assert "Generated:" in result
        assert "Total Failures: 1" in result

        # Check failure content
        assert "## Failure 1: `test_example`" in result
        assert "**Module:** `test_module`" in result
        assert "**File:** `/path/to/test_file.py`" in result
        assert "**Time:** 2025-12-03T12:00:00" in result

    def test_markdown_formatter_table_of_contents(self, basic_failure_data):
        """Test MarkdownFormatter table of contents generation (>3 failures)."""
        # Create 4 failures to trigger table of contents
        failures = []
        for i in range(4):
            failure = basic_failure_data.copy()
            failure["test_name"] = f"test_example_{i}"
            failures.append(failure)

        formatter = MarkdownFormatter()
        result = formatter.format(failures)

        # Should include table of contents
        assert "## Table of Contents" in result
        assert "[Failure 1: test_example_0]" in result
        assert "[Failure 4: test_example_3]" in result

    def test_markdown_formatter_no_table_of_contents(self, basic_failure_data):
        """Test MarkdownFormatter with <=3 failures (no TOC)."""
        # Create only 2 failures
        failures = [basic_failure_data, basic_failure_data.copy()]

        formatter = MarkdownFormatter()
        result = formatter.format(failures)

        # Should NOT include table of contents
        assert "## Table of Contents" not in result

    def test_markdown_formatter_with_fixtures(self, complex_failure_data):
        """Test MarkdownFormatter with fixture data."""
        formatter = MarkdownFormatter()
        result = formatter.format([complex_failure_data])

        # Should include fixture information
        assert "### Fixtures" in result
        assert "fixture1" in result

    def test_markdown_formatter_with_complex_data(self, complex_failure_data):
        """Test MarkdownFormatter handles complex data gracefully."""
        formatter = MarkdownFormatter()
        result = formatter.format([complex_failure_data])

        # Should handle complex data without errors and include basic sections
        assert "### Test Code" in result
        assert "### Error Details" in result
        assert "test_complex" in result

    def test_markdown_formatter_traceback_details(self, complex_failure_data):
        """Test MarkdownFormatter traceback details section."""
        formatter = MarkdownFormatter()
        result = formatter.format([complex_failure_data])

        # Should include traceback details
        assert "<details>" in result
        assert "<summary>Full Traceback</summary>" in result
        assert "Traceback..." in result

    def test_markdown_formatter_extension(self):
        """Test MarkdownFormatter extension."""
        formatter = MarkdownFormatter()
        assert formatter.get_extension() == ".md"

    # ==================== HTML FORMATTER TESTS ====================
    # HTMLFormatter has been removed from the codebase
    # These tests are commented out to prevent import errors
    
    # def test_html_formatter_basic_structure(self, basic_failure_data):
    #     """Test HTMLFormatter basic HTML structure."""
    #     formatter = HTMLFormatter()
    #     result = formatter.format([basic_failure_data])
    #
    #     # Check HTML structure
    #     assert "<!DOCTYPE html>" in result
    #     assert "<html>" in result
    #     assert "<head>" in result
    #     assert "FailExtract" in result and "Test Failure" in result  # Enhanced title
    #     assert "<style>" in result
    #     assert "<body>" in result
    #     assert "</html>" in result
    #
    # def test_html_formatter_css_styling(self, basic_failure_data):
    #     """Test HTMLFormatter CSS styling inclusion."""
    #     formatter = HTMLFormatter()
    #     result = formatter.format([basic_failure_data])
    #
    #     # Check CSS styles (enhanced formatter uses external CSS)
    #     assert "tailwindcss" in result or "<style>" in result  # Has styling
    #     assert "background" in result or "bg-" in result  # Some styling present
    #
    # def test_html_formatter_failure_content(self, basic_failure_data):
    #     """Test HTMLFormatter failure content rendering."""
    #     formatter = HTMLFormatter()
    #     result = formatter.format([basic_failure_data])
    #
    #     # Check failure content (flexible for enhanced formatter)
    #     assert "test_example" in result  # Test name present
    #     assert "Failure" in result  # Failure indication
    #     assert "Test error message" in result  # Error message present
    #     assert "<strong>Module:</strong> <code>test_module</code>" in result
    #
    # def test_html_formatter_error_highlighting(self, basic_failure_data):
    #     """Test HTMLFormatter error highlighting."""
    #     formatter = HTMLFormatter()
    #     result = formatter.format([basic_failure_data])
    #
    #     # Check error styling (flexible for enhanced formatter)
    #     assert "Test error message" in result  # Error message present
    #     assert "ValueError" in result  # Exception type present
    #     assert "ValueError" in result
    #     assert "Test error message" in result
    #
    # def test_html_formatter_code_blocks(self, basic_failure_data):
    #     """Test HTMLFormatter code block rendering."""
    #     formatter = HTMLFormatter()
    #     result = formatter.format([basic_failure_data])
    #
    #     # Check code blocks (enhanced formatter may use different structure)
    #     assert "test_example" in result  # Test name present
    #     assert "ValueError" in result  # Exception type present
    #     assert "def test_example()" in result
    #     assert "</code></pre>" in result
    #
    # def test_html_formatter_with_fixtures(self, complex_failure_data):
    #     """Test HTMLFormatter with fixture data."""
    #     formatter = HTMLFormatter()
    #     result = formatter.format([complex_failure_data])
    #
    #     # Check fixture rendering (flexible for enhanced formatter)
    #     assert "fixture1" in result  # Fixture name present
    #     assert "function" in result  # Fixture type present
    #     # Enhanced formatter shows fixtures in modern UI
    #     # (No need for specific HTML tags - just verify fixture data is present)
    #     assert "fixture1" in result
    #
    # def test_html_formatter_multiple_failures(self, basic_failure_data):
    #     """Test HTMLFormatter with multiple failures."""
    #     failures = [basic_failure_data, basic_failure_data.copy()]
    #     formatter = HTMLFormatter()
    #     result = formatter.format(failures)
    #
    #     # Should have multiple failures (flexible count check)
    #     assert result.count("test_example") >= 2  # Multiple test names
    #     assert "2" in result  # Count appears somewhere
    #
    # def test_html_formatter_extension(self):
    #     """Test HTMLFormatter extension."""
    #     formatter = HTMLFormatter()
    #     assert formatter.get_extension() == ".html"

    # ==================== YAML FORMATTER TESTS ====================
    # Targeting lines 676-760 (84 lines)

    def test_yaml_formatter_basic_structure(self, basic_failure_data):
        """Test YAMLFormatter basic structure."""
        formatter = YAMLFormatter()
        result = formatter.format([basic_failure_data])

        # Check YAML structure
        assert "test_failure_report:" in result
        assert "metadata:" in result
        assert "generated:" in result
        assert "total_failures: 1" in result
        assert "failures:" in result

    def test_yaml_formatter_failure_data(self, basic_failure_data):
        """Test YAMLFormatter failure data structure."""
        formatter = YAMLFormatter()
        result = formatter.format([basic_failure_data])

        # Check failure data (using actual YAML structure)
        assert "name: test_example" in result
        assert "module: test_module" in result
        assert "type: ValueError" in result
        assert "message: Test error message" in result

    def test_yaml_formatter_with_fixtures(self, complex_failure_data):
        """Test YAMLFormatter with fixture data."""
        formatter = YAMLFormatter()
        result = formatter.format([complex_failure_data])

        # Check fixture data in YAML
        assert "fixtures:" in result
        assert "name: fixture1" in result
        assert "type: function" in result

    def test_yaml_formatter_import_error(self):
        """Test YAMLFormatter import error handling."""
        # Mock yaml import to raise ImportError
        with patch("builtins.__import__", side_effect=ImportError):
            formatter = YAMLFormatter()
            with pytest.raises(
                ImportError, match="PyYAML is required for YAML output format"
            ):
                formatter.format([])

    def test_yaml_formatter_multiple_failures(self, basic_failure_data):
        """Test YAMLFormatter with multiple failures."""
        failures = []
        for i in range(3):
            failure = basic_failure_data.copy()
            failure["test_name"] = f"test_{i}"
            failures.append(failure)

        formatter = YAMLFormatter()
        result = formatter.format(failures)

        # Check multiple failures structure (using actual YAML structure)
        assert "total_failures: 3" in result
        assert "name: test_0" in result
        assert "name: test_2" in result

    def test_yaml_formatter_extension(self):
        """Test YAMLFormatter extension."""
        formatter = YAMLFormatter()
        assert formatter.get_extension() == ".yaml"

    def test_yaml_formatter_empty_failures(self):
        """Test YAMLFormatter with empty failures list."""
        formatter = YAMLFormatter()
        result = formatter.format([])

        assert "total_failures: 0" in result
        assert "failures: []" in result

    # ==================== EDGE CASE TESTS ====================

    def test_formatters_basic_functionality_validation(self):
        """Test that all three main formatters produce valid output."""
        # Use basic test data that has all required fields
        basic_data = {
            "test_name": "test_validation",
            "test_module": "test_module",
            "test_file": "/path/to/test.py",
            "timestamp": "2025-12-03T12:00:00",
            "exception_type": "ValidationError",
            "exception_message": "Validation test",
            "exception_traceback": "Traceback...",
            "test_source": "def test_validation(): pass",
            "extracted_code": [],
        }

        # Test available formatters (HTMLFormatter removed)
        markdown_formatter = MarkdownFormatter()
        yaml_formatter = YAMLFormatter()

        markdown_result = markdown_formatter.format([basic_data])
        yaml_result = yaml_formatter.format([basic_data])

        # Basic validation that each formatter produces expected content
        assert "test_validation" in markdown_result
        assert "test_validation" in yaml_result
        assert len(markdown_result) > 50
        assert len(yaml_result) > 50
