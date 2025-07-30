#!/usr/bin/env python3
"""
Advanced example: Custom formatter implementation

This example demonstrates how to create and register a custom output formatter.
"""

import json
from datetime import datetime
from typing import List, Dict, Any, Optional

from failextract import (
    OutputFormatter, FormatterRegistry, OutputFormat, 
    extract_on_failure, FailureExtractor, OutputConfig
)


class SlackFormatter(OutputFormatter):
    """Custom formatter for Slack notifications."""
    
    def format(self, failures: List[Dict[str, Any]], 
               passed: Optional[List[Dict[str, Any]]] = None,
               metadata: Optional[Dict[str, Any]] = None) -> str:
        """Format failures as Slack message blocks."""
        
        if not failures:
            return self._create_success_message(passed, metadata)
        
        blocks = []
        
        # Header block
        total_tests = len(failures) + (len(passed) if passed else 0)
        success_rate = ((len(passed) if passed else 0) / total_tests * 100) if total_tests > 0 else 0
        
        header_text = f"🚨 Test Failures Report"
        if metadata and metadata.get('generated_at'):
            header_text += f" - {metadata['generated_at']}"
        
        blocks.append({
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": header_text
            }
        })
        
        # Summary block
        summary_text = f"*{len(failures)} failures* out of {total_tests} tests ({success_rate:.1f}% success rate)"
        blocks.append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": summary_text
            }
        })
        
        # Divider
        blocks.append({"type": "divider"})
        
        # Failure details (limit to first 5 to avoid message size limits)
        for i, failure in enumerate(failures[:5]):
            test_name = failure.get('test_name', 'Unknown test')
            module = failure.get('test_module', 'Unknown module')
            error_msg = failure.get('exception_message', 'No error message')
            error_type = failure.get('exception_type', 'Unknown error')
            
            failure_text = f"*{test_name}*\n"
            failure_text += f"Module: `{module}`\n"
            failure_text += f"Error: {error_type}: {error_msg[:100]}{'...' if len(error_msg) > 100 else ''}"
            
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": failure_text
                }
            })
        
        if len(failures) > 5:
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"_... and {len(failures) - 5} more failures_"
                }
            })
        
        return json.dumps({"blocks": blocks}, indent=2)
    
    def _create_success_message(self, passed, metadata):
        """Create a success message when no failures."""
        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": "✅ All Tests Passed!"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*{len(passed) if passed else 0} tests* completed successfully"
                }
            }
        ]
        
        return json.dumps({"blocks": blocks}, indent=2)


class JunitXMLFormatter(OutputFormatter):
    """Custom formatter for JUnit XML format."""
    
    def format(self, failures: List[Dict[str, Any]], 
               passed: Optional[List[Dict[str, Any]]] = None,
               metadata: Optional[Dict[str, Any]] = None) -> str:
        """Format failures as JUnit XML."""
        
        total_tests = len(failures) + (len(passed) if passed else 0)
        total_failures = len(failures)
        
        xml_lines = [
            '<?xml version="1.0" encoding="UTF-8"?>',
            f'<testsuite name="FailExtract" tests="{total_tests}" failures="{total_failures}" errors="0" time="0">'
        ]
        
        # Add failure test cases
        for failure in failures:
            test_name = failure.get('test_name', 'unknown_test')
            classname = failure.get('test_module', 'unknown_module')
            error_type = failure.get('exception_type', 'AssertionError')
            error_msg = failure.get('exception_message', 'No message')
            traceback = failure.get('exception_traceback', 'No traceback')
            
            xml_lines.extend([
                f'  <testcase classname="{classname}" name="{test_name}" time="0">',
                f'    <failure type="{error_type}" message="{self._escape_xml(error_msg)}">',
                f'      <![CDATA[{traceback}]]>',
                '    </failure>',
                '  </testcase>'
            ])
        
        # Add passed test cases
        if passed:
            for test in passed:
                test_name = test.get('test_name', 'unknown_test')
                classname = test.get('test_module', 'unknown_module')
                xml_lines.append(f'  <testcase classname="{classname}" name="{test_name}" time="0"/>')
        
        xml_lines.append('</testsuite>')
        
        return '\n'.join(xml_lines)
    
    def _escape_xml(self, text: str) -> str:
        """Escape XML special characters."""
        return (text.replace('&', '&amp;')
                   .replace('<', '&lt;')
                   .replace('>', '&gt;')
                   .replace('"', '&quot;')
                   .replace("'", '&#39;'))


# Test functions to demonstrate custom formatters
@extract_on_failure
def test_user_authentication():
    """Test user authentication failure."""
    username = "test_user"
    password = "wrong_password"
    authenticated = False  # Simulate auth failure
    
    assert authenticated, f"Authentication failed for user: {username}"


@extract_on_failure
def test_data_validation():
    """Test data validation failure."""
    data = {"name": "", "email": "invalid-email", "age": -5}
    
    errors = []
    if not data["name"]:
        errors.append("Name is required")
    if "@" not in data["email"]:
        errors.append("Invalid email format")
    if data["age"] < 0:
        errors.append("Age must be positive")
    
    assert len(errors) == 0, f"Validation errors: {', '.join(errors)}"


def main():
    """Demonstrate custom formatters."""
    print("Running custom formatter example...")
    
    # Register custom formatters
    slack_formatter = SlackFormatter()
    junit_formatter = JunitXMLFormatter()
    
    # Note: In a real implementation, you'd extend OutputFormat enum
    # For this example, we'll use the formatters directly
    
    # Run tests to generate failures
    tests = [test_user_authentication, test_data_validation]
    for test_func in tests:
        try:
            test_func()
        except AssertionError:
            pass
    
    # Get failures
    extractor = FailureExtractor()
    failures = extractor.failures
    
    if failures:
        print(f"Generated {len(failures)} failures")
        
        # Generate Slack format
        slack_output = slack_formatter.format(failures)
        with open("failures_slack.json", "w") as f:
            f.write(slack_output)
        print("Generated failures_slack.json (Slack blocks format)")
        
        # Generate JUnit XML format
        junit_output = junit_formatter.format(failures)
        with open("failures_junit.xml", "w") as f:
            f.write(junit_output)
        print("Generated failures_junit.xml (JUnit XML format)")
        
        # Show sample of Slack output
        print("\nSample Slack format:")
        print("=" * 50)
        slack_data = json.loads(slack_output)
        for block in slack_data["blocks"][:3]:  # Show first 3 blocks
            if block["type"] == "header":
                print(f"HEADER: {block['text']['text']}")
            elif block["type"] == "section":
                print(f"SECTION: {block['text']['text']}")
            print()
    else:
        print("No failures to format")


if __name__ == "__main__":
    main()