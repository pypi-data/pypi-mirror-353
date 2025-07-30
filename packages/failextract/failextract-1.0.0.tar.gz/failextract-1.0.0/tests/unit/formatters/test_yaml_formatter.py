"""Unit tests for YAMLFormatter implementation."""

from unittest.mock import patch

import pytest

from failextract import OutputFormatter, YAMLFormatter


class TestYAMLFormatter:
    """Test YAMLFormatter implementation."""

    def test_initialization(self):
        """Test YAMLFormatter initialization."""
        formatter = YAMLFormatter()
        assert isinstance(formatter, OutputFormatter)

    def test_get_extension(self):
        """Test YAML file extension."""
        formatter = YAMLFormatter()
        assert formatter.get_extension() == ".yaml"

    @patch("yaml.dump")
    def test_format_calls_yaml_dump(self, mock_yaml_dump, sample_failure_data):
        """Test that YAML formatter calls yaml.dump."""
        mock_yaml_dump.return_value = "mocked_yaml_output"

        formatter = YAMLFormatter()
        result = formatter.format([sample_failure_data])

        assert mock_yaml_dump.called
        assert result == "mocked_yaml_output"

        # Check arguments passed to yaml.dump
        call_args = mock_yaml_dump.call_args
        assert call_args[1]["default_flow_style"] is False
        assert call_args[1]["sort_keys"] is False
        assert call_args[1]["indent"] == 2

    def test_format_without_yaml_module(self, sample_failure_data):
        """Test error when PyYAML is not available."""
        formatter = YAMLFormatter()

        with patch.dict("sys.modules", {"yaml": None}):
            with pytest.raises(ImportError, match="PyYAML is required"):
                formatter.format([sample_failure_data])

    @patch("yaml.dump")
    def test_format_data_structure(self, mock_yaml_dump, sample_failure_data):
        """Test the data structure passed to YAML formatter."""
        formatter = YAMLFormatter()
        formatter.format([sample_failure_data])

        # Get the data structure passed to yaml.dump
        call_args = mock_yaml_dump.call_args
        data = call_args[0][0]

        # Check top-level structure
        assert "test_failure_report" in data
        report = data["test_failure_report"]

        assert "metadata" in report
        assert "failures" in report

        # Check metadata
        metadata = report["metadata"]
        assert "generated" in metadata
        assert "total_failures" in metadata
        assert metadata["total_failures"] == 1

        # Check failure structure
        failures = report["failures"]
        assert len(failures) == 1

        failure = failures[0]
        assert "test_info" in failure
        assert "exception" in failure
        assert "test_source" in failure

    @patch("yaml.dump")
    def test_format_with_fixtures(self, mock_yaml_dump):
        """Test YAML formatting with fixtures."""
        failure_data = {
            "test_name": "test_fixtures",
            "test_module": "test_module",
            "test_file": "/path/to/test.py",
            "timestamp": "2024-01-01T12:00:00",
            "test_source": "def test(): pass",
            "exception_type": "AssertionError",
            "exception_message": "Test failed",
            "fixtures": [
                {
                    "name": "tmp_path",
                    "type": "builtin",
                    "description": "Temporary directory",
                }
            ],
        }

        formatter = YAMLFormatter()
        formatter.format([failure_data])

        # Check fixture structure in YAML data
        call_args = mock_yaml_dump.call_args
        data = call_args[0][0]
        failure = data["test_failure_report"]["failures"][0]

        assert "fixtures" in failure
        assert len(failure["fixtures"]) == 1
        assert failure["fixtures"][0]["name"] == "tmp_path"
        assert failure["fixtures"][0]["type"] == "builtin"