"""Unit tests for JSONFormatter implementation."""

import json
from datetime import datetime
from unittest.mock import Mock

import pytest

from failextract import JSONFormatter, OutputFormatter


class TestJSONFormatter:
    """Test JSONFormatter implementation."""

    def test_initialization(self):
        """Test JSONFormatter initialization."""
        formatter = JSONFormatter()
        assert isinstance(formatter, OutputFormatter)

    def test_get_extension(self):
        """Test JSON file extension."""
        formatter = JSONFormatter()
        assert formatter.get_extension() == ".json"

    def test_format_empty_list(self):
        """Test formatting empty failure list."""
        formatter = JSONFormatter()
        result = formatter.format([])

        # Should be valid JSON
        parsed = json.loads(result)
        assert parsed == []

    def test_format_single_failure(self, sample_failure_data):
        """Test formatting single failure."""
        formatter = JSONFormatter()
        result = formatter.format([sample_failure_data])

        # Should be valid JSON
        parsed = json.loads(result)
        assert len(parsed) == 1
        assert parsed[0]["test_name"] == sample_failure_data["test_name"]

    def test_format_multiple_failures(self, multiple_failure_data):
        """Test formatting multiple failures."""
        formatter = JSONFormatter()
        result = formatter.format(multiple_failure_data)

        parsed = json.loads(result)
        assert len(parsed) == len(multiple_failure_data)

        for i, failure in enumerate(multiple_failure_data):
            assert parsed[i]["test_name"] == failure["test_name"]

    def test_format_with_non_serializable_data(self):
        """Test formatting with non-JSON-serializable data."""
        formatter = JSONFormatter()

        # Data with datetime object
        failure_data = {
            "test_name": "test_datetime",
            "timestamp": datetime.now(),  # Not JSON serializable by default
            "custom_object": Mock(),  # Not JSON serializable
        }

        # Should handle with default=str
        result = formatter.format([failure_data])
        parsed = json.loads(result)

        # Datetime should be converted to string
        assert isinstance(parsed[0]["timestamp"], str)
        assert isinstance(parsed[0]["custom_object"], str)

    def test_format_indentation(self, sample_failure_data):
        """Test that JSON output is properly indented."""
        formatter = JSONFormatter()
        result = formatter.format([sample_failure_data])

        # Should have indentation (2 spaces)
        lines = result.split("\n")
        assert len(lines) > 1  # Multi-line output
        assert any(line.startswith("  ") for line in lines)  # Has indentation