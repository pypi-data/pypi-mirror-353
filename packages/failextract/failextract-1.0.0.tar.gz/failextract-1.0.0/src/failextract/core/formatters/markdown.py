"""Markdown output formatter for test failure reports.

This module provides Markdown formatting capabilities for test failure data.
Markdown output is ideal for documentation, GitHub issues, pull requests,
and other contexts where rich text formatting is needed while maintaining
readability in plain text.
"""

from datetime import datetime
from typing import List, Dict, Any

from .base import OutputFormatter


class MarkdownFormatter(OutputFormatter):
    """Markdown output formatter for test failure reports.
    
    This formatter produces well-structured Markdown output with proper
    headings, code blocks, and formatting. The output includes a table
    of contents for reports with multiple failures and uses GitHub-flavored
    Markdown syntax for optimal display.
    
    Features:
    - Automatic table of contents for reports with 3+ failures
    - Syntax-highlighted code blocks for source code
    - Structured sections with clear headings and metadata
    - Anchor links for easy navigation
    - Compatible with GitHub, GitLab, and other Markdown renderers
    
    Example:
        >>> formatter = MarkdownFormatter()
        >>> failures = [{'test_name': 'test_example', 'exception_type': 'AssertionError'}]
        >>> markdown_output = formatter.format(failures)
        >>> print(markdown_output[:30])
        # Test Failure Report
        
        Generated
    """

    def format(self, failures: List[Dict[str, Any]]) -> str:
        """Format failure data as Markdown.
        
        Args:
            failures: List of failure dictionaries containing test failure information
            
        Returns:
            Well-formatted Markdown string with headings, code blocks, and metadata
            
        Note:
            Automatically generates a table of contents for reports with 3 or more
            failures. Uses GitHub-flavored Markdown syntax for code highlighting.
        """
        output = ["# Test Failure Report\n"]
        output.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        output.append(f"Total Failures: {len(failures)}\n\n")

        # Table of contents
        if len(failures) >= 3:
            output.append("## Table of Contents\n")
            for i, failure in enumerate(failures, 1):
                test_name = failure["test_name"]
                anchor = test_name.lower().replace("_", "-")
                output.append(f"- [Failure {i}: {test_name}](#{anchor}-{i})\n")
            output.append("\n")

        for i, failure in enumerate(failures, 1):
            anchor = failure["test_name"].lower().replace("_", "-")
            output.append(
                f"## Failure {i}: `{failure['test_name']}` {{#{anchor}-{i}}}\n\n"
            )

            if "test_module" in failure:
                output.append(f"**Module:** `{failure['test_module']}`  \n")
            if "test_file" in failure:
                output.append(f"**File:** `{failure['test_file']}`  \n")
            if "timestamp" in failure:
                output.append(f"**Time:** {failure['timestamp']}  \n\n")
            else:
                output.append("\n")

            # Test code
            if "test_source" in failure:
                output.append("### Test Code\n")
                if failure.get("enhanced_context") and failure.get(
                    "test_source_with_context"
                ):
                    output.append(
                        self._format_markdown_code_context(
                            failure["test_source_with_context"]
                        )
                    )
                else:
                    output.append("```python\n")
                    output.append(failure["test_source"])
                    output.append("```\n\n")

            # Fixtures
            if failure.get("fixtures"):
                output.append("### Fixtures Used\n")
                for fixture in failure["fixtures"]:
                    output.append(f"#### `{fixture['name']}` ")
                    if fixture["type"] == "builtin":
                        output.append("(built-in)\n")
                        output.append(f"> {fixture['description']}\n\n")
                    else:
                        output.append(f"(scope: {fixture.get('scope', 'function')})\n")
                        if fixture.get("file"):
                            output.append(f"**File:** `{fixture['file']}`  \n")
                        if fixture.get("dependencies"):
                            deps = ", ".join(f"`{d}`" for d in fixture["dependencies"])
                            output.append(f"**Dependencies:** {deps}  \n")
                        if fixture.get("enhanced_source"):
                            output.append("\n")
                            output.append(
                                self._format_markdown_code_context(
                                    fixture["enhanced_source"]
                                )
                            )
                        else:
                            output.append("\n```python\n")
                            output.append(
                                fixture.get("source", "# Source not available")
                            )
                            output.append("```\n\n")

            # Tested code (optional)
            if failure.get("extracted_code"):
                output.append("### Tested Code\n")
                for code in failure["extracted_code"]:
                    func_info = (
                        f"`{code['file']}` - `{code['function']}()` line {code['line']}"
                    )
                    output.append(f"#### {func_info}\n")
                    if code.get("source"):
                        output.append("```python\n")
                        output.append(code["source"])
                        output.append("```\n")
                    output.append("\n")

            # Error details
            # Error details (optional)
            if "exception_type" in failure or "exception_message" in failure:
                output.append("### Error Details\n")
                if "exception_type" in failure:
                    output.append(f"**Type:** `{failure['exception_type']}`  \n")
                if "exception_message" in failure:
                    output.append(f"**Message:** {failure['exception_message']}  \n\n")
                else:
                    output.append("\n")

            if failure.get("exception_traceback"):
                output.append("<details>\n<summary>Full Traceback</summary>\n\n```\n")
                output.append(failure["exception_traceback"])
                output.append("```\n</details>\n\n")

            output.append("---\n\n")

        return "".join(output)

    def _format_markdown_code_context(self, source_info: Dict[str, Any]) -> str:
        """Format source code with enhanced context for Markdown.
        
        Args:
            source_info: Dictionary containing source code information with
                        'lines', 'start_line', and 'include_line_numbers' keys
                        
        Returns:
            Markdown-formatted code block with optional line numbers
            
        Note:
            Falls back to simple code block formatting if source_info is not
            a properly structured dictionary.
        """
        if not isinstance(source_info, dict):
            return f"```python\n{source_info}\n```\n\n"

        lines = source_info.get("lines", [])
        start_line = source_info.get("start_line", 1)
        include_line_numbers = source_info.get("include_line_numbers", True)

        if include_line_numbers:
            output = ["```python"]
            for i, line in enumerate(lines):
                line_num = start_line + i
                # Use comment format to show line numbers in markdown
                output.append(f"# Line {line_num}")
                output.append(line)
            output.append("```\n\n")
            return "\n".join(output)
        else:
            return f"```python\n" + "\n".join(lines) + "\n```\n\n"

    def get_extension(self) -> str:
        """Get the file extension for Markdown files.
        
        Returns:
            File extension '.md'
        """
        return ".md"