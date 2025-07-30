"""YAML output formatter for test failure reports.

This module provides YAML formatting capabilities for test failure data.
YAML output is ideal for configuration-like structured data, human-readable
reports, and integration with systems that prefer YAML over JSON.

Note:
    This formatter requires PyYAML as an optional dependency. Install with:
    pip install failextract[formatters]
"""

from datetime import datetime
from typing import List, Dict, Any

from .base import OutputFormatter


class YAMLFormatter(OutputFormatter):
    """YAML output formatter for test failure reports.
    
    This formatter produces human-readable YAML output with proper structure
    and formatting. YAML is often preferred over JSON for configuration files
    and human-readable data exchange due to its clean syntax and comment support.
    
    The formatter requires PyYAML as an optional dependency and will raise
    a helpful error message if the dependency is not installed.
    
    Features:
    - Clean, human-readable YAML structure
    - Metadata section with generation time and failure count
    - Structured failure data with proper YAML formatting
    - Helpful error message if PyYAML is not installed
    
    Example:
        >>> formatter = YAMLFormatter()
        >>> failures = [{'test_name': 'test_example', 'timestamp': '2024-01-01'}]
        >>> yaml_output = formatter.format(failures)
        >>> print(yaml_output[:50])
        test_failure_report:
          metadata:
            generated: 2024-01-01
    """

    def format(self, failures: List[Dict[str, Any]]) -> str:
        """Format failure data as YAML.
        
        Args:
            failures: List of failure dictionaries containing test failure information
            
        Returns:
            Human-readable YAML string with structured failure data
            
        Raises:
            ImportError: If PyYAML is not installed with helpful installation message
            
        Note:
            Structures data with metadata section and organized failure information.
            Uses PyYAML's default_flow_style=False for readable multi-line output.
        """
        try:
            import yaml
        except ImportError:
            raise ImportError(
                "PyYAML is required for YAML output format. "
                "Install it with: pip install failextract[formatters]"
            ) from None

        # Structure the data for YAML output
        output_data = {
            "test_failure_report": {
                "metadata": {
                    "generated": datetime.now().isoformat(),
                    "total_failures": len(failures),
                },
                "failures": [],
            }
        }

        for failure in failures:
            failure_data = {
                "test_info": {
                    "name": failure["test_name"],
                    "module": failure["test_module"],
                    "file": failure["test_file"],
                    "timestamp": failure["timestamp"],
                },
                "exception": {
                    "type": failure["exception_type"],
                    "message": failure["exception_message"],
                },
                "test_source": failure["test_source"],
            }

            # Add test arguments if present
            if failure.get("test_args") and failure["test_args"] != "()":
                failure_data["test_info"]["args"] = failure["test_args"]
            if failure.get("test_kwargs") and failure["test_kwargs"] != "{}":
                failure_data["test_info"]["kwargs"] = failure["test_kwargs"]

            # Add fixtures if present
            if failure.get("fixtures"):
                failure_data["fixtures"] = []
                for fixture in failure["fixtures"]:
                    fixture_data = {"name": fixture["name"], "type": fixture["type"]}
                    if fixture["type"] == "builtin":
                        fixture_data["description"] = fixture["description"]
                    else:
                        if fixture.get("scope"):
                            fixture_data["scope"] = fixture["scope"]
                        if fixture.get("file"):
                            fixture_data["file"] = fixture["file"]
                        if fixture.get("dependencies"):
                            fixture_data["dependencies"] = fixture["dependencies"]
                        if fixture.get("source"):
                            fixture_data["source"] = fixture["source"]
                    failure_data["fixtures"].append(fixture_data)

            # Add extracted code if present
            if failure.get("extracted_code"):
                failure_data["extracted_code"] = []
                for code in failure["extracted_code"]:
                    code_data = {
                        "file": code["file"],
                        "function": code["function"],
                        "line": code["line"],
                    }
                    if code.get("source"):
                        code_data["source"] = code["source"]
                    if code.get("class_source"):
                        code_data["class_source"] = code["class_source"]
                    if code.get("locals"):
                        code_data["locals"] = code["locals"]
                    failure_data["extracted_code"].append(code_data)

            # Add full traceback if present
            if failure.get("exception_traceback"):
                failure_data["exception"]["traceback"] = failure["exception_traceback"]

            output_data["test_failure_report"]["failures"].append(failure_data)

        return yaml.dump(
            output_data, default_flow_style=False, sort_keys=False, indent=2
        )

    def get_extension(self) -> str:
        """Get the file extension for YAML files.
        
        Returns:
            File extension '.yaml'
        """
        return ".yaml"