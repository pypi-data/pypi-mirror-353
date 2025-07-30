"""Property-based tests for YAML formatter."""

import string
from datetime import datetime
from unittest.mock import Mock, patch

from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

from failextract import YAMLFormatter

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


class TestYAMLFormatterProperties:
    """Property-based tests for YAMLFormatter."""

    @given(failures=st.lists(failure_data_strategy, min_size=0, max_size=5))
    @settings(
        suppress_health_check=[HealthCheck.filter_too_much],
        max_examples=50,  # Reduce examples for suite stability
        deadline=None,  # Remove deadline for complex mocking
    )
    def test_yaml_structure_consistency(self, failures):
        """Test YAML formatter data structure consistency."""
        # Use more isolated mocking approach
        mock_yaml = Mock()
        mock_yaml.dump.return_value = "mocked_yaml_output"

        with patch.dict("sys.modules", {"yaml": mock_yaml}):
            formatter = YAMLFormatter()
            result = formatter.format(failures)

            # Should call yaml.dump
            assert mock_yaml.dump.called

            # Check the data structure passed to yaml.dump
            call_args = mock_yaml.dump.call_args
            data = call_args[0][0]

            # Should have consistent top-level structure
            assert "test_failure_report" in data
            report = data["test_failure_report"]

            assert "metadata" in report
            assert "failures" in report

            # Metadata should be correct
            assert report["metadata"]["total_failures"] == len(failures)

            # Number of failures should match
            assert len(report["failures"]) == len(failures)

    @given(failure_data=failure_data_strategy)
    @settings(
        suppress_health_check=[HealthCheck.filter_too_much],
        max_examples=50,  # Reduce examples for suite stability
        deadline=None,  # Remove deadline for complex mocking
    )
    def test_yaml_data_preservation(self, failure_data):
        """Test that YAML formatter preserves data correctly."""
        # Use more isolated mocking approach
        mock_yaml = Mock()
        mock_yaml.dump.return_value = "mocked_yaml_output"

        with patch.dict("sys.modules", {"yaml": mock_yaml}):
            formatter = YAMLFormatter()
            formatter.format([failure_data])

            # Get the data passed to yaml.dump
            call_args = mock_yaml.dump.call_args
            data = call_args[0][0]

            failure = data["test_failure_report"]["failures"][0]

            # Should preserve test information
            assert failure["test_info"]["name"] == failure_data["test_name"]
            assert failure["test_info"]["module"] == failure_data["test_module"]

            # Should preserve exception information
            assert failure["exception"]["type"] == failure_data["exception_type"]
            assert failure["exception"]["message"] == failure_data["exception_message"]