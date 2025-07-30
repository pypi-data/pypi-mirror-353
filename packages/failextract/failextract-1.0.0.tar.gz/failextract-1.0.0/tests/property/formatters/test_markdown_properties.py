"""Property-based tests for Markdown formatter."""

import string
from datetime import datetime

from hypothesis import given
from hypothesis import strategies as st

from failextract import MarkdownFormatter

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

failure_data_strategy = st.fixed_dictionaries(
    {
        "timestamp": timestamp_strategy,
        "test_name": identifier_strategy,
        "test_module": identifier_strategy,
        "test_file": file_path_strategy,
        "test_source": text_strategy,
        "test_args": st.text(min_size=2, max_size=50),
        "test_kwargs": st.text(min_size=2, max_size=50),
        "exception_type": identifier_strategy,
        "exception_message": text_strategy,
        "exception_traceback": text_strategy,
        "extracted_code": st.lists(
            st.fixed_dictionaries(
                {
                    "file": file_path_strategy,
                    "function": identifier_strategy,
                    "line": st.integers(min_value=1, max_value=10000),
                    "source": text_strategy,
                }
            ),
            min_size=0,
            max_size=5,
        ),
    }
)


class TestMarkdownFormatterProperties:
    """Property-based tests for MarkdownFormatter."""

    @given(failures=st.lists(failure_data_strategy, min_size=1, max_size=5))
    def test_markdown_structure_consistency(self, failures):
        """Test that Markdown formatter produces consistent structure."""
        formatter = MarkdownFormatter()
        result = formatter.format(failures)

        # Should always start with header
        assert result.startswith("# Test Failure Report")

        # Should contain total count
        assert f"Total Failures: {len(failures)}" in result

        # Should contain each test name
        for failure in failures:
            assert failure["test_name"] in result

        # Should have failure sections for each failure
        failure_headers = result.count("## Failure")
        assert failure_headers == len(failures)

    @given(test_name=identifier_strategy, exception_message=text_strategy)
    def test_markdown_content_escaping(self, test_name, exception_message):
        """Test that Markdown formatter handles content properly."""
        formatter = MarkdownFormatter()

        failure_data = {
            "test_name": test_name,
            "test_module": "test_module",
            "test_file": "/path/test.py",
            "timestamp": "2024-01-01T12:00:00",
            "test_source": "def test(): pass",
            "exception_type": "ValueError",
            "exception_message": exception_message,
            "extracted_code": [],
        }

        result = formatter.format([failure_data])

        # Content should be present and readable
        assert test_name in result
        assert exception_message in result

        # Should not break Markdown structure
        lines = result.split("\n")
        assert len(lines) > 5  # Should have multiple lines

    @given(failures=st.lists(failure_data_strategy, min_size=4, max_size=10))
    def test_markdown_table_of_contents(self, failures):
        """Test table of contents generation in Markdown."""
        formatter = MarkdownFormatter()
        result = formatter.format(failures)

        # Should have table of contents for multiple failures
        if len(failures) > 3:
            assert "## Table of Contents" in result

            # Should have links for each failure
            for i, failure in enumerate(failures, 1):
                link_pattern = f"- [Failure {i}: {failure['test_name']}]"
                assert link_pattern in result