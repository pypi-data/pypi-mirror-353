How-To Guides
=============

**Practical solutions for specific tasks and problems**

These guides provide focused, step-by-step instructions for accomplishing specific tasks with FailExtract. Each guide assumes you have basic familiarity with FailExtract and focuses on solving a particular problem.

.. toctree::
   :maxdepth: 2

   install_failextract
   generate_reports
   optimize_performance
   troubleshoot_issues
   setup_ci_cd
   setup_pypi_release

Quick Reference
---------------

**Installation and Setup**
- :doc:`install_failextract` - Get FailExtract installed and working

**Report Generation**
- :doc:`generate_reports` - Create reports in different formats for various use cases

**Performance and Optimization**
- :doc:`optimize_performance` - Configure for development, CI/CD, and production environments

**Problem Solving**
- :doc:`troubleshoot_issues` - Diagnose and fix common issues

**Development and CI/CD**
- :doc:`setup_ci_cd` - Configure automated documentation builds and deployment
- :doc:`setup_pypi_release` - Configure automated PyPI package releases

Task-Oriented Solutions
-----------------------

These guides solve specific problems you might encounter:

Installation Tasks
~~~~~~~~~~~~~~~~~~

- Installing FailExtract with different feature sets
- Setting up in virtual environments, Docker, and CI/CD
- Verifying installation and troubleshooting import issues
- Upgrading between versions

Report Generation Tasks
~~~~~~~~~~~~~~~~~~~~~~~

- Generating reports in multiple formats
- Automating report generation in CI/CD pipelines
- Integrating reports with external tools and services
- Handling large datasets and memory management

Performance Tasks
~~~~~~~~~~~~~~~~~

- Configuring for minimal overhead in production
- Optimizing for CI/CD environments
- Managing memory usage in long-running test suites
- Measuring and monitoring performance impact

Troubleshooting Tasks
~~~~~~~~~~~~~~~~~~~~~

- Diagnosing import and installation problems
- Fixing capture and extraction issues
- Resolving report generation failures
- Handling environment-specific problems

Development and CI/CD Tasks
~~~~~~~~~~~~~~~~~~~~~~~~~~~

- Setting up automated documentation builds
- Configuring GitHub Pages deployment  
- Creating release-triggered workflows
- Setting up automated PyPI package releases
- Managing PyPI tokens and security
- Monitoring and maintaining CI/CD pipelines

How to Use These Guides
-----------------------

**Problem-First Approach**
Each guide starts with a specific problem or task you want to accomplish.

**Step-by-Step Solutions**
Clear, actionable instructions that you can follow immediately.

**Error Handling**
Robust solutions that handle edge cases and provide fallback options.

**Real-World Context**
Examples and scenarios from actual usage patterns.

When to Use How-To Guides vs. Tutorials
----------------------------------------

**Use How-To Guides when:**
- You have a specific problem to solve
- You're already familiar with FailExtract basics
- You need a quick solution to accomplish a task
- You're troubleshooting an issue

**Use Tutorials when:**
- You're learning FailExtract for the first time
- You want to understand concepts step-by-step
- You're exploring FailExtract's capabilities
- You want guided, hands-on learning

Quick Solutions
---------------

**Most Common Tasks:**

.. code-block:: bash

   # Quick installation
   pip install failextract
   
   # Generate JSON report
   failextract report --format json --output failures.json
   
   # Install with all features
   pip install failextract[formatters,cli]

.. code-block:: python

   # Basic usage pattern
   from failextract import extract_on_failure, FailureExtractor, OutputConfig
   
   @extract_on_failure
   def test_example():
       assert False, "Test failure"
   
   # Generate report
   extractor = FailureExtractor()
   config = OutputConfig("failures.json")
   extractor.save_report(config)

Get Started
-----------

Choose the guide that matches your current need:

- **New to FailExtract?** Start with :doc:`install_failextract`
- **Need reports?** Go to :doc:`generate_reports`
- **Performance issues?** Check :doc:`optimize_performance`
- **Something not working?** Try :doc:`troubleshoot_issues`
- **Setting up CI/CD?** See :doc:`setup_ci_cd`
- **Need PyPI releases?** Go to :doc:`setup_pypi_release`

**Next**: Choose the guide that solves your specific problem