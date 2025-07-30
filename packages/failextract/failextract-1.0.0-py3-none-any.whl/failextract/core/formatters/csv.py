"""CSV output formatter for test failure reports.

This module provides CSV formatting capabilities for test failure data.
CSV output is ideal for importing into spreadsheet applications, performing
data analysis, and creating tabular reports from test failure information.
"""

import csv
import io
from typing import List, Dict, Any

from .base import OutputFormatter


class CSVFormatter(OutputFormatter):
    """CSV output formatter for test failure reports.
    
    This formatter produces comma-separated values output suitable for
    spreadsheet applications, data analysis tools, and tabular reporting.
    The CSV format includes essential test failure information in a
    structured tabular format.
    
    The CSV includes these columns:
    - Test Name: Name of the failed test
    - Module: Python module containing the test
    - File: File path where the test is located
    - Timestamp: When the failure occurred
    - Exception Type: Type of exception raised
    - Exception Message: Error message from the exception
    - Line Number: Line number where failure occurred (if available)
    
    Example:
        >>> formatter = CSVFormatter()
        >>> failures = [{'test_name': 'test_example', 'test_module': 'test_mod'}]
        >>> csv_output = formatter.format(failures)
        >>> print(csv_output.split('\\n')[0])
        Test Name,Module,File,Timestamp,Exception Type,Exception Message,Line Number
    """

    def format(self, failures: List[Dict[str, Any]]) -> str:
        """Format failure data as CSV.
        
        Args:
            failures: List of failure dictionaries containing test failure information
            
        Returns:
            CSV-formatted string with headers and failure data rows
            
        Note:
            Uses Python's csv module for proper escaping and formatting.
            Extracts line numbers from extracted_code if available.
        """
        output = io.StringIO()
        writer = csv.writer(output)

        # Header
        writer.writerow(
            [
                "Test Name",
                "Module",
                "File",
                "Timestamp",
                "Exception Type",
                "Exception Message",
                "Line Number",
            ]
        )

        # Data rows
        for failure in failures:
            # Get first line number from extracted code
            line_no = ""
            if failure.get("extracted_code"):
                line_no = str(failure["extracted_code"][0].get("line", ""))

            writer.writerow(
                [
                    failure["test_name"],
                    failure["test_module"],
                    failure["test_file"],
                    failure["timestamp"],
                    failure["exception_type"],
                    failure["exception_message"],
                    line_no,
                ]
            )

        return output.getvalue()

    def get_extension(self) -> str:
        """Get the file extension for CSV files.
        
        Returns:
            File extension '.csv'
        """
        return ".csv"