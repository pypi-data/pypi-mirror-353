Changelog
=========

All notable changes to FailExtract will be documented in this file.

The format is based on `Keep a Changelog <https://keepachangelog.com/en/1.0.0/>`_,
and this project adheres to `Semantic Versioning <https://semver.org/spec/v2.0.0.html>`_.

[Unreleased]
------------

Added
~~~~~
- Initial release preparation
- Comprehensive documentation infrastructure
- Performance and threading documentation
- Extension points documentation

[0.1.0] - 2025-06-04
--------------------

Added
~~~~~
- Core FailureExtractor with singleton pattern and thread safety
- FixtureExtractor for automatic pytest fixture detection
- Multiple output formatters: JSON, Markdown, XML, CSV (built-in) + YAML (optional)
- ``@extract_on_failure`` decorator for simple test instrumentation
- Comprehensive test suite with 300+ tests
- Memory management with configurable limits
- Performance optimizations and caching
- Thread-safe operations for concurrent test execution
- Extensive examples and usage patterns
- Complete API documentation with Google-style docstrings

Changed
~~~~~~~
- Initial implementation

Deprecated
~~~~~~~~~~
- None

Removed
~~~~~~~
- None

Fixed
~~~~~
- All test infrastructure issues resolved
- Thread safety implementation completed
- Memory management edge cases handled

Security
~~~~~~~~
- Thread-safe singleton implementation
- Input validation for all public APIs
- Safe file handling with proper error recovery