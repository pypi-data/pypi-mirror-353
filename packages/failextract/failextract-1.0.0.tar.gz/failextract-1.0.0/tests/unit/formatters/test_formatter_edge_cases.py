"""Edge case tests for formatter functionality."""

from unittest.mock import patch

import pytest

from failextract import YAMLFormatter
from failextract.core.formatters.registry import FormatterRegistry
from failextract.core.formatters.base import OutputFormat


class TestFormatterEdgeCases:
    """Test edge cases for formatter functionality."""

    def test_yaml_formatter_missing_dependency(self):
        """Test YAML formatter when PyYAML is not available."""
        formatter = YAMLFormatter()

        with patch.dict("sys.modules", {"yaml": None}):
            with pytest.raises(ImportError, match="PyYAML is required"):
                formatter.format([])

    def test_formatter_registry_edge_cases(self):
        """Test FormatterRegistry edge cases."""
        # Test getting formatter by enum
        formatter = FormatterRegistry.get_formatter(OutputFormat.JSON)
        assert formatter is not None

        # Test case insensitive string matching
        formatter = FormatterRegistry.get_formatter("json")
        assert formatter is not None

        formatter = FormatterRegistry.get_formatter("markdown")
        assert formatter is not None