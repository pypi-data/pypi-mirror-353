"""Tests for CLI input/output operations and coverage-specific functionality.

This module tests file I/O operations and save functionality including:
- File I/O operations and save functionality
- Coverage-specific CLI operations
- File writing, appending, and format handling
"""

import os
import tempfile
from unittest.mock import patch

import pytest

from failextract import FailureExtractor, OutputConfig, OutputFormat


class TestFileIOCoverage:
    """Test file I/O operations and save functionality."""

    def test_save_report_basic_functionality(self):
        """Test basic save report functionality."""
        # Target lines 1007-1021: save_report method
        extractor = FailureExtractor()

        # Add a failure to have data to save
        extractor.failures.append(
            {
                "test_name": "test_example",
                "test_module": "test_module",
                "test_file": "/path/to/test.py",
                "exception_message": "Test failure",
                "exception_type": "AssertionError",
                "timestamp": "2025-12-03T12:00:00",
                "test_source": "def test_example(): assert False",
                "extracted_code": [],
            }
        )

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            config = OutputConfig(output=f.name, format=OutputFormat.JSON)

            # Target line 1007: data = self._prepare_data(config)
            # Target lines 1012-1013: formatter and content generation
            # Target lines 1015-1021: file writing logic
            extractor.save_report(config)

        # Verify file was created and contains data
        assert os.path.exists(f.name)
        with open(f.name, "r") as f:
            content = f.read()
            assert "test_example" in content
            assert "AssertionError" in content

        os.unlink(f.name)

    def test_save_report_no_failures_no_output(self):
        """Test save report with no failures doesn't create output."""
        # Target lines 1009-1010: Early return when no data and not include_passed
        extractor = FailureExtractor()
        # Ensure extractor has no failures
        extractor.failures.clear()
        extractor.passed.clear()

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            temp_name = f.name
        os.unlink(temp_name)  # Remove the file so we can test it doesn't get created

        config = OutputConfig(
            output=temp_name, format=OutputFormat.JSON, include_passed=False
        )
        extractor.save_report(config)

        # File should not be created
        assert not os.path.exists(temp_name)

    def test_save_report_append_mode(self):
        """Test save report with append mode."""
        # Target line 1015: mode = 'a' if config.append else 'w'
        extractor = FailureExtractor()
        extractor.failures.append(
            {
                "test_name": "test_first",
                "test_module": "test_module_first",
                "test_file": "/path/to/first.py",
                "exception_message": "First failure",
                "exception_type": "AssertionError",
                "timestamp": "2025-12-03T12:00:00",
                "test_source": "def test_first(): assert False",
                "extracted_code": [],
            }
        )

        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            # First write
            config = OutputConfig(
                output=f.name, format=OutputFormat.MARKDOWN, append=False
            )
            extractor.save_report(config)

            # Second write with append
            extractor.failures.append(
                {
                    "test_name": "test_second",
                    "test_module": "test_module_second",
                    "test_file": "/path/to/second.py",
                    "exception_message": "Second failure",
                    "exception_type": "ValueError",
                    "timestamp": "2025-12-03T12:01:00",
                    "test_source": 'def test_second(): raise ValueError("test")',
                    "extracted_code": [],
                }
            )

            config_append = OutputConfig(
                output=f.name, format=OutputFormat.MARKDOWN, append=True
            )
            extractor.save_report(config_append)

        # Verify both failures are in the file
        with open(f.name, "r") as f:
            content = f.read()
            assert "test_first" in content
            assert "test_second" in content

        os.unlink(f.name)

    def test_save_report_json_append_special_handling(self):
        """Test special JSON append handling."""
        # Target lines 1017-1019: Special JSON append logic
        extractor = FailureExtractor()
        extractor.failures.append(
            {
                "test_name": "test_json",
                "test_module": "test_module_json",
                "test_file": "/path/to/json.py",
                "exception_message": "JSON test",
                "exception_type": "RuntimeError",
                "timestamp": "2025-12-03T12:00:00",
                "test_source": 'def test_json(): raise RuntimeError("json test")',
                "extracted_code": [],
            }
        )

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            config = OutputConfig(output=f.name, format=OutputFormat.JSON, append=True)

            # This should trigger the _append_json path
            with patch.object(extractor, "_append_json") as mock_append:
                extractor.save_report(config)
                mock_append.assert_called_once()

        os.unlink(f.name)