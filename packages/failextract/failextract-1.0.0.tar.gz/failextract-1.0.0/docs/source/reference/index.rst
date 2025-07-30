Reference Documentation
=======================

**Technical specifications and complete API documentation**

This reference provides detailed technical information about FailExtract's APIs, configuration options, and technical specifications. Use this section when you need precise details about classes, methods, parameters, and behavior.

.. toctree::
   :maxdepth: 3

   api

Quick Reference
---------------

**Core Classes**

- ``FailureExtractor`` - Main singleton for managing failure data
- ``OutputConfig`` - Configuration for report generation  
- ``@extract_on_failure`` - Primary decorator for failure capture

**Output Formats**

- ``json`` - Machine-readable JSON (always available)
- ``markdown`` - Human-readable Markdown (always available)
- ``xml`` - Structured XML data (always available)
- ``csv`` - Tabular CSV data (always available)
- ``yaml`` - YAML format (requires ``pip install failextract[formatters]``)

**Configuration Options**

.. list-table:: Decorator Configuration
   :header-rows: 1
   :widths: 25 15 60

   * - Parameter
     - Default
     - Description
   * - ``include_locals``
     - ``True``
     - Capture local variables in failure context
   * - ``include_fixtures``
     - ``True``
     - Capture pytest fixture values
   * - ``max_depth``
     - ``10``
     - Maximum depth for variable inspection
   * - ``skip_stdlib``
     - ``True``
     - Skip standard library stack frames
   * - ``extract_classes``
     - ``True``
     - Extract class instance details
   * - ``enhanced_context``
     - ``False``
     - Enhanced context analysis (experimental)
   * - ``code_context_lines``
     - ``5``
     - Lines of code context around failure point

**Memory Management**

.. list-table:: Memory Limits
   :header-rows: 1
   :widths: 25 25 50

   * - Parameter
     - Default
     - Description
   * - ``max_failures``
     - ``1000``
     - Maximum number of failures to store
   * - ``max_passed``
     - ``500``
     - Maximum number of passed tests to track

**Environment Variables**

.. list-table:: Environment Detection
   :header-rows: 1
   :widths: 25 75

   * - Variable
     - Purpose
   * - ``CI``
     - Detects CI/CD environment for performance optimization
   * - ``PYTEST_CURRENT_TEST``
     - Detects pytest execution context
   * - ``FAILEXTRACT_MODE``
     - Override performance mode (``development``, ``ci``, ``production``)

Common Patterns
---------------

**Basic Usage Pattern**

.. code-block:: python

   from failextract import extract_on_failure, FailureExtractor, OutputConfig

   @extract_on_failure
   def test_function():
       # Test code that might fail
       pass

   # Generate report
   extractor = FailureExtractor()
   config = OutputConfig("output.json", format="json")
   extractor.save_report(config)

**Environment-Aware Configuration**

.. code-block:: python

   import os
   from failextract import extract_on_failure

   # Configure based on environment
   is_ci = os.getenv("CI") == "true"
   
   config = {
       "include_locals": True,
       "max_depth": 8 if is_ci else 15,
       "skip_stdlib": is_ci
   }

   @extract_on_failure(**config)
   def test_with_env_config():
       pass

**Memory Management Pattern**

.. code-block:: python

   from failextract import FailureExtractor

   extractor = FailureExtractor()
   
   # Set appropriate limits
   extractor.set_memory_limits(
       max_failures=500,  # For CI environments
       max_passed=100
   )
   
   # Monitor usage
   stats = extractor.get_stats()
   if stats['failures_at_limit']:
       # Handle memory limit reached
       pass

**Error Handling Pattern**

.. code-block:: python

   from failextract import OutputConfig, FailureExtractor

   def safe_report_generation():
       extractor = FailureExtractor()
       
       # Try preferred format, fall back to JSON
       try:
           config = OutputConfig("report.yaml", format="yaml")
           extractor.save_report(config)
       except ImportError:
           config = OutputConfig("report.json", format="json")
           extractor.save_report(config)

Exit Codes and Return Values
----------------------------

**CLI Exit Codes**

- ``0`` - Success
- ``1`` - General error (invalid arguments, file errors)
- ``2`` - No data available for operation
- ``3`` - Permission/access errors

**Exception Hierarchy**

- ``ConfigurationError`` - Invalid configuration parameters
- ``IntegrationError`` - Errors during integration with external systems

Version Compatibility
----------------------

**Python Version Support**

- **Minimum**: Python 3.11
- **Recommended**: Python 3.11+
- **Tested**: Python 3.11, 3.12, 3.13

**Dependencies**

**Core (required)**
- None - FailExtract's core uses only Python standard library

**Optional extras**
- ``pyyaml>=6.0`` - For YAML formatter (``pip install failextract[formatters]``)
- ``tomli>=1.2.0`` - For TOML config support on Python < 3.11 (``pip install failextract[config]``)
- ``rich>=13.0`` - For enhanced CLI (``pip install failextract[cli]``)
- ``typer>=0.9`` - For advanced CLI features (``pip install failextract[cli]``)

Performance Characteristics
---------------------------

**Overhead by Mode**

.. list-table:: Performance Modes
   :header-rows: 1
   :widths: 20 15 15 50

   * - Mode
     - Overhead
     - Use Case
     - Configuration
   * - Static
     - <5%
     - Production
     - ``include_locals=False, max_depth=3``
   * - Profile
     - ~50%
     - CI/CD
     - ``include_locals=True, max_depth=8``
   * - Trace
     - ~300%
     - Development
     - ``include_locals=True, max_depth=20``

**Memory Usage**

- **Per failure**: ~2-10 KB depending on context captured
- **Per passed test**: ~0.5-1 KB if tracked
- **Default limits**: 1000 failures + 500 passed tests ≈ 2.5-10.5 MB

Technical Specifications
------------------------

**Data Formats**

**Failure Data Structure**

.. code-block:: python

   {
       "test_name": str,              # Test function name
       "test_module": str,            # Module containing test
       "test_file": str,              # File path
       "exception_type": str,         # Exception class name
       "exception_message": str,      # Exception message
       "timestamp": str,              # ISO format timestamp
       "local_variables": dict,       # Local variables (optional)
       "test_source": str,           # Source code (optional)
       "exception_traceback": str     # Stack trace (optional)
   }

**Passed Test Data Structure**

.. code-block:: python

   {
       "test_name": str,              # Test function name
       "test_module": str,            # Module containing test
       "timestamp": str,              # ISO format timestamp
       "duration": float              # Execution time (optional)
   }

**Thread Safety**

- ``FailureExtractor`` singleton is thread-safe
- Report generation is thread-safe
- Decorator application is thread-safe

**File Format Specifications**

.. list-table:: Output Format Details
   :header-rows: 1
   :widths: 15 25 60

   * - Format
     - MIME Type
     - Specification
   * - JSON
     - ``application/json``
     - RFC 7159 compliant JSON
   * - XML
     - ``application/xml``
     - Well-formed XML with UTF-8 encoding
   * - CSV
     - ``text/csv``
     - RFC 4180 compliant CSV
   * - Markdown
     - ``text/markdown``
     - CommonMark specification
   * - YAML
     - ``application/x-yaml``
     - YAML 1.2 specification

Migration Guides
----------------

**Upgrading to Version 2.x**

Major changes from 1.x:

- ``FailureExtractor`` is now a singleton (automatically managed)
- Optional features moved to separate installation extras
- CLI functionality requires ``[cli]`` extra
- YAML formatter requires ``[formatters]`` extra

**Backward Compatibility**

- All core APIs remain unchanged
- Configuration parameters unchanged  
- Report formats unchanged
- Decorator interface unchanged

See Also
--------

- :doc:`../tutorials/index` - Learn FailExtract step-by-step
- :doc:`../how-to/index` - Solve specific problems
- :doc:`../discussions/index` - Understand design decisions