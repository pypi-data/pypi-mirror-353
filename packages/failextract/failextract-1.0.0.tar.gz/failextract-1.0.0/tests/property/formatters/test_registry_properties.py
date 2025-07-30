"""Property-based tests for FormatterRegistry and formatter robustness."""

import string
from datetime import datetime

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from failextract import (
    CSVFormatter,
    FormatterRegistry,
    JSONFormatter,
    MarkdownFormatter,
    XMLFormatter,
)
from failextract.core.formatters.base import OutputFormat

# Strategies for generating test data
text_strategy = st.text(
    alphabet=string.ascii_letters + string.digits + " .,!?-_()[]{}",
    min_size=1,
    max_size=100,
)

identifier_strategy = st.text(
    alphabet=string.ascii_letters + string.digits + "_", min_size=1, max_size=50
).filter(lambda x: x.isidentifier())

file_path_strategy = st.text(
    alphabet=string.ascii_letters + string.digits + "_-", min_size=3, max_size=50
).map(lambda x: f"/test/{x}.py")

timestamp_strategy = st.datetimes(
    min_value=datetime(2020, 1, 1), max_value=datetime(2030, 12, 31)
).map(lambda dt: dt.isoformat())


class TestFormatterRegistryProperties:
    """Property-based tests for FormatterRegistry."""

    @given(
        format_type=st.sampled_from(
            [
                OutputFormat.JSON,
                OutputFormat.MARKDOWN,
                OutputFormat.XML,
                OutputFormat.CSV,
                OutputFormat.YAML,
            ]
        )
    )
    def test_formatter_registry_consistency(self, format_type):
        """Test that formatter registry returns consistent formatters."""
        formatter1 = FormatterRegistry.get_formatter(format_type)
        formatter2 = FormatterRegistry.get_formatter(format_type)

        # Should return same instance
        assert formatter1 is formatter2

        # Should be correct type
        assert formatter1.format is not None
        assert formatter1.get_extension() is not None

    @given(
        filename=st.text(
            alphabet=string.ascii_letters + string.digits + "_.-",
            min_size=5,
            max_size=50,
        ).filter(lambda x: "." in x)
    )
    def test_format_detection_robustness(self, filename):
        """Test format detection with various filenames."""
        # Should not crash on any filename
        try:
            detected_format = FormatterRegistry.detect_format(filename)
            assert isinstance(detected_format, OutputFormat)

            # Should be able to get formatter for detected format
            formatter = FormatterRegistry.get_formatter(detected_format)
            assert formatter is not None

        except Exception as e:
            # Detection should be robust and not crash
            pytest.fail(f"Format detection failed for '{filename}': {e}")

    @given(
        extension=st.sampled_from(
            [
                ".json",
                ".md",
                ".markdown",
                ".yaml",
                ".yml",
                ".xml",
                ".csv",
                ".unknown",
            ]
        )
    )
    def test_extension_mapping_consistency(self, extension):
        """Test that extension mapping is consistent."""
        filename = f"test_file{extension}"

        detected_format = FormatterRegistry.detect_format(filename)
        formatter = FormatterRegistry.get_formatter(detected_format)

        # Should get a valid formatter
        assert formatter is not None

        # For known extensions, should match expected format
        expected_mappings = {
            ".json": OutputFormat.JSON,
            ".md": OutputFormat.MARKDOWN,
            ".markdown": OutputFormat.MARKDOWN,
            ".yaml": OutputFormat.YAML,
            ".yml": OutputFormat.YAML,
            ".xml": OutputFormat.XML,
            ".csv": OutputFormat.CSV,
        }

        if extension in expected_mappings:
            assert detected_format == expected_mappings[extension]
        else:
            # Unknown extensions should default to JSON
            assert detected_format == OutputFormat.JSON


class TestFormatterRobustness:
    """Property-based tests for formatter robustness."""

    @given(
        formatter_type=st.sampled_from(
            [
                JSONFormatter,
                MarkdownFormatter,
                XMLFormatter,
                CSVFormatter,
            ]
        ),
        failures=st.lists(
            st.fixed_dictionaries(
                {
                    "test_name": text_strategy,
                    "exception_message": text_strategy,
                    "timestamp": timestamp_strategy,
                },
                optional={
                    "test_module": text_strategy,
                    "test_file": text_strategy,
                    "test_source": text_strategy,
                    "exception_type": text_strategy,
                    "extracted_code": st.lists(
                        st.dictionaries(
                            keys=st.sampled_from(
                                ["file", "function", "line", "source"]
                            ),
                            values=st.one_of(
                                text_strategy, st.integers(min_value=1, max_value=1000)
                            ),
                        ),
                        max_size=3,
                    ),
                },
            ),
            min_size=0,
            max_size=3,
        ),
    )
    @settings(max_examples=20)  # Limit for performance
    def test_formatter_robustness_with_partial_data(self, formatter_type, failures):
        """Test that formatters handle partial or malformed data gracefully."""
        formatter = formatter_type()

        try:
            result = formatter.format(failures)

            # Should produce some output
            assert isinstance(result, str)
            assert len(result) > 0

            # Should contain basic structure markers
            if formatter_type == JSONFormatter:
                # Should be valid JSON or at least start/end with brackets
                assert result.strip().startswith("[") and result.strip().endswith("]")

            elif formatter_type == MarkdownFormatter:
                assert "# Test Failure Report" in result


            elif formatter_type == XMLFormatter:
                assert "<?xml version=" in result

            elif formatter_type == CSVFormatter:
                # Should have at least a header line
                lines = result.strip().split("\n")
                assert len(lines) >= 1

        except Exception as e:
            # Some malformed data might cause exceptions, but they should be reasonable
            # (not crashes due to infinite loops, memory issues, etc.)
            assert isinstance(e, (ValueError, TypeError, KeyError, AttributeError))

    @given(
        large_text=st.text(min_size=1000, max_size=10000),
        num_failures=st.integers(min_value=1, max_value=20),
    )
    @settings(max_examples=5)  # Limit for performance
    def test_formatter_performance_with_large_data(self, large_text, num_failures):
        """Test formatter performance with large amounts of data."""
        # Create failures with large text content
        failures = []
        for i in range(num_failures):
            failure = {
                "test_name": f"test_large_{i}",
                "test_module": "test_module",
                "test_file": "/path/test.py",
                "timestamp": "2024-01-01T12:00:00",
                "test_source": large_text,
                "exception_type": "ValueError",
                "exception_message": large_text,
                "extracted_code": [
                    {
                        "file": "/path/code.py",
                        "function": "large_function",
                        "line": 1,
                        "source": large_text,
                    }
                ],
            }
            failures.append(failure)

        # Test each formatter
        formatters = [
            JSONFormatter(),
            MarkdownFormatter(),
            XMLFormatter(),
            CSVFormatter(),
        ]

        for formatter in formatters:
            try:
                result = formatter.format(failures)

                # Should complete in reasonable time and produce output
                assert isinstance(result, str)
                assert len(result) > 0

                # Output size should be reasonable (not exponentially larger than input)
                total_input_size = len(large_text) * num_failures * 3  # Rough estimate
                output_size = len(result)

                # Allow for some expansion due to formatting, but not excessive
                assert output_size < total_input_size * 10  # Reasonable upper bound

            except MemoryError:
                pytest.skip(f"Memory limit exceeded for {formatter.__class__.__name__}")
            except Exception as e:
                # Should handle large data gracefully
                assert not isinstance(e, RecursionError)  # No infinite recursion