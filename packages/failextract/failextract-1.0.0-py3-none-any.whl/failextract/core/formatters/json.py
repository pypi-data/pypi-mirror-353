"""JSON output formatter for test failure reports.

This module provides JSON formatting capabilities for test failure data.
JSON is the core format that is always available in FailExtract and serves
as the foundation for machine-readable output.
"""

import json
from typing import List, Dict, Any

from .base import OutputFormatter


class JSONFormatter(OutputFormatter):
    """JSON output formatter for test failure reports.
    
    This formatter produces structured JSON output suitable for programmatic
    processing, integration with tools, and serving as input for other
    processing systems. The JSON format is always available in FailExtract
    and does not require any optional dependencies.
    
    The output includes full test failure information with proper JSON
    serialization handling for Python-specific types like datetime objects.
    
    Example:
        >>> formatter = JSONFormatter()
        >>> failures = [{'test_name': 'test_example', 'timestamp': '2024-01-01'}]
        >>> json_output = formatter.format(failures)
        >>> print(json_output)
        [
          {
            "test_name": "test_example",
            "timestamp": "2024-01-01"
          }
        ]
    """

    def format(self, failures: List[Dict[str, Any]]) -> str:
        """Format failure data as JSON.
        
        Args:
            failures: List of failure dictionaries containing test failure information
            
        Returns:
            Pretty-formatted JSON string with 2-space indentation
            
        Note:
            Uses json.dumps with default=str to handle non-serializable types
            like datetime objects by converting them to strings.
        """
        return json.dumps(failures, indent=2, default=str)

    def get_extension(self) -> str:
        """Get the file extension for JSON files.
        
        Returns:
            File extension '.json'
        """
        return ".json"