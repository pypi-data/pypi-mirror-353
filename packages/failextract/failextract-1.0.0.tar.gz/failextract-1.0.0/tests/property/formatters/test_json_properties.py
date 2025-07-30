"""Property-based tests for JSON formatter."""

import json
import string
from datetime import datetime

from hypothesis import given
from hypothesis import strategies as st

from failextract import JSONFormatter

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


class TestJSONFormatterProperties:
    """Property-based tests for JSONFormatter."""

    @given(failures=st.lists(failure_data_strategy, min_size=0, max_size=10))
    def test_json_format_always_valid(self, failures):
        """Test that JSON formatter always produces valid JSON."""
        formatter = JSONFormatter()
        result = formatter.format(failures)

        # Should always be valid JSON
        parsed = json.loads(result)

        # Should be a list
        assert isinstance(parsed, list)

        # Length should match input
        assert len(parsed) == len(failures)

        # Each item should have required fields if they were in input
        for i, failure in enumerate(failures):
            if i < len(parsed):
                parsed_failure = parsed[i]
                assert parsed_failure["test_name"] == failure["test_name"]
                assert parsed_failure["exception_type"] == failure["exception_type"]

    @given(failure_data=failure_data_strategy)
    def test_json_roundtrip_consistency(self, failure_data):
        """Test that JSON formatting preserves data through roundtrip."""
        formatter = JSONFormatter()

        # Format and parse back
        json_output = formatter.format([failure_data])
        parsed_back = json.loads(json_output)

        # Should preserve all string fields exactly
        original = parsed_back[0]
        assert original["test_name"] == failure_data["test_name"]
        assert original["exception_message"] == failure_data["exception_message"]

        # Numeric fields should be preserved - compare corresponding code blocks
        original_extracted = original.get("extracted_code", [])
        expected_extracted = failure_data.get("extracted_code", [])

        assert len(original_extracted) == len(expected_extracted)

        for i, (code_block, expected_block) in enumerate(
            zip(original_extracted, expected_extracted, strict=False)
        ):
            if "line" in expected_block:
                assert code_block["line"] == expected_block["line"]

    @given(special_chars=st.text(alphabet="<>&\"'\\/", min_size=1, max_size=20))
    def test_json_special_character_handling(self, special_chars):
        """Test JSON formatter handles special characters correctly."""
        formatter = JSONFormatter()

        failure_data = {
            "test_name": "test_special_chars",
            "test_module": "test_module",
            "test_file": "/path/test.py",
            "timestamp": "2024-01-01T12:00:00",
            "test_source": "def test(): pass",
            "exception_type": "ValueError",
            "exception_message": special_chars,  # Special characters here
            "extracted_code": [],
        }

        # Should handle any characters in JSON
        result = formatter.format([failure_data])
        parsed = json.loads(result)

        # Special characters should be preserved
        assert parsed[0]["exception_message"] == special_chars