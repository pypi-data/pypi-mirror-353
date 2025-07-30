"""Unit tests for CSVFormatter implementation."""

import pytest

from failextract import CSVFormatter, OutputFormatter


class TestCSVFormatter:
    """Test CSVFormatter implementation."""

    def test_initialization(self):
        """Test CSVFormatter initialization."""
        formatter = CSVFormatter()
        assert isinstance(formatter, OutputFormatter)

    def test_get_extension(self):
        """Test CSV file extension."""
        formatter = CSVFormatter()
        assert formatter.get_extension() == ".csv"

    def test_format_empty_list(self):
        """Test formatting empty failure list."""
        formatter = CSVFormatter()
        result = formatter.format([])

        # Should have header row only
        lines = result.strip().split("\n")
        assert len(lines) == 1
        assert "Test Name,Module,File,Timestamp" in lines[0]

    def test_format_single_failure(self, sample_failure_data):
        """Test formatting single failure."""
        formatter = CSVFormatter()
        result = formatter.format([sample_failure_data])

        lines = result.strip().split("\n")
        assert len(lines) == 2  # Header + 1 data row

        # Check header
        header = lines[0]
        assert "Test Name" in header
        assert "Exception Type" in header

        # Check data row
        data_row = lines[1]
        assert sample_failure_data["test_name"] in data_row
        assert sample_failure_data["exception_type"] in data_row

    def test_format_multiple_failures(self, multiple_failure_data):
        """Test formatting multiple failures."""
        formatter = CSVFormatter()
        result = formatter.format(multiple_failure_data)

        lines = result.strip().split("\n")
        assert len(lines) == len(multiple_failure_data) + 1  # Header + data rows

        # Check that all test names are present
        for failure in multiple_failure_data:
            assert failure["test_name"] in result

    def test_format_line_number_extraction(self):
        """Test line number extraction from extracted code."""
        formatter = CSVFormatter()

        failure_data = {
            "test_name": "test_line_numbers",
            "test_module": "test_module",
            "test_file": "/path/to/test.py",
            "timestamp": "2024-01-01T12:00:00",
            "exception_type": "AssertionError",
            "exception_message": "Test failed",
            "extracted_code": [
                {"line": 42, "function": "test_func"},
                {"line": 84, "function": "other_func"},
            ],
        }

        result = formatter.format([failure_data])
        lines = result.strip().split("\n")

        # Should extract first line number
        assert "42" in lines[1]

    def test_format_missing_line_number(self):
        """Test handling of missing line numbers."""
        formatter = CSVFormatter()

        failure_data = {
            "test_name": "test_no_line",
            "test_module": "test_module",
            "test_file": "/path/to/test.py",
            "timestamp": "2024-01-01T12:00:00",
            "exception_type": "AssertionError",
            "exception_message": "Test failed",
            "extracted_code": [],  # No extracted code
        }

        result = formatter.format([failure_data])

        # Should handle gracefully (empty line number field)
        lines = result.strip().split("\n")
        assert len(lines) == 2