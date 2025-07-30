Getting Started with FailExtract
=================================

**Purpose**: Learn to capture and analyze test failures in 5 minutes

This tutorial will guide you through your first successful failure extraction. By the end, you'll have captured test failures and generated readable reports.

What You'll Learn
-----------------

- How to add failure extraction to existing tests
- How to generate JSON and Markdown reports
- How to read failure context data
- How to set up a basic debugging workflow

Prerequisites
-------------

- Python 3.11 or later
- Basic understanding of Python functions and assertions
- 5 minutes of time

Installation
------------

Install FailExtract with a single command:

.. code-block:: bash

   pip install failextract

That's it! FailExtract has zero required dependencies for core functionality.

Your First Failure Extraction
------------------------------

Let's start with a simple test that fails:

.. code-block:: python

   from failextract import extract_on_failure

   @extract_on_failure
   def test_basic_assertion():
       """A simple test that will fail and be captured."""
       x = 10
       y = 20
       assert x > y, f"Expected {x} to be greater than {y}"

The ``@extract_on_failure`` decorator automatically captures failure context when the function raises an exception.

Running and Capturing Failures
-------------------------------

Create a complete example that demonstrates the full workflow:

.. code-block:: python

   #!/usr/bin/env python3
   """Your first FailExtract example"""
   
   from failextract import extract_on_failure, FailureExtractor, OutputConfig

   @extract_on_failure
   def test_basic_assertion():
       """A simple test that will fail and be captured."""
       x = 10
       y = 20
       assert x > y, f"Expected {x} to be greater than {y}"

   @extract_on_failure
   def test_with_context():
       """Test with setup data that will be captured."""
       user_data = {
           'name': 'John Doe',
           'email': 'john@example.com',
           'age': 25
       }
       
       # This failure will capture the user_data context
       assert user_data['age'] > 30, "User must be over 30"

   if __name__ == "__main__":
       print("Running failure extraction example...")
       
       # Run the tests (they will fail and be captured)
       try:
           test_basic_assertion()
       except AssertionError:
           pass  # Expected failure
       
       try:
           test_with_context()
       except AssertionError:
           pass  # Expected failure
       
       # Generate reports
       extractor = FailureExtractor()
       print(f"Captured {len(extractor.failures)} failures")
       
       # Generate JSON report (machine-readable)
       json_config = OutputConfig("my_failures.json", format="json")
       extractor.save_report(json_config)
       print("Generated my_failures.json")
       
       # Generate Markdown report (human-readable)
       md_config = OutputConfig("my_failures.md", format="markdown")
       extractor.save_report(md_config)
       print("Generated my_failures.md")

Save this as ``first_example.py`` and run it:

.. code-block:: bash

   python first_example.py

You should see output like:

.. code-block:: text

   Running failure extraction example...
   Captured 2 failures
   Generated my_failures.json
   Generated my_failures.md

Understanding the Generated Reports
-----------------------------------

FailExtract generates two types of reports:

**JSON Report (my_failures.json)**

Machine-readable format perfect for automation:

.. code-block:: json

   [
     {
       "test_name": "test_basic_assertion",
       "exception_type": "AssertionError",
       "exception_message": "Expected 10 to be greater than 20",
       "timestamp": "2025-06-06T09:15:42.123456",
       "local_variables": {
         "x": 10,
         "y": 20
       }
     }
   ]

**Markdown Report (my_failures.md)**

Human-readable format perfect for documentation:

.. code-block:: markdown

   # Test Failures Report
   
   Generated on: 2025-06-06 09:15:42
   
   ## test_basic_assertion
   
   **Exception:** AssertionError  
   **Message:** Expected 10 to be greater than 20
   
   **Local Variables:**
   - x: 10
   - y: 20

What Just Happened?
-------------------

1. **Decoration**: ``@extract_on_failure`` monitored your functions
2. **Capture**: When assertions failed, context was automatically captured
3. **Storage**: Failure data was stored in memory by ``FailureExtractor``
4. **Reporting**: Data was formatted and saved as JSON and Markdown files

Key Concepts
------------

**Failure Context**
   Local variables, function arguments, and exception details captured automatically

**Zero Overhead**
   When tests pass, there's no performance impact (<5% even when capturing failures)

**Multiple Formats**
   Generate reports in formats that match your workflow (JSON for automation, Markdown for documentation)

**Progressive Enhancement**
   Start simple, add more sophisticated features as needed

Next Steps
----------

Now that you've captured your first failures, you can:

- **Explore Multiple Formats**: :doc:`multiple_formats` - Learn about XML, CSV, and YAML output
- **Configure FailExtract**: :doc:`configuration` - Customize output and behavior  
- **Integrate with pytest**: :doc:`pytest_integration` - Add to your existing test suite
- **Create Custom Formatters**: :doc:`custom_formatters` - Build domain-specific outputs

**Immediate Action**: Try the tutorial with your own test functions. Add the decorator to any function that might fail and see what context gets captured!

Troubleshooting
---------------

**No failures captured?**
   Make sure your functions are decorated with ``@extract_on_failure`` and actually raise exceptions.

**Import errors?**
   Verify FailExtract is installed: ``pip list | grep failextract``

**Report not generated?**
   Check that you have write permissions in the current directory.

Success Checklist
------------------

| ✅ Installed FailExtract  
| ✅ Added ``@extract_on_failure`` decorator to a function  
| ✅ Function failed and was captured  
| ✅ Generated JSON and Markdown reports  
| ✅ Understood the failure context data  

**You're ready for the next tutorial!** Your failure extraction workflow is now established.