"""XML output formatter for test failure reports.

This module provides XML formatting capabilities for test failure data.
XML output is useful for integration with tools that require structured
XML input, such as CI/CD systems, reporting tools, and data processing
pipelines.
"""

from datetime import datetime
from typing import List, Dict, Any

from .base import OutputFormatter


class XMLFormatter(OutputFormatter):
    """XML output formatter for test failure reports.
    
    This formatter produces well-formed XML output with proper escaping
    and CDATA sections for source code. The XML structure includes metadata
    about the report generation and detailed information for each test failure.
    
    The XML schema includes:
    - Report metadata (generation time, failure count)
    - Individual failure elements with full test information
    - Proper XML escaping for special characters
    - CDATA sections for source code to preserve formatting
    
    Example:
        >>> formatter = XMLFormatter()
        >>> failures = [{'test_name': 'test_example', 'exception_type': 'AssertionError'}]
        >>> xml_output = formatter.format(failures)
        >>> print(xml_output[:50])
        <?xml version="1.0" encoding="UTF-8"?>
        <testFailure
    """

    def format(self, failures: List[Dict[str, Any]]) -> str:
        """Format failure data as XML.
        
        Args:
            failures: List of failure dictionaries containing test failure information
            
        Returns:
            Well-formed XML string with proper escaping and CDATA sections
            
        Note:
            Uses XML escaping for text content and CDATA sections for source code
            to preserve formatting and special characters.
        """
        xml = ['<?xml version="1.0" encoding="UTF-8"?>']
        xml.append("<testFailureReport>")
        xml.append("  <metadata>")
        xml.append(f"    <generated>{datetime.now().isoformat()}</generated>")
        xml.append(f"    <totalFailures>{len(failures)}</totalFailures>")
        xml.append("  </metadata>")
        xml.append("  <failures>")

        for failure in failures:
            xml.append("    <failure>")
            xml.append(
                f"      <testName>{self._escape_xml(failure['test_name'])}</testName>"
            )
            xml.append(
                f"      <module>{self._escape_xml(failure['test_module'])}</module>"
            )
            xml.append(f"      <file>{self._escape_xml(failure['test_file'])}</file>")
            xml.append(f"      <timestamp>{failure['timestamp']}</timestamp>")
            escaped_type = self._escape_xml(failure["exception_type"])
            xml.append(f"      <exceptionType>{escaped_type}</exceptionType>")
            escaped_msg = self._escape_xml(failure["exception_message"])
            xml.append(f"      <exceptionMessage>{escaped_msg}</exceptionMessage>")
            xml.append("      <testSource><![CDATA[")
            xml.append(failure["test_source"])
            xml.append("]]></testSource>")
            xml.append("    </failure>")

        xml.append("  </failures>")
        xml.append("</testFailureReport>")
        return "\n".join(xml)

    def _escape_xml(self, text: str) -> str:
        """Escape XML special characters.
        
        Args:
            text: Raw text that may contain XML special characters
            
        Returns:
            XML-escaped text safe for inclusion in XML documents
            
        Note:
            Escapes the five XML special characters: &, <, >, ", and '
        """
        return (
            text.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;")
            .replace("'", "&apos;")
        )

    def get_extension(self) -> str:
        """Get the file extension for XML files.
        
        Returns:
            File extension '.xml'
        """
        return ".xml"