Configuring FailExtract
=======================

**Purpose**: Learn to customize FailExtract behavior for your specific workflow

This tutorial covers configuration options, output customization, memory management, and error handling. By the end, you'll understand how to tailor FailExtract to your exact needs.

What You'll Learn
-----------------

- How to configure decorator behavior and output settings
- How to manage memory usage and performance trade-offs
- How to handle format detection and override capabilities
- How to set up session-level reporting workflows
- How to handle configuration errors gracefully

Prerequisites
-------------

- Completed :doc:`getting_started` and :doc:`multiple_formats`
- Understanding of Python configuration patterns
- 15 minutes of time

Configuration Overview
----------------------

FailExtract provides configuration at three levels:

1. **Decorator Level** - Configure individual test behavior
2. **Output Level** - Control report generation and formats  
3. **Session Level** - Manage global behavior and memory

Decorator Configuration
-----------------------

The ``@extract_on_failure`` decorator accepts several configuration options:

**Basic Configuration Options**

.. code-block:: python

   from failextract import extract_on_failure

   # 1. Default configuration (minimal overhead)
   @extract_on_failure
   def test_basic():
       assert 1 == 2, "Basic assertion failure"

   # 2. Specify output file directly
   @extract_on_failure("my_failures.json")
   def test_with_output():
       assert "hello" == "world", "String comparison failure"

   # 3. Detailed configuration
   @extract_on_failure(
       output="detailed_failures.json",
       include_locals=True,      # Capture local variables
       include_fixtures=True,    # Capture pytest fixtures  
       max_depth=15             # Maximum variable inspection depth
   )
   def test_detailed():
       local_var = {"user": "john", "active": True}
       assert local_var["active"] == False, "User should be inactive"

   # 4. Performance-optimized configuration
   @extract_on_failure(
       output="minimal_failures.json",
       include_locals=False,     # Skip local variables for speed
       skip_stdlib=True,        # Skip standard library frames
       extract_classes=False    # Skip class instance inspection
   )
   def test_minimal():
       data = [1, 2, 3, 4, 5]
       assert len(data) == 10, "Data length mismatch"

**Configuration Parameters Reference**

.. list-table:: Decorator Configuration Options
   :header-rows: 1
   :widths: 25 15 15 45

   * - Parameter
     - Type
     - Default
     - Description
   * - ``output``
     - ``str``
     - ``None``
     - Output filename (auto-detected format)
   * - ``include_locals``
     - ``bool``
     - ``True``
     - Capture local variables in failure context
   * - ``include_fixtures``
     - ``bool``
     - ``True``
     - Capture pytest fixture values
   * - ``max_depth``
     - ``int``
     - ``10``
     - Maximum depth for variable inspection
   * - ``skip_stdlib``
     - ``bool``
     - ``True``
     - Skip standard library stack frames
   * - ``extract_classes``
     - ``bool``
     - ``True``
     - Extract class instance details
   * - ``enhanced_context``
     - ``bool``
     - ``False``
     - Enhanced context analysis (experimental)
   * - ``code_context_lines``
     - ``int``
     - ``5``
     - Lines of code context around failure point

Output Configuration
--------------------

Use ``OutputConfig`` for precise control over report generation:

.. code-block:: python

   from failextract import OutputConfig, FailureExtractor

   # Basic configurations
   configs = [
       # 1. JSON with auto-detection
       OutputConfig("failures.json"),
       
       # 2. Markdown with explicit format
       OutputConfig("report.md", format="markdown"),
       
       # 3. Append mode for continuous reporting
       OutputConfig("ongoing.json", append=True),
       
       # 4. Limited report size
       OutputConfig("summary.json", max_failures=50),
       
       # 5. Format override (filename says .txt, format is JSON)
       OutputConfig("data.txt", format="json")
   ]

   # Generate reports with different configurations
   extractor = FailureExtractor()
   
   for config in configs:
       try:
           extractor.save_report(config)
           print(f"✓ Generated {config.filename} ({config.format.value})")
       except Exception as e:
           print(f"✗ Failed {config.filename}: {e}")

**Output Configuration Parameters**

.. list-table:: OutputConfig Parameters
   :header-rows: 1
   :widths: 25 15 15 45

   * - Parameter
     - Type
     - Default
     - Description
   * - ``filename``
     - ``str``
     - Required
     - Output file path (format auto-detected from extension)
   * - ``format``
     - ``str|OutputFormat``
     - Auto-detect
     - Force specific format (overrides filename detection)
   * - ``append``
     - ``bool``
     - ``False``
     - Append to existing file instead of overwriting
   * - ``max_failures``
     - ``int``
     - ``None``
     - Limit number of failures included in report

Format Detection and Override
-----------------------------

FailExtract automatically detects output format from file extensions:

.. code-block:: python

   from failextract import OutputConfig

   # Automatic format detection examples
   format_examples = {
       "report.json": "json",
       "failures.md": "markdown", 
       "data.csv": "csv",
       "config.yaml": "yaml",
       "integration.xml": "xml",
       "unknown.txt": "json"  # Defaults to JSON
   }

   print("Format Detection Examples:")
   for filename, expected in format_examples.items():
       config = OutputConfig(filename)
       actual = config.format.value
       status = "✓" if actual == expected else "✗"
       print(f"  {status} {filename:15} -> {actual}")

**Format Override Example**

Sometimes you need to override automatic detection:

.. code-block:: python

   # These configurations override filename-based detection
   overrides = [
       OutputConfig("data.log", format="json"),      # .log file with JSON content
       OutputConfig("backup.bak", format="yaml"),    # .bak file with YAML content
       OutputConfig("report", format="markdown")     # No extension, explicit format
   ]

   for config in overrides:
       print(f"File: {config.filename} -> Format: {config.format.value}")

Memory Management Configuration
-------------------------------

Control memory usage for long-running test suites:

.. code-block:: python

   from failextract import FailureExtractor

   def configure_memory_management():
       extractor = FailureExtractor()
       
       # Check current state
       stats = extractor.get_stats()
       limits = extractor.get_memory_limits()
       
       print("Initial State:")
       print(f"  Failures: {stats['failures_count']}")
       print(f"  Passed: {stats['passed_count']}")
       print(f"  Max failures limit: {limits['max_failures']}")
       print(f"  Max passed limit: {limits['max_passed']}")
       
       # Set memory limits to prevent excessive memory usage
       extractor.set_memory_limits(max_failures=1000, max_passed=500)
       
       print("\\nAfter Setting Limits:")
       limits = extractor.get_memory_limits()
       print(f"  Max failures limit: {limits['max_failures']}")
       print(f"  Max passed limit: {limits['max_passed']}")
       
       # Monitor usage as tests run
       for i in range(5):
           # Simulate adding test results
           extractor.add_failure({
               "test_name": f"test_failure_{i}",
               "timestamp": f"2025-06-06T12:0{i}:00",
               "exception_message": f"Demo failure {i}"
           })
           
           extractor.add_passed({
               "test_name": f"test_passed_{i}",
               "timestamp": f"2025-06-06T12:0{i}:30"
           })
       
       # Check final state
       final_stats = extractor.get_stats()
       print("\\nFinal State:")
       print(f"  Failures: {final_stats['failures_count']}")
       print(f"  Passed: {final_stats['passed_count']}")
       print(f"  At failure limit: {final_stats['failures_at_limit']}")

**Memory Management Guidelines**

- Set ``max_failures`` based on available memory and report requirements
- Set ``max_passed`` lower than ``max_failures`` (passed tests need less detail)
- Monitor memory usage in long-running CI/CD environments
- Use ``clear()`` method to reset between test sessions

Session-Level Reporting
-----------------------

Configure session-wide behavior for comprehensive reporting:

.. code-block:: python

   from failextract import generate_session_report
   import tempfile
   from pathlib import Path

   def setup_session_reporting():
       # 1. Generate session report with defaults
       generate_session_report("session_summary.md")
       
       # 2. Generate comprehensive Markdown report
       generate_session_report("session_report.md", format="markdown")
       
       # 3. Generate JSON data without clearing session
       generate_session_report("session_data.json", format="json", clear=False)
       
       # 4. Generate multiple session reports
       session_formats = ["json", "markdown", "csv"]
       for fmt in session_formats:
           filename = f"session_report.{fmt}"
           try:
               generate_session_report(filename, format=fmt)
               print(f"✓ Generated {filename}")
           except Exception as e:
               print(f"✗ Failed {filename}: {e}")

**Session Reporting Parameters**

.. list-table:: Session Reporting Options
   :header-rows: 1
   :widths: 25 15 45

   * - Parameter
     - Type
     - Description
   * - ``filename``
     - ``str``
     - Output file path
   * - ``format``
     - ``str``
     - Output format (auto-detected if not specified)
   * - ``clear``
     - ``bool``
     - Clear session data after generating report (default: ``True``)

Performance Configuration Patterns
----------------------------------

Choose configuration patterns based on your performance requirements:

.. code-block:: python

   # 1. DEVELOPMENT MODE: Maximum detail, slower but comprehensive
   @extract_on_failure(
       include_locals=True,
       include_fixtures=True,
       max_depth=20,
       extract_classes=True,
       skip_stdlib=False
   )
   def test_development_mode():
       # Detailed capture for debugging
       pass

   # 2. CI/CD MODE: Balanced detail and performance  
   @extract_on_failure(
       include_locals=True,
       include_fixtures=False,
       max_depth=10,
       extract_classes=True,
       skip_stdlib=True
   )
   def test_ci_mode():
       # Good balance for automated environments
       pass

   # 3. PRODUCTION MODE: Minimal overhead, basic information
   @extract_on_failure(
       include_locals=False,
       include_fixtures=False,
       max_depth=5,
       extract_classes=False,
       skip_stdlib=True
   )
   def test_production_mode():
       # Fast capture for production monitoring
       pass

**Performance Mode Comparison**

.. list-table:: Performance vs Detail Trade-offs
   :header-rows: 1
   :widths: 20 15 15 50

   * - Mode
     - Overhead
     - Detail Level
     - Best Use Case
   * - Development
     - ~300%
     - Maximum
     - Local debugging, deep investigation
   * - CI/CD
     - ~50%
     - Balanced
     - Automated testing, build pipelines
   * - Production
     - <5%
     - Minimal
     - Production monitoring, health checks

Error Handling and Validation
-----------------------------

Handle configuration errors gracefully:

.. code-block:: python

   from failextract import OutputConfig

   def handle_configuration_errors():
       print("Testing Configuration Error Handling:")
       
       # 1. Test invalid format
       try:
           config = OutputConfig("test.txt", format="invalid_format")
       except ValueError as e:
           print(f"✓ Caught invalid format: {e}")
       
       # 2. Test negative max_failures
       try:
           config = OutputConfig("test.json", max_failures=-1)
       except ValueError as e:
           print(f"✓ Caught negative max_failures: {e}")
       
       # 3. Test type errors
       try:
           config = OutputConfig("test.json", append="not_a_bool")
       except TypeError as e:
           print(f"✓ Caught type error: {e}")
       
       # 4. Safe configuration with fallbacks
       def safe_config(filename, format=None, **kwargs):
           try:
               return OutputConfig(filename, format=format, **kwargs)
           except ValueError as e:
               print(f"⚠ Configuration error: {e}")
               return OutputConfig(filename)  # Use defaults
           except Exception as e:
               print(f"✗ Unexpected error: {e}")
               return None
       
       # Test safe configuration
       configs = [
           safe_config("good.json"),                    # Valid
           safe_config("bad.txt", format="invalid"),    # Invalid format
           safe_config("negative.json", max_failures=-1) # Invalid parameter
       ]
       
       valid_configs = [c for c in configs if c is not None]
       print(f"Created {len(valid_configs)} valid configurations")

Complete Configuration Example
------------------------------

Here's a complete example showing all configuration concepts:

.. code-block:: python

   #!/usr/bin/env python3
   """Complete FailExtract configuration example"""
   
   from failextract import (
       extract_on_failure, FailureExtractor, OutputConfig,
       generate_session_report
   )
   from pathlib import Path

   # Configure different test modes
   @extract_on_failure(include_locals=True, max_depth=15)
   def test_detailed_failure():
       config = {"api_key": "secret", "timeout": 30}
       response = {"status": "error", "code": 500}
       assert response["status"] == "success", f"API failed: {response}"

   @extract_on_failure(include_locals=False, skip_stdlib=True)
   def test_minimal_failure():
       data = [1, 2, 3]
       assert len(data) == 5, "Wrong data length"

   def setup_comprehensive_reporting():
       # Run tests to generate failures
       try:
           test_detailed_failure()
       except AssertionError:
           pass
       
       try:
           test_minimal_failure()
       except AssertionError:
           pass
       
       # Configure multiple output formats
       extractor = FailureExtractor()
       
       # Set memory limits for production use
       extractor.set_memory_limits(max_failures=1000, max_passed=500)
       
       # Generate reports with different configurations
       configs = [
           OutputConfig("detailed_report.json"),
           OutputConfig("summary.md", format="markdown"),
           OutputConfig("data_analysis.csv", format="csv"),
           OutputConfig("continuous.json", append=True, max_failures=10),
       ]
       
       for config in configs:
           try:
               extractor.save_report(config)
               print(f"✓ Generated {config.filename}")
           except Exception as e:
               print(f"✗ Failed {config.filename}: {e}")
       
       # Generate session report
       generate_session_report("session_summary.md")
       
       # Display statistics
       stats = extractor.get_stats()
       print(f"\\nSession Statistics:")
       print(f"  Total failures: {stats['failures_count']}")
       print(f"  Total passed: {stats['passed_count']}")
       print(f"  Memory usage: {stats['total_count']} tests tracked")

   if __name__ == "__main__":
       setup_comprehensive_reporting()

Environment-Specific Configuration
----------------------------------

Adapt configuration to different environments:

.. code-block:: python

   import os
   from failextract import extract_on_failure

   # Detect environment
   env = os.getenv("ENVIRONMENT", "development").lower()

   if env == "production":
       # Minimal overhead for production
       decorator_config = {
           "include_locals": False,
           "skip_stdlib": True,
           "max_depth": 3
       }
   elif env == "ci":
       # Balanced for CI/CD
       decorator_config = {
           "include_locals": True,
           "skip_stdlib": True,
           "max_depth": 8
       }
   else:
       # Full detail for development
       decorator_config = {
           "include_locals": True,
           "skip_stdlib": False,
           "max_depth": 15
       }

   # Apply environment-specific configuration
   @extract_on_failure(**decorator_config)
   def test_environment_aware():
       # This test adapts its behavior based on environment
       assert False, f"Test running in {env} mode"

Next Steps
----------

Now that you understand configuration, you can:

- **Integrate with pytest**: :doc:`pytest_integration` - Set up automatic test suite integration
- **Create Custom Formatters**: :doc:`custom_formatters` - Build specialized output formats
- **Optimize for CI/CD**: Learn advanced patterns for continuous integration
- **Monitor Production**: Set up lightweight production failure monitoring

Key Configuration Takeaways
----------------------------

| ✅ **Decorator configuration** controls capture behavior and performance  
| ✅ **Output configuration** manages report generation and formats  
| ✅ **Memory management** prevents resource issues in long-running suites  
| ✅ **Session reporting** provides comprehensive overview capabilities  
| ✅ **Error handling** ensures graceful configuration failures  
| ✅ **Environment adaptation** tailors behavior to deployment context  

**You now have complete control over FailExtract behavior!**