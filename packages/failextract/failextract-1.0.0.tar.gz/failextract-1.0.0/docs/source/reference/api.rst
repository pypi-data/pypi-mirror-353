API Reference
=============

Complete reference documentation for all FailExtract classes, functions, and interfaces.

.. note::
   
   FailExtract follows a progressive enhancement model. Core functionality is always available, with optional features providing additional capabilities.

Main Module
-----------

.. automodule:: failextract
   :members:
   :undoc-members:
   :show-inheritance:

Core Classes
------------

FailureExtractor
~~~~~~~~~~~~~~~~

The main singleton class for managing failure data throughout a session.

.. autoclass:: failextract.FailureExtractor
   :members:
   :undoc-members:
   :show-inheritance:

FixtureExtractor  
~~~~~~~~~~~~~~~~

Specialized extractor for pytest fixture analysis.

.. autoclass:: failextract.FixtureExtractor
   :members:
   :undoc-members:
   :show-inheritance:

OutputConfig
~~~~~~~~~~~~

Configuration class for report generation.

.. autoclass:: failextract.OutputConfig
   :members:
   :undoc-members:
   :show-inheritance:

Decorators and Functions
------------------------

extract_on_failure
~~~~~~~~~~~~~~~~~~~

Primary decorator for automatic failure capture.

.. autofunction:: failextract.extract_on_failure

generate_session_report
~~~~~~~~~~~~~~~~~~~~~~~

Utility function for session-level reporting.

.. autofunction:: failextract.generate_session_report

Enums and Types
---------------

OutputFormat
~~~~~~~~~~~~

Enumeration of supported output formats.

.. autoclass:: failextract.OutputFormat
   :members:
   :undoc-members:
   :show-inheritance:

Formatter Classes
-----------------

Base Formatter
~~~~~~~~~~~~~~

.. autoclass:: failextract.OutputFormatter
   :members:
   :undoc-members:
   :show-inheritance:

JSON Formatter
~~~~~~~~~~~~~~

.. autoclass:: failextract.JSONFormatter
   :members:
   :undoc-members:
   :show-inheritance:

Markdown Formatter
~~~~~~~~~~~~~~~~~~

.. autoclass:: failextract.MarkdownFormatter
   :members:
   :undoc-members:
   :show-inheritance:

XML Formatter
~~~~~~~~~~~~~

.. autoclass:: failextract.XMLFormatter
   :members:
   :undoc-members:
   :show-inheritance:

CSV Formatter
~~~~~~~~~~~~~

.. autoclass:: failextract.CSVFormatter
   :members:
   :undoc-members:
   :show-inheritance:

YAML Formatter (Optional)
~~~~~~~~~~~~~~~~~~~~~~~~~

Available with ``pip install failextract[formatters]``:

.. autoclass:: failextract.YAMLFormatter
   :members:
   :undoc-members:
   :show-inheritance:

Configuration Classes
---------------------

Configuration system is always available as part of core functionality:

.. autoclass:: failextract.ConfigurationManager
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: failextract.ProjectConfig
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: failextract.WorkspaceDetector
   :members:
   :undoc-members:
   :show-inheritance:

CLI Module
----------

Command-line interface is always available as part of core functionality:

.. automodule:: failextract.cli
   :members:
   :undoc-members:
   :show-inheritance:


Exception Classes
-----------------

Base Exceptions
~~~~~~~~~~~~~~~

.. autoexception:: failextract.ConfigurationError
   :members:
   :show-inheritance:

Constants and Settings
----------------------

Version Information
~~~~~~~~~~~~~~~~~~~

.. autodata:: failextract.__version__

Built-in Fixtures
~~~~~~~~~~~~~~~~~~

.. autodata:: failextract.BUILTIN_FIXTURES

Feature Detection
-----------------

Runtime Feature Detection
~~~~~~~~~~~~~~~~~~~~~~~~~~

Check what features are available in the current installation:

.. code-block:: python

   from failextract import get_available_features
   
   features = get_available_features()
   print(f"Available features: {features['available']}")
   print(f"Missing features: {features['missing']}")
   print(f"Core features: {features['core']}")

Installation Suggestions
~~~~~~~~~~~~~~~~~~~~~~~~~

Get installation commands for missing features:

.. code-block:: python

   from failextract import suggest_installation
   
   # Suggest installation for YAML support
   suggestion = suggest_installation("yaml")
   print(suggestion)  # "pip install failextract[formatters]"

Utilities and Helpers
---------------------

Context Analysis
~~~~~~~~~~~~~~~~

.. autoclass:: failextract.CodeContextExtractor
   :members:
   :undoc-members:
   :show-inheritance:

Registry Management
~~~~~~~~~~~~~~~~~~~

.. autofunction:: failextract.get_available_features

.. autofunction:: failextract.suggest_installation

Examples
--------

**Basic Usage Example:**

.. code-block:: python

   from failextract import extract_on_failure, FailureExtractor, OutputConfig

   @extract_on_failure
   def test_example():
       assert 1 == 2, "This will fail and be captured"

   # Run test (it will fail and be captured)
   try:
       test_example()
   except AssertionError:
       pass

   # Generate report
   extractor = FailureExtractor()
   config = OutputConfig("failures.json", format="json")
   extractor.save_report(config)

**Advanced Configuration Example:**

.. code-block:: python

   from failextract import extract_on_failure

   @extract_on_failure(
       include_locals=True,        # Capture local variables
       include_fixtures=True,      # Capture pytest fixtures  
       max_depth=15,              # Variable inspection depth
       skip_stdlib=False,         # Include all stack frames
       enhanced_context=True,     # Enhanced context analysis
       code_context_lines=10      # Lines of code context
   )
   def test_detailed():
       user_data = {"id": 123, "name": "Alice"}
       config = {"timeout": 30, "retries": 3}
       assert False, "Detailed context will be captured"

**Memory Management Example:**

.. code-block:: python

   from failextract import FailureExtractor

   extractor = FailureExtractor()
   
   # Set memory limits
   extractor.set_memory_limits(max_failures=500, max_passed=100)
   
   # Check usage
   stats = extractor.get_stats()
   print(f"Usage: {stats['failures_count']} failures, {stats['passed_count']} passed")

**CLI Usage Examples:**

.. code-block:: bash

   # Generate different format reports
   failextract report --format json --output failures.json
   failextract report --format markdown --output failures.md
   failextract report --format csv --output failures.csv
   failextract report --format yaml --output failures.yaml
   failextract report --format xml --output failures.xml
   
   # List captured failures
   failextract list --format table
   failextract list --format json
   
   # Show statistics and analysis
   failextract stats --format table
   failextract stats --format json
   
   # Check available features
   failextract features --format table
   
   # Clear all data
   failextract clear --confirm
   
   # Advanced analysis (if analytics extra installed)
   # failextract analyze --trends --days 30

Error Handling
--------------

**Import Error Handling:**

.. code-block:: python

   try:
       from failextract import extract_on_failure
   except ImportError as e:
       print(f"FailExtract not available: {e}")
       print("Install with: pip install failextract")

**Feature Availability Checking:**

.. code-block:: python

   from failextract import OutputConfig, FailureExtractor
   
   def safe_yaml_report():
       """Generate YAML report if possible, JSON otherwise."""
       extractor = FailureExtractor()
       
       try:
           config = OutputConfig("report.yaml", format="yaml")
           extractor.save_report(config)
           print("Generated YAML report")
       except ImportError:
           print("YAML not available, generating JSON instead")
           config = OutputConfig("report.json", format="json")
           extractor.save_report(config)

**Configuration Error Handling:**

.. code-block:: python

   from failextract import OutputConfig, ConfigurationError
   
   try:
       config = OutputConfig("invalid.txt", format="unsupported_format")
   except ValueError as e:  # OutputConfig raises ValueError for invalid parameters
       print(f"Configuration error: {e}")
       # Fall back to default
       config = OutputConfig("backup.json")

Migration Notes
---------------

**From Version 1.x to 2.x:**

- ``FailureExtractor`` is now a singleton
- ``OutputConfig`` constructor has simplified parameters
- YAML formatter moved to optional ``[formatters]`` extra
- CLI moved to optional ``[cli]`` extra

**Backward Compatibility:**

- All core APIs remain compatible
- Optional features gracefully degrade if not installed
- Configuration format remains unchanged

See Also
--------

- :doc:`../tutorials/index` - Step-by-step learning guides
- :doc:`../how-to/index` - Task-focused solutions
- :doc:`../discussions/index` - In-depth design discussions