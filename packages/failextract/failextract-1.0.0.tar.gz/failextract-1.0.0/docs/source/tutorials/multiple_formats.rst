Working with Multiple Output Formats
=====================================

**Purpose**: Learn to generate reports in different formats for different workflows

This tutorial shows you how to generate failure reports in JSON, Markdown, XML, CSV, and YAML formats. Each format serves different use cases in your development workflow.

What You'll Learn
-----------------

- How to generate reports in all 5 supported formats
- When to use each format in your workflow
- How to handle optional format dependencies
- How to automate multi-format report generation

Prerequisites
-------------

- Completed :doc:`getting_started`
- Understanding of different data formats (JSON, XML, CSV, etc.)
- 10 minutes of time

Format Overview
---------------

FailExtract supports 5 output formats, each optimized for different use cases:

.. list-table:: Supported Output Formats
   :header-rows: 1
   :widths: 15 15 40 15 15

   * - Format
     - Extension
     - Best For
     - Dependencies
     - Core Feature
   * - JSON
     - ``.json``
     - Automation, APIs, machine processing
     - None
     - ✅ Yes
   * - Markdown
     - ``.md``
     - Documentation, GitHub, human reading
     - None
     - ✅ Yes
   * - XML
     - ``.xml``
     - Structured data, enterprise systems
     - None
     - ✅ Yes
   * - CSV
     - ``.csv``
     - Spreadsheets, data analysis, Excel
     - None
     - ✅ Yes
   * - YAML
     - ``.yaml``
     - Configuration, Docker, CI/CD
     - ``pyyaml``
     - ❌ Optional

Setting Up Example Failures
----------------------------

Let's create some realistic test failures to demonstrate format differences:

.. code-block:: python

   from failextract import extract_on_failure, FailureExtractor, OutputConfig

   @extract_on_failure
   def test_database_connection():
       """Simulate a database connection test failure."""
       connection_string = "postgresql://user:pass@localhost:5432/testdb"
       connected = False  # Simulate connection failure
       
       assert connected, f"Failed to connect to database: {connection_string}"

   @extract_on_failure
   def test_api_response():
       """Simulate an API response validation failure."""
       api_response = {
           'status': 'error',
           'code': 500,
           'message': 'Internal server error',
           'data': None
       }
       
       assert api_response['status'] == 'success', f"API returned error: {api_response}"

   @extract_on_failure
   def test_file_processing():
       """Simulate a file processing failure."""
       file_path = "/data/important_file.csv"
       file_exists = False  # Simulate missing file
       
       assert file_exists, f"Required file not found: {file_path}"

Generate Reports in All Formats
--------------------------------

Here's how to generate reports in every supported format:

.. code-block:: python

   def generate_all_formats():
       """Generate reports in all supported formats."""
       extractor = FailureExtractor()
       
       if not extractor.failures:
           print("No failures to report")
           return
       
       # Format definitions: (format_name, description)
       formats = [
           ("json", "Machine-readable JSON format"),
           ("markdown", "Markdown format for documentation"),
           ("xml", "XML format for structured data"),
           ("csv", "CSV format for spreadsheet analysis"),
           ("yaml", "YAML format for configuration-like output")
       ]
       
       print(f"Generating reports for {len(extractor.failures)} failures...")
       
       for format_name, description in formats:
           try:
               config = OutputConfig(f"failures.{format_name}", format=format_name)
               extractor.save_report(config)
               print(f"✓ Generated failures.{format_name} - {description}")
           except Exception as e:
               print(f"✗ Failed to generate {format_name}: {e}")

Complete Working Example
------------------------

Save this as ``multiple_formats_example.py``:

.. code-block:: python

   #!/usr/bin/env python3
   """Multiple format generation example"""
   
   from failextract import extract_on_failure, FailureExtractor, OutputConfig

   @extract_on_failure
   def test_database_connection():
       connection_string = "postgresql://user:pass@localhost:5432/testdb"
       connected = False
       assert connected, f"Failed to connect to database: {connection_string}"

   @extract_on_failure
   def test_api_response():
       api_response = {
           'status': 'error', 'code': 500,
           'message': 'Internal server error', 'data': None
       }
       assert api_response['status'] == 'success', f"API returned error: {api_response}"

   @extract_on_failure
   def test_file_processing():
       file_path = "/data/important_file.csv"
       file_exists = False
       assert file_exists, f"Required file not found: {file_path}"

   def run_tests_and_generate_reports():
       # Run the failing tests
       tests = [test_database_connection, test_api_response, test_file_processing]
       
       for test_func in tests:
           try:
               test_func()
           except AssertionError:
               pass  # Expected to fail
       
       # Generate all format reports
       extractor = FailureExtractor()
       formats = ["json", "markdown", "xml", "csv", "yaml"]
       
       for format_name in formats:
           try:
               config = OutputConfig(f"failures.{format_name}", format=format_name)
               extractor.save_report(config)
               print(f"✓ Generated failures.{format_name}")
           except Exception as e:
               print(f"✗ Failed to generate {format_name}: {e}")

   if __name__ == "__main__":
       run_tests_and_generate_reports()

Run the example:

.. code-block:: bash

   python multiple_formats_example.py

Expected output:

.. code-block:: text

   ✓ Generated failures.json
   ✓ Generated failures.markdown
   ✓ Generated failures.xml
   ✓ Generated failures.csv
   ✗ Failed to generate yaml: No module named 'yaml'

Understanding Each Format
--------------------------

**JSON Format (failures.json)**

Machine-readable, perfect for automation:

.. code-block:: json

   [
     {
       "test_name": "test_database_connection",
       "exception_type": "AssertionError", 
       "exception_message": "Failed to connect to database: postgresql://user:pass@localhost:5432/testdb",
       "timestamp": "2025-06-06T09:30:15.123456",
       "local_variables": {
         "connection_string": "postgresql://user:pass@localhost:5432/testdb",
         "connected": false
       }
     }
   ]

**Markdown Format (failures.markdown)**

Human-readable, perfect for documentation:

.. code-block:: markdown

   # Test Failures Report
   
   Generated on: 2025-06-06 09:30:15
   
   ## test_database_connection
   
   **Exception:** AssertionError  
   **Message:** Failed to connect to database: postgresql://user:pass@localhost:5432/testdb

**XML Format (failures.xml)**

Structured data, perfect for enterprise systems:

.. code-block:: xml

   <?xml version="1.0" encoding="UTF-8"?>
   <testFailureReport>
     <metadata>
       <generated>2025-06-06T09:30:15.123456</generated>
       <totalFailures>1</totalFailures>
     </metadata>
     <failures>
       <failure>
         <testName>test_database_connection</testName>
         <module>__main__</module>
         <file>/path/to/test.py</file>
         <timestamp>2025-06-06T09:30:15.123456</timestamp>
         <exceptionType>AssertionError</exceptionType>
         <exceptionMessage>Failed to connect to database: postgresql://user:pass@localhost:5432/testdb</exceptionMessage>
         <testSource><![CDATA[
def test_database_connection():
    connection_string = "postgresql://user:pass@localhost:5432/testdb"
    connected = False
    assert connected, f"Failed to connect to database: {connection_string}"
         ]]></testSource>
       </failure>
     </failures>
   </testFailureReport>

**CSV Format (failures.csv)**

Tabular data, perfect for spreadsheet analysis:

.. code-block:: text

   Test Name,Module,File,Timestamp,Exception Type,Exception Message,Line Number
   test_database_connection,__main__,/path/to/test.py,2025-06-06T09:30:15.123456,AssertionError,"Failed to connect to database: postgresql://user:pass@localhost:5432/testdb",

**YAML Format (failures.yaml)**

Configuration-style, perfect for CI/CD:

.. code-block:: yaml

   test_failure_report:
     metadata:
       generated: 2025-06-06T09:30:15.123456
       total_failures: 1
     failures:
       - test_info:
           name: test_database_connection
           module: __main__
           file: /path/to/test.py
           timestamp: 2025-06-06T09:30:15.123456
         exception:
           type: AssertionError
           message: "Failed to connect to database: postgresql://user:pass@localhost:5432/testdb"
         test_source: |
           def test_database_connection():
               connection_string = "postgresql://user:pass@localhost:5432/testdb"
               connected = False
               assert connected, f"Failed to connect to database: {connection_string}"

Adding YAML Support
--------------------

YAML requires an optional dependency. Install it with:

.. code-block:: bash

   # Option 1: Install with YAML support
   pip install failextract[formatters]
   
   # Option 2: Install YAML library separately  
   pip install pyyaml

After installation, the YAML format will work without errors.

Workflow-Specific Format Recommendations
-----------------------------------------

**Development Workflow**
   Use **Markdown** for quick human review and **JSON** for automation

**CI/CD Pipeline**
   Use **JSON** for parsing and **CSV** for artifact storage

**Bug Reports**
   Use **Markdown** for GitHub issues and **JSON** for detailed context

**Data Analysis**
   Use **CSV** for Excel/spreadsheet analysis

**Configuration Management**
   Use **YAML** for infrastructure-as-code integration

Handling Format Errors Gracefully
----------------------------------

Always handle potential format generation errors:

.. code-block:: python

   def safe_format_generation():
       extractor = FailureExtractor()
       
       # Core formats (always available)
       core_formats = ["json", "markdown", "xml", "csv"]
       
       # Optional formats (may require dependencies)
       optional_formats = ["yaml"]
       
       # Generate core formats
       for format_name in core_formats:
           config = OutputConfig(f"failures.{format_name}", format=format_name)
           extractor.save_report(config)
           print(f"✓ Generated {format_name}")
       
       # Try optional formats
       for format_name in optional_formats:
           try:
               config = OutputConfig(f"failures.{format_name}", format=format_name)
               extractor.save_report(config)
               print(f"✓ Generated {format_name}")
           except ImportError as e:
               print(f"⚠ Skipped {format_name}: {e}")
           except Exception as e:
               print(f"✗ Failed {format_name}: {e}")

Automating Multi-Format Reports
--------------------------------

Create a utility function for consistent multi-format generation:

.. code-block:: python

   def create_comprehensive_report(base_filename="failures"):
       """Generate failure reports in all available formats."""
       extractor = FailureExtractor()
       
       if not extractor.failures:
           print("No failures to report")
           return []
       
       generated_files = []
       formats = ["json", "markdown", "xml", "csv", "yaml"]
       
       for format_name in formats:
           try:
               filename = f"{base_filename}.{format_name}"
               config = OutputConfig(filename, format=format_name)
               extractor.save_report(config)
               generated_files.append(filename)
               print(f"✓ {filename}")
           except Exception as e:
               print(f"⚠ Skipped {format_name}: {e}")
       
       return generated_files

Next Steps
----------

Now that you understand multiple formats, you can:

- **Configure Behavior**: :doc:`configuration` - Customize output paths and format options
- **Integrate with pytest**: :doc:`pytest_integration` - Automate multi-format generation in test suites  
- **Create Custom Formatters**: :doc:`custom_formatters` - Build your own output formats
- **Set Up CI/CD**: Learn how to automate format generation in your deployment pipeline

Key Takeaways
-------------

| ✅ **Core formats** (JSON, Markdown, XML, CSV) always work  
| ✅ **YAML format** requires ``pip install failextract[formatters]``  
| ✅ **Each format** serves different workflow needs  
| ✅ **Error handling** ensures graceful degradation  
| ✅ **Automation** makes multi-format generation routine  

**You now have flexible reporting for any workflow!**