Creating Custom Formatters
===========================

**Purpose**: Build specialized output formats for your tools and workflows

This tutorial teaches you how to create custom formatters for FailExtract, enabling you to generate output in any format your tools and processes require. Perfect for integrating with monitoring systems, chat platforms, and custom reporting tools.

What You'll Learn
-----------------

- How to implement the OutputFormatter interface
- How to create formatters for popular platforms (Slack, JUnit, etc.)
- How to handle different data structures and edge cases
- How to register and use custom formatters
- How to build production-ready formatters with error handling

Prerequisites
-------------

- Completed all previous tutorials
- Understanding of Python classes and inheritance
- Familiarity with output formats you want to support
- 25 minutes of time

Custom Formatter Architecture
-----------------------------

FailExtract uses a simple interface for custom formatters:

.. code-block:: python

   from abc import ABC, abstractmethod
   from typing import List, Dict, Any, Optional

   class OutputFormatter(ABC):
       """Base class for all output formatters."""
       
       @abstractmethod
       def format(self, 
                  failures: List[Dict[str, Any]], 
                  passed: Optional[List[Dict[str, Any]]] = None,
                  metadata: Optional[Dict[str, Any]] = None) -> str:
           """Format failure data into output string."""
           pass

**Key Design Principles**:

- **Simple interface** - Just implement one method
- **Rich input data** - Access to failures, passed tests, and metadata
- **String output** - Return formatted string ready for file writing
- **Flexible data handling** - Handle missing or optional data gracefully

Your First Custom Formatter
----------------------------

Let's create a simple formatter for team notifications:

.. code-block:: python

   from failextract import OutputFormatter
   from typing import List, Dict, Any, Optional
   import json

   class TeamNotificationFormatter(OutputFormatter):
       """Simple formatter for team notifications."""
       
       def format(self, 
                  failures: List[Dict[str, Any]], 
                  passed: Optional[List[Dict[str, Any]]] = None,
                  metadata: Optional[Dict[str, Any]] = None) -> str:
           """Format as simple team notification."""
           
           if not failures:
               return "🎉 All tests passed! Great work team!"
           
           # Build notification message
           total_tests = len(failures) + (len(passed) if passed else 0)
           success_rate = ((len(passed) if passed else 0) / total_tests * 100) if total_tests > 0 else 0
           
           message_parts = [
               f"🚨 Test Results Summary",
               f"",
               f"❌ Failures: {len(failures)}",
               f"✅ Passed: {len(passed) if passed else 0}",
               f"📊 Success Rate: {success_rate:.1f}%",
               f"",
               f"Failed Tests:"
           ]
           
           # Add failure details (limit to avoid spam)
           for i, failure in enumerate(failures[:5]):
               test_name = failure.get('test_name', 'Unknown test')
               error_msg = failure.get('exception_message', 'No error message')
               message_parts.append(f"  {i+1}. {test_name}: {error_msg[:80]}{'...' if len(error_msg) > 80 else ''}")
           
           if len(failures) > 5:
               message_parts.append(f"  ... and {len(failures) - 5} more failures")
           
           return "\\n".join(message_parts)

**Test your formatter:**

.. code-block:: python

   # test_custom_formatter.py
   from failextract import extract_on_failure, FailureExtractor

   @extract_on_failure
   def test_example_failure():
       assert False, "This is a test failure for our custom formatter"

   if __name__ == "__main__":
       # Run test to generate failure
       try:
           test_example_failure()
       except AssertionError:
           pass
       
       # Use custom formatter
       extractor = FailureExtractor()
       formatter = TeamNotificationFormatter()
       
       output = formatter.format(extractor.failures)
       print(output)
       
       # Save to file
       with open("team_notification.txt", "w") as f:
           f.write(output)

Real-World Example: Slack Formatter
------------------------------------

Here's a production-ready formatter for Slack notifications:

.. code-block:: python

   import json
   from datetime import datetime
   from failextract import OutputFormatter

   class SlackFormatter(OutputFormatter):
       """Professional Slack notification formatter."""
       
       def format(self, 
                  failures: List[Dict[str, Any]], 
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
           
           # Summary block with rich formatting
           summary_text = f"*{len(failures)} failures* out of {total_tests} tests "
           summary_text += f"({success_rate:.1f}% success rate)"
           
           # Add color coding based on success rate
           if success_rate >= 95:
               emoji = "🟡"
           elif success_rate >= 80:
               emoji = "🟠" 
           else:
               emoji = "🔴"
           
           blocks.append({
               "type": "section",
               "text": {
                   "type": "mrkdwn",
                   "text": f"{emoji} {summary_text}"
               }
           })
           
           # Divider
           blocks.append({"type": "divider"})
           
           # Failure details (limit to avoid Slack message size limits)
           for i, failure in enumerate(failures[:5]):
               test_name = failure.get('test_name', 'Unknown test')
               module = failure.get('test_module', 'Unknown module')
               error_msg = failure.get('exception_message', 'No error message')
               error_type = failure.get('exception_type', 'Unknown error')
               
               # Truncate long error messages
               if len(error_msg) > 100:
                   error_msg = error_msg[:100] + "..."
               
               failure_text = f"*{test_name}*\\n"
               failure_text += f"Module: `{module}`\\n"
               failure_text += f"Error: {error_type}: {error_msg}"
               
               blocks.append({
                   "type": "section",
                   "text": {
                       "type": "mrkdwn",
                       "text": failure_text
                   }
               })
           
           # Show remaining count if truncated
           if len(failures) > 5:
               blocks.append({
                   "type": "section",
                   "text": {
                       "type": "mrkdwn",
                       "text": f"_... and {len(failures) - 5} more failures_"
                   }
               })
           
           # Add action buttons for common responses
           blocks.append({
               "type": "actions",
               "elements": [
                   {
                       "type": "button",
                       "text": {
                           "type": "plain_text",
                           "text": "View Full Report"
                       },
                       "style": "primary",
                       "url": metadata.get('report_url', '#') if metadata else '#'
                   },
                   {
                       "type": "button", 
                       "text": {
                           "type": "plain_text",
                           "text": "Acknowledge"
                       },
                       "style": "danger"
                   }
               ]
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

**Using the Slack formatter:**

.. code-block:: python

   # Generate Slack notification
   formatter = SlackFormatter()
   slack_message = formatter.format(
       failures=extractor.failures,
       passed=extractor.passed,
       metadata={
           'generated_at': datetime.now().isoformat(),
           'report_url': 'https://your-ci.com/reports/123'
       }
   )
   
   # Save for Slack webhook
   with open("slack_notification.json", "w") as f:
       f.write(slack_message)

Advanced Example: JUnit XML Formatter
--------------------------------------

For CI/CD integration, here's a JUnit XML formatter:

.. code-block:: python

   class JunitXMLFormatter(OutputFormatter):
       """JUnit XML formatter for CI/CD integration."""
       
       def format(self, 
                  failures: List[Dict[str, Any]], 
                  passed: Optional[List[Dict[str, Any]]] = None,
                  metadata: Optional[Dict[str, Any]] = None) -> str:
           """Format failures as JUnit XML."""
           
           total_tests = len(failures) + (len(passed) if passed else 0)
           total_failures = len(failures)
           
           # Calculate timing if available
           total_time = 0
           if metadata and 'total_duration' in metadata:
               total_time = metadata['total_duration']
           
           xml_lines = [
               '<?xml version="1.0" encoding="UTF-8"?>',
               f'<testsuite name="FailExtract" tests="{total_tests}" '
               f'failures="{total_failures}" errors="0" time="{total_time}">'
           ]
           
           # Add failure test cases
           for failure in failures:
               test_name = failure.get('test_name', 'unknown_test')
               classname = failure.get('test_module', 'unknown_module')
               error_type = failure.get('exception_type', 'AssertionError')
               error_msg = failure.get('exception_message', 'No message')
               traceback = failure.get('exception_traceback', 'No traceback')
               test_time = failure.get('duration', 0)
               
               xml_lines.extend([
                   f'  <testcase classname="{classname}" name="{test_name}" time="{test_time}">',
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
                   test_time = test.get('duration', 0)
                   xml_lines.append(
                       f'  <testcase classname="{classname}" name="{test_name}" time="{test_time}"/>'
                   )
           
           xml_lines.append('</testsuite>')
           
           return '\\n'.join(xml_lines)
       
       def _escape_xml(self, text: str) -> str:
           """Escape XML special characters."""
           if not text:
               return ""
           
           return (str(text).replace('&', '&amp;')
                           .replace('<', '&lt;')
                           .replace('>', '&gt;')
                           .replace('"', '&quot;')
                           .replace("'", '&#39;'))

Handling Edge Cases and Errors
-------------------------------

Production formatters must handle edge cases gracefully:

.. code-block:: python

   class RobustFormatter(OutputFormatter):
       """Example showing robust error handling."""
       
       def format(self, 
                  failures: List[Dict[str, Any]], 
                  passed: Optional[List[Dict[str, Any]]] = None,
                  metadata: Optional[Dict[str, Any]] = None) -> str:
           """Robust formatter with comprehensive error handling."""
           
           try:
               return self._format_internal(failures, passed, metadata)
           except Exception as e:
               # Fallback to minimal format if main formatting fails
               return self._create_fallback_format(failures, passed, str(e))
       
       def _format_internal(self, failures, passed, metadata):
           """Main formatting logic."""
           # Handle None inputs
           failures = failures or []
           passed = passed or []
           metadata = metadata or {}
           
           # Validate data structure
           for failure in failures:
               if not isinstance(failure, dict):
                   raise ValueError(f"Invalid failure data type: {type(failure)}")
           
           # Handle empty data
           if not failures and not passed:
               return "No test data available"
           
           # Main formatting logic here
           result_parts = [
               f"Test Results ({metadata.get('generated_at', 'unknown time')})",
               f"Failures: {len(failures)}",
               f"Passed: {len(passed)}"
           ]
           
           # Format failures with safe access to nested data
           for failure in failures:
               test_name = self._safe_get(failure, 'test_name', 'Unknown test')
               error_msg = self._safe_get(failure, 'exception_message', 'No error message')
               
               # Sanitize strings to prevent injection
               test_name = self._sanitize_string(test_name)
               error_msg = self._sanitize_string(error_msg)
               
               result_parts.append(f"  - {test_name}: {error_msg}")
           
           return "\\n".join(result_parts)
       
       def _safe_get(self, data: Dict, key: str, default: str = "") -> str:
           """Safely get string value from dict."""
           value = data.get(key, default)
           return str(value) if value is not None else default
       
       def _sanitize_string(self, text: str, max_length: int = 200) -> str:
           """Sanitize and truncate string."""
           if not text:
               return ""
           
           # Remove control characters
           sanitized = ''.join(char for char in text if ord(char) >= 32 or char in '\\n\\t')
           
           # Truncate if too long
           if len(sanitized) > max_length:
               sanitized = sanitized[:max_length] + "..."
           
           return sanitized
       
       def _create_fallback_format(self, failures, passed, error_msg):
           """Create minimal format when main formatting fails."""
           return f"Formatting error: {error_msg}\\nFailures: {len(failures or [])}\\nPassed: {len(passed or [])}"

Using Custom Formatters
------------------------

**Direct Usage**

.. code-block:: python

   from failextract import FailureExtractor

   # Create formatter and use directly
   formatter = SlackFormatter()
   extractor = FailureExtractor()

   # Generate output
   output = formatter.format(
       failures=extractor.failures,
       passed=extractor.passed,
       metadata={'generated_at': datetime.now().isoformat()}
   )

   # Save or send
   with open("custom_report.json", "w") as f:
       f.write(output)

**Integration with OutputConfig** (Advanced)

For seamless integration, you can extend FailExtract's format system:

.. code-block:: python

   from failextract.core.formatters.registry import FormatterRegistry

   # Register custom formatter (in a real implementation)
   def register_custom_formatters():
       """Register custom formatters with FailExtract."""
       registry = FormatterRegistry()
       
       # This would require extending the OutputFormat enum
       # and modifying the registry system
       # registry.register('slack', SlackFormatter())
       # registry.register('junit', JunitXMLFormatter())
       
       # For now, use formatters directly as shown above

Complete Custom Formatter Example
----------------------------------

Here's a complete example showing a formatter for GitHub Issues:

.. code-block:: python

   #!/usr/bin/env python3
   """Complete custom formatter example for GitHub Issues"""
   
   from failextract import OutputFormatter, extract_on_failure, FailureExtractor
   from typing import List, Dict, Any, Optional
   from datetime import datetime

   class GitHubIssueFormatter(OutputFormatter):
       """Format failures as GitHub issue markdown."""
       
       def format(self, 
                  failures: List[Dict[str, Any]], 
                  passed: Optional[List[Dict[str, Any]]] = None,
                  metadata: Optional[Dict[str, Any]] = None) -> str:
           """Format as GitHub issue markdown."""
           
           if not failures:
               return self._create_success_summary(passed, metadata)
           
           issue_parts = []
           
           # Issue title and summary
           total_tests = len(failures) + (len(passed) if passed else 0)
           success_rate = ((len(passed) if passed else 0) / total_tests * 100) if total_tests > 0 else 0
           
           issue_parts.extend([
               f"# 🚨 Test Failures Report",
               f"",
               f"**Summary:** {len(failures)} test(s) failed out of {total_tests} total tests ({success_rate:.1f}% success rate)",
               f"",
               f"**Generated:** {metadata.get('generated_at', datetime.now().isoformat()) if metadata else datetime.now().isoformat()}",
               f""
           ])
           
           # Add environment information if available
           if metadata:
               issue_parts.extend([
                   f"## Environment",
                   f"",
                   f"- **Branch:** {metadata.get('branch', 'unknown')}",
                   f"- **Commit:** {metadata.get('commit', 'unknown')}",
                   f"- **Environment:** {metadata.get('environment', 'unknown')}",
                   f""
               ])
           
           # Failure details
           issue_parts.extend([
               f"## Failed Tests",
               f""
           ])
           
           for i, failure in enumerate(failures, 1):
               test_name = failure.get('test_name', 'Unknown test')
               module = failure.get('test_module', 'Unknown module')
               file_path = failure.get('test_file', 'Unknown file')
               error_type = failure.get('exception_type', 'Unknown error')
               error_msg = failure.get('exception_message', 'No error message')
               
               issue_parts.extend([
                   f"### {i}. `{test_name}`",
                   f"",
                   f"**File:** `{file_path}`  ",
                   f"**Module:** `{module}`  ",
                   f"**Error Type:** `{error_type}`  ",
                   f"",
                   f"**Error Message:**",
                   f"```",
                   f"{error_msg}",
                   f"```",
                   f""
               ])
               
               # Add local variables if available
               if 'local_variables' in failure and failure['local_variables']:
                   issue_parts.extend([
                       f"**Local Variables:**",
                       f"```python"
                   ])
                   
                   for var_name, var_value in failure['local_variables'].items():
                       # Limit variable output to prevent huge issues
                       value_str = str(var_value)
                       if len(value_str) > 100:
                           value_str = value_str[:100] + "..."
                       issue_parts.append(f"{var_name} = {value_str}")
                   
                   issue_parts.extend([f"```", f""])
           
           # Add success summary if there are passed tests
           if passed:
               issue_parts.extend([
                   f"## Passed Tests",
                   f"",
                   f"✅ {len(passed)} tests passed successfully",
                   f""
               ])
           
           # Add troubleshooting section
           issue_parts.extend([
               f"## Troubleshooting",
               f"",
               f"- [ ] Review failed test cases above",
               f"- [ ] Check environment configuration",
               f"- [ ] Verify test data and fixtures",
               f"- [ ] Review recent code changes",
               f"- [ ] Run tests locally to reproduce",
               f"",
               f"## Labels",
               f"",
               f"`bug` `test-failure` `needs-investigation`"
           ])
           
           return "\\n".join(issue_parts)
       
       def _create_success_summary(self, passed, metadata):
           """Create success summary for all-passing runs."""
           return f"""# ✅ All Tests Passed!
   
   **Summary:** {len(passed) if passed else 0} tests completed successfully
   
   **Generated:** {metadata.get('generated_at', datetime.now().isoformat()) if metadata else datetime.now().isoformat()}
   
   Great work! 🎉"""

   # Example usage
   @extract_on_failure
   def test_user_registration():
       user_data = {"email": "invalid-email", "age": -5}
       assert "@" in user_data["email"], "Invalid email format"

   @extract_on_failure  
   def test_data_processing():
       data = []
       assert len(data) > 0, "No data to process"

   if __name__ == "__main__":
       # Run tests to generate failures
       for test_func in [test_user_registration, test_data_processing]:
           try:
               test_func()
           except AssertionError:
               pass
       
       # Generate GitHub issue
       formatter = GitHubIssueFormatter()
       extractor = FailureExtractor()
       
       github_issue = formatter.format(
           failures=extractor.failures,
           metadata={
               'generated_at': datetime.now().isoformat(),
               'branch': 'feature/user-registration',
               'commit': 'abc123def',
               'environment': 'CI/CD'
           }
       )
       
       # Save as markdown file
       with open("github_issue.md", "w") as f:
           f.write(github_issue)
       
       print("Generated github_issue.md")
       print(f"Found {len(extractor.failures)} failures to report")

Formatter Best Practices
-------------------------

**Design Principles**

1. **Fail Gracefully** - Handle missing data without crashing
2. **Limit Output Size** - Prevent overwhelming users or hitting API limits
3. **Sanitize Input** - Clean data to prevent injection or display issues
4. **Provide Context** - Include enough information for actionable responses
5. **Consider Your Audience** - Format for your specific users and tools

**Performance Considerations**

.. code-block:: python

   class PerformantFormatter(OutputFormatter):
       """Example showing performance optimizations."""
       
       def __init__(self, max_failures: int = 50, max_message_length: int = 1000):
           self.max_failures = max_failures
           self.max_message_length = max_message_length
       
       def format(self, failures, passed=None, metadata=None):
           # Limit data size early to improve performance
           limited_failures = failures[:self.max_failures] if failures else []
           
           # Use list comprehension for efficiency
           formatted_failures = [
               self._format_single_failure(f) 
               for f in limited_failures
           ]
           
           result = "\\n".join(formatted_failures)
           
           # Truncate final result if too long
           if len(result) > self.max_message_length:
               result = result[:self.max_message_length] + "\\n... (truncated)"
           
           return result

Next Steps
----------

Now that you can create custom formatters:

- **Deploy in Production** - Integrate formatters with your monitoring and notification systems
- **Share with Team** - Create formatters that match your team's workflow tools
- **Contribute Back** - Consider contributing useful formatters to the FailExtract project
- **Automate Integration** - Set up automatic formatter usage in CI/CD pipelines

Key Custom Formatter Takeaways
-------------------------------

| ✅ **Simple interface** - Just implement the `format()` method  
| ✅ **Rich input data** - Access failures, passed tests, and metadata  
| ✅ **Production-ready patterns** - Error handling, sanitization, limits  
| ✅ **Platform-specific examples** - Slack, JUnit, GitHub formats  
| ✅ **Performance optimization** - Limit data size and processing time  
| ✅ **Flexible integration** - Use directly or integrate with existing systems  

**You can now create formatters for any tool or platform!**