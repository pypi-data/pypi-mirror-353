FailExtract Documentation
==========================

.. image:: https://img.shields.io/badge/python-3.11%2B-blue.svg
   :target: https://www.python.org/downloads/
   :alt: Python Version

.. image:: https://img.shields.io/badge/License-Apache%202.0-blue.svg
   :target: https://opensource.org/licenses/Apache-2.0
   :alt: License: Apache 2.0

FailExtract is a lightweight Python library for extracting and analyzing pytest test failures. It provides automatic failure context capture with minimal overhead and supports multiple output formats for different workflows.

**Core Philosophy**: Progressive enhancement with honest documentation. Start simple, grow sophisticated as needed.

Key Features
------------

* **Zero Dependencies**: Core functionality uses only Python standard library
* **Automatic Context Capture**: Local variables, stack traces, and pytest fixtures
* **Multiple Output Formats**: JSON, Markdown, XML, CSV (built-in) + YAML (optional)
* **Performance Awareness**: <5% overhead in production, configurable for different environments
* **pytest Integration**: Seamless integration with existing test suites
* **Memory Management**: Built-in limits and monitoring for long-running test suites

Quick Start
-----------

**Installation** (30 seconds)::

    pip install failextract

**First Use** (2 minutes):

.. code-block:: python

    from failextract import extract_on_failure, FailureExtractor, OutputConfig

    @extract_on_failure
    def test_example():
        user_data = {"name": "John", "age": 25}
        assert user_data["name"] == "Jane", "Name mismatch"

    # Run test (it will fail and be captured)
    try:
        test_example()
    except AssertionError:
        pass

    # Generate report
    extractor = FailureExtractor()
    config = OutputConfig("failures.json")
    extractor.save_report(config)

**What just happened?** FailExtract captured the failure context (local variables, exception details) and saved it as a JSON report. The ``user_data`` dictionary is now available for debugging.

Documentation Structure
-----------------------

This documentation follows the `Diátaxis framework <https://diataxis.fr/>`_ for optimal learning and reference:

.. toctree::
   :maxdepth: 2
   :caption: 📚 Tutorials

   tutorials/index

.. toctree::
   :maxdepth: 2
   :caption: 🛠️ How-To Guides

   how-to/index

.. toctree::
   :maxdepth: 2
   :caption: 💭 Discussions

   discussions/index

.. toctree::
   :maxdepth: 2
   :caption: 📖 Reference

   reference/index

Getting Started
---------------

**New to FailExtract?**

1. **Install**: :doc:`how-to/install_failextract` (2 minutes)
2. **Learn**: :doc:`tutorials/getting_started` (5 minutes)  
3. **Explore**: :doc:`tutorials/multiple_formats` (10 minutes)

**Have a specific problem?**

- **Installation issues**: :doc:`how-to/troubleshoot_issues`
- **Need reports**: :doc:`how-to/generate_reports`
- **Performance concerns**: :doc:`how-to/optimize_performance`

**Want to understand the design?**

- **Why FailExtract exists**: :doc:`discussions/architectural_philosophy`
- **How it evolved**: :doc:`discussions/development_journey`
- **Design principles**: :doc:`discussions/progressive_enhancement`

**Need technical details?**

- **Complete API**: :doc:`reference/api`
- **All configuration options**: :doc:`reference/index`

Why FailExtract?
================

**The Problem**: Test failures often lack sufficient context for efficient debugging. Stack traces show what failed, but not the state that led to the failure.

**The Solution**: FailExtract automatically captures comprehensive failure context - local variables, fixture values, and execution environment - with minimal performance impact.

**The Result**: Faster debugging, better failure analysis, and improved test reliability through actionable failure reports.

**Design Philosophy**: 

- **Progressive Enhancement** - Start simple, add complexity only when needed
- **Honest Documentation** - Document what actually works, not what we wish worked  
- **Performance Awareness** - Explicit trade-offs between detail and speed
- **Zero Dependencies** - Core functionality works everywhere Python runs

Production Ready
=================

FailExtract is designed for real-world usage:

| ✅ **Production-tested** with 96% test coverage and comprehensive test suite  
| ✅ **Performance-optimized** with <5% overhead in production mode  
| ✅ **Memory-managed** with configurable limits for long-running test suites  
| ✅ **Thread-safe** singleton architecture for concurrent test execution  
| ✅ **CI/CD ready** with command-line interface and automation support  

Community and Support
=====================

**Get Help**

- **Documentation**: You're reading it! Start with :doc:`tutorials/getting_started`
- **Troubleshooting**: :doc:`how-to/troubleshoot_issues` for common problems
- **GitHub Issues**: Report bugs and request features
- **Examples**: Working examples in the ``examples/`` directory

**Project Links**

- **PyPI Package**: https://pypi.org/project/failextract/
- **GitHub Repository**: https://github.com/your-org/failextract
- **Issue Tracker**: https://github.com/your-org/failextract/issues

**Contributing**

Contributions welcome! See :doc:`discussions/development_journey` for the development philosophy and approach.

.. toctree::
   :maxdepth: 1
   :caption: Meta

   changelog
   glossary

Indices and Tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`