"""Property-based tests for XML formatter."""

import string
import xml.etree.ElementTree as ET
from datetime import datetime

import pytest
from hypothesis import given
from hypothesis import strategies as st

from failextract import XMLFormatter

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


class TestXMLFormatterProperties:
    """Property-based tests for XMLFormatter."""

    @given(failures=st.lists(failure_data_strategy, min_size=0, max_size=5))
    def test_xml_validity(self, failures):
        """Test that XML formatter produces valid XML."""
        formatter = XMLFormatter()
        result = formatter.format(failures)

        # Should parse as valid XML
        try:
            root = ET.fromstring(result)

            # Should have correct root element
            assert root.tag == "testFailureReport"

            # Should have metadata and failures elements
            metadata = root.find("metadata")
            assert metadata is not None

            failures_elem = root.find("failures")
            assert failures_elem is not None

            # Number of failure elements should match input
            failure_elements = failures_elem.findall("failure")
            assert len(failure_elements) == len(failures)

        except ET.ParseError as e:
            pytest.fail(f"Generated XML is not valid: {e}")

    @given(xml_special_chars=st.text(alphabet="<>&\"'", min_size=1, max_size=20))
    def test_xml_character_escaping(self, xml_special_chars):
        """Test XML character escaping."""
        formatter = XMLFormatter()

        failure_data = {
            "test_name": "test_xml_chars",
            "test_module": "test_module",
            "test_file": "/path/test.py",
            "timestamp": "2024-01-01T12:00:00",
            "test_source": "def test(): pass",
            "exception_type": "ValueError",
            "exception_message": xml_special_chars,
            "extracted_code": [],
        }

        result = formatter.format([failure_data])

        # Should still be valid XML despite special characters
        try:
            root = ET.fromstring(result)

            # Find the exception message element
            exception_msg = root.find(".//exceptionMessage")
            if exception_msg is not None:
                # Characters should be properly escaped or in CDATA
                assert exception_msg.text is not None

        except ET.ParseError as e:
            pytest.fail(f"XML with special characters is not valid: {e}")