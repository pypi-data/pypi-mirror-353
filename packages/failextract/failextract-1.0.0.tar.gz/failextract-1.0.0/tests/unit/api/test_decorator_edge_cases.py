"""Edge case tests for decorator functionality."""

import pytest

from failextract import OutputConfig, OutputFormat, extract_on_failure


class TestDecoratorEdgeCases:
    """Test edge cases for decorator functionality."""

    def test_extract_on_failure_edge_cases(self, temp_directory):
        """Test extract_on_failure decorator edge cases."""
        output_file = temp_directory / "test_output.json"

        # Test decorator without arguments (bare @extract_on_failure)
        @extract_on_failure
        def test_bare_decorator():
            return "success"

        result = test_bare_decorator()
        assert result == "success"

        # Test decorator with callable as first argument
        def test_func():
            raise ValueError("Test error")

        decorated = extract_on_failure(test_func)
        assert hasattr(decorated, "_extract_on_failure")

        # Test function should still raise exception
        with pytest.raises(ValueError):
            decorated()

    def test_output_config_edge_cases(self, temp_directory):
        """Test OutputConfig edge cases."""
        # Test with existing parent directory
        nested_dir = temp_directory / "nested"
        nested_dir.mkdir()

        config = OutputConfig(str(nested_dir / "report.json"))
        assert config.filename == str(nested_dir / "report.json")

        # Test format detection with no extension
        config = OutputConfig("report_no_ext")
        assert config.format == OutputFormat.JSON  # Should default to JSON