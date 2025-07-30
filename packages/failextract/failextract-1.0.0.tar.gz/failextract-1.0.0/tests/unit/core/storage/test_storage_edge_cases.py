"""Edge case tests for storage functionality."""

import json
from unittest.mock import patch

import pytest

from failextract import (
    FailureExtractor,
    OutputConfig,
    OutputFormat,
    save_failure_report,
    save_single_failure,
    save_with_config,
)


class TestStorageEdgeCases:
    """Test edge cases for storage functionality."""

    def test_save_single_failure_edge_cases(self, temp_directory):
        """Test save_single_failure edge cases."""
        failure_data = {"test_name": "test"}

        # Test with existing file containing invalid JSON
        bad_file = temp_directory / "bad.json"
        bad_file.write_text('{"invalid": json')

        # Should handle gracefully
        save_single_failure(failure_data, str(bad_file))

        # File should now contain valid data
        with open(bad_file, "r") as f:
            data = json.load(f)
        assert len(data) == 1

    def test_save_failure_report_variations(self, temp_directory):
        """Test save_failure_report variations."""
        extractor = FailureExtractor()
        extractor.clear()

        failure_data = {
            "test_name": "test_save_variations",
            "timestamp": "2024-01-01T12:00:00",
            "test_module": "test_module",
            "test_file": "/test.py",
            "test_source": "def test(): pass",
            "exception_type": "Error",
            "exception_message": "Test error",
            "extracted_code": [],
        }
        extractor.add_failure(failure_data)

        # Test format="md" (alias)
        md_file = temp_directory / "test.md"
        save_failure_report(str(md_file), "md")
        assert md_file.exists()

    def test_save_with_config_edge_cases(self, temp_directory):
        """Test save_with_config edge cases."""
        data = {"test_name": "test_config"}

        # Test with non-JSON format and append
        md_file = temp_directory / "test.md"
        md_file.write_text("# Existing Content\n")

        config = OutputConfig(str(md_file), OutputFormat.MARKDOWN, append=True)
        save_with_config(data, config)

        content = md_file.read_text()
        assert "Existing Content" in content
        assert "test_config" in content