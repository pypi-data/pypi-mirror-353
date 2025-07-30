"""Unit tests for XMLFormatter implementation."""

import xml.etree.ElementTree as ET

import pytest

from failextract import OutputFormatter, XMLFormatter


class TestXMLFormatter:
    """Test XMLFormatter implementation."""

    def test_initialization(self):
        """Test XMLFormatter initialization."""
        formatter = XMLFormatter()
        assert isinstance(formatter, OutputFormatter)

    def test_get_extension(self):
        """Test XML file extension."""
        formatter = XMLFormatter()
        assert formatter.get_extension() == ".xml"

    def test_format_basic_structure(self, sample_failure_data):
        """Test basic XML structure."""
        formatter = XMLFormatter()
        result = formatter.format([sample_failure_data])

        # Check XML declaration and structure
        assert '<?xml version="1.0" encoding="UTF-8"?>' in result
        assert "<testFailureReport>" in result
        assert "<metadata>" in result
        assert "<failures>" in result
        assert "</testFailureReport>" in result

    def test_format_valid_xml(self, sample_failure_data):
        """Test that output is valid XML."""
        formatter = XMLFormatter()
        result = formatter.format([sample_failure_data])

        # Should parse without errors
        root = ET.fromstring(result)
        assert root.tag == "testFailureReport"

        # Check structure
        metadata = root.find("metadata")
        assert metadata is not None

        failures = root.find("failures")
        assert failures is not None

        failure_elements = failures.findall("failure")
        assert len(failure_elements) == 1

    def test_xml_escape_functionality(self):
        """Test XML character escaping."""
        formatter = XMLFormatter()

        # Test escape method
        assert formatter._escape_xml("&") == "&amp;"
        assert formatter._escape_xml("<") == "&lt;"
        assert formatter._escape_xml(">") == "&gt;"
        assert formatter._escape_xml('"') == "&quot;"
        assert formatter._escape_xml("'") == "&apos;"

    def test_format_with_special_characters(self):
        """Test XML formatting with special characters."""
        formatter = XMLFormatter()

        failure_data = {
            "test_name": "test_xml_chars",
            "test_module": "test_module",
            "test_file": "/path/to/test.py",
            "timestamp": "2024-01-01T12:00:00",
            "test_source": "def test():\n    assert \"value\" == 'other'",
            "exception_type": "AssertionError",
            "exception_message": "Failed: \"value\" & 'other'",
            "extracted_code": [],
        }

        result = formatter.format([failure_data])

        # Should be valid XML despite special characters
        root = ET.fromstring(result)

        # Check that special characters are properly escaped
        exception_msg = root.find(".//exceptionMessage").text
        assert '"' not in exception_msg or "&quot;" in result
        assert "'" not in exception_msg or "&apos;" in result

    def test_format_cdata_sections(self, sample_failure_data):
        """Test CDATA sections for source code."""
        formatter = XMLFormatter()
        result = formatter.format([sample_failure_data])

        # Source code should be in CDATA sections
        assert "<![CDATA[" in result
        assert "]]>" in result

        # Verify CDATA contains source code
        cdata_start = result.find("<![CDATA[")
        cdata_end = result.find("]]>", cdata_start)
        cdata_content = result[cdata_start + 9 : cdata_end]
        assert sample_failure_data["test_source"] in cdata_content