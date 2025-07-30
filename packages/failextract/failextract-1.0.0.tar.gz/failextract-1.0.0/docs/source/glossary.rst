Glossary
========

.. glossary::

   decorator
      A Python decorator that wraps a function to add functionality. In FailExtract, the :func:`extract_on_failure` decorator wraps test functions to automatically capture failure information.

   fixture
      A pytest feature that provides reusable test data, setup, and teardown functionality. FailExtract can automatically extract fixture information during test failures.

   formatter
      A component that converts test failure data into specific output formats like JSON, XML, CSV, Markdown, or YAML.

   output format
      The format in which test failure reports are generated. FailExtract supports multiple formats including JSON (always available), XML, CSV, Markdown, and YAML (optional).

   singleton
      A design pattern that ensures only one instance of a class exists. FailExtract uses a singleton pattern for the :class:`FailureExtractor` class to maintain centralized failure collection.

   thread-safe
      Code that can be safely executed by multiple threads concurrently without data corruption. FailExtract's core classes are thread-safe to support parallel test execution.

   context extractor
      A component that analyzes code and extracts relevant context information around test failures, including source code, dependencies, and variable states.

   optional dependency
      A package dependency that is not required for core functionality but enables additional features. FailExtract uses optional dependencies for features like YAML formatting.

   progressive enhancement
      A development approach where basic functionality works without optional features, and additional capabilities are added when optional dependencies are available.

   graceful degradation
      The ability of software to continue functioning when some features or dependencies are unavailable, providing helpful error messages and fallback behavior.