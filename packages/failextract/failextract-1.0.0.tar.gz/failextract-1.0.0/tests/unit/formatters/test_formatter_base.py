"""Unit tests for base OutputFormatter abstract class."""

import pytest

from failextract import OutputFormatter


class TestOutputFormatter:
    """Test base OutputFormatter abstract class."""

    def test_abstract_methods(self):
        """Test that OutputFormatter is properly abstract."""
        with pytest.raises(TypeError):
            OutputFormatter()

    def test_subclass_implementation(self):
        """Test that subclasses must implement abstract methods."""

        class IncompleteFormatter(OutputFormatter):
            def format(self, failures):
                return "test"

            # Missing get_extension method

        with pytest.raises(TypeError):
            IncompleteFormatter()

        class CompleteFormatter(OutputFormatter):
            def format(self, failures):
                return "test"

            def get_extension(self):
                return ".test"

        # Should work
        formatter = CompleteFormatter()
        assert formatter.format([]) == "test"
        assert formatter.get_extension() == ".test"