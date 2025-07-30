How to Generate Reports
=======================

**Task**: Create failure reports in different formats for various use cases

This guide shows you how to generate reports from captured failure data using FailExtract's programmatic API and command-line interface.

Basic Report Generation
-----------------------

**Using the Programmatic API**

.. code-block:: python

   from failextract import FailureExtractor, OutputConfig

   # Get the extractor instance (contains all captured failures)
   extractor = FailureExtractor()

   # Generate JSON report (always available)
   json_config = OutputConfig("failures.json")
   extractor.save_report(json_config)

   # Generate Markdown report (core feature) 
   md_config = OutputConfig("failures.md", format="markdown")
   extractor.save_report(md_config)

   print(f"Generated reports for {len(extractor.failures)} failures")

**Using the Command Line**

.. code-block:: bash

   # Generate JSON report
   failextract report --format json --output failures.json

   # Generate Markdown report
   failextract report --format markdown --output failures.md

Report Formats and Use Cases
-----------------------------

**JSON Format - Machine Processing**

Best for: Automation, APIs, further data processing

.. code-block:: python

   # Generate JSON with specific configuration
   config = OutputConfig("api_failures.json", format="json")
   extractor.save_report(config)

.. code-block:: bash

   # CLI equivalent
   failextract report --format json --output api_failures.json

**Markdown Format - Documentation**

Best for: GitHub issues, documentation, human review

.. code-block:: python

   # Generate Markdown report
   config = OutputConfig("failures.md", format="markdown")
   extractor.save_report(config)

.. code-block:: bash

   # CLI equivalent  
   failextract report --format markdown --output failures.md

**XML Format - Tool Integration**

Best for: CI/CD tools, enterprise systems expecting XML

.. code-block:: python

   # Generate XML report
   config = OutputConfig("failures.xml", format="xml")
   extractor.save_report(config)

.. code-block:: bash

   # CLI equivalent
   failextract report --format xml --output failures.xml

**CSV Format - Data Analysis**

Best for: Spreadsheet analysis, data science workflows

.. code-block:: python

   # Generate CSV for analysis
   config = OutputConfig("failures.csv", format="csv")
   extractor.save_report(config)

.. code-block:: bash

   # CLI equivalent
   failextract report --format csv --output failures.csv

**YAML Format - Configuration Style** (Optional)

Best for: Configuration files, infrastructure-as-code

.. code-block:: python

   # Generate YAML (requires: pip install failextract[formatters])
   try:
       config = OutputConfig("failures.yaml", format="yaml")
       extractor.save_report(config)
       print("✓ Generated YAML report")
   except ImportError:
       print("✗ YAML formatter not available - install with: pip install failextract[formatters]")

.. code-block:: bash

   # CLI equivalent (if YAML formatter is installed)
   failextract report --format yaml --output failures.yaml

Customizing Report Content
---------------------------

**Limiting Report Size**

.. code-block:: python

   # Limit to most recent 50 failures
   config = OutputConfig("recent_failures.json", max_failures=50)
   extractor.save_report(config)

.. code-block:: bash

   # CLI equivalent
   failextract report --format json --max-failures 50 --output recent_failures.json

**Including Passed Tests** (if tracked)

.. code-block:: python

   # Include both failures and passed tests in report
   config = OutputConfig("complete_report.json")
   # Note: Passed test inclusion is controlled at the extraction level
   extractor.save_report(config)

.. code-block:: bash

   # CLI equivalent
   failextract report --format json --include-passed --output complete_report.json

**Append vs. Overwrite**

.. code-block:: python

   # Append to existing file
   config = OutputConfig("ongoing_failures.json", append=True)
   extractor.save_report(config)

   # Overwrite existing file (default behavior)
   config = OutputConfig("latest_failures.json", append=False)
   extractor.save_report(config)

Multi-Format Report Generation
-------------------------------

**Generate All Available Formats**

.. code-block:: python

   def generate_comprehensive_reports():
       """Generate reports in all available formats."""
       extractor = FailureExtractor()
       
       if not extractor.failures:
           print("No failures to report")
           return
       
       # Core formats (always available)
       core_formats = ["json", "markdown", "xml", "csv"]
       
       # Optional formats
       optional_formats = ["yaml"]
       
       generated_files = []
       
       # Generate core format reports
       for fmt in core_formats:
           try:
               config = OutputConfig(f"failures.{fmt}", format=fmt)
               extractor.save_report(config)
               generated_files.append(f"failures.{fmt}")
               print(f"✓ Generated {fmt} report")
           except Exception as e:
               print(f"✗ Failed to generate {fmt}: {e}")
       
       # Try optional formats
       for fmt in optional_formats:
           try:
               config = OutputConfig(f"failures.{fmt}", format=fmt)
               extractor.save_report(config)
               generated_files.append(f"failures.{fmt}")
               print(f"✓ Generated {fmt} report")
           except ImportError:
               print(f"⚠ Skipped {fmt} (install with: pip install failextract[formatters])")
           except Exception as e:
               print(f"✗ Failed to generate {fmt}: {e}")
       
       return generated_files

   # Use the function
   files = generate_comprehensive_reports()
   print(f"Generated {len(files)} report files")

**Batch Report Generation Script**

.. code-block:: bash

   #!/bin/bash
   # generate_all_reports.sh - Generate reports in all formats

   set -e

   echo "Generating comprehensive failure reports..."

   # Core formats
   failextract report --format json --output failures.json
   failextract report --format markdown --output failures.md  
   failextract report --format xml --output failures.xml
   failextract report --format csv --output failures.csv

   # Optional format (if available)
   if failextract report --format yaml --output failures.yaml 2>/dev/null; then
       echo "✓ Generated YAML report"
   else
       echo "⚠ YAML format not available"
   fi

   echo "Report generation complete!"
   ls -la failures.*

Automated Report Generation
----------------------------

**GitHub Actions Integration**

.. code-block:: yaml

   # .github/workflows/test-reports.yml
   name: Generate Test Reports
   
   on: [push, pull_request]
   
   jobs:
     test-and-report:
       runs-on: ubuntu-latest
       steps:
         - uses: actions/checkout@v3
         - uses: actions/setup-python@v4
           with:
             python-version: 3.9
             
         - name: Install dependencies
           run: |
             pip install failextract[formatters]
             pip install -r requirements.txt
             
         - name: Run tests
           run: pytest --tb=short || true
           
         - name: Generate failure reports
           if: always()
           run: |
             failextract report --format json --output test-failures.json
             failextract report --format markdown --output test-failures.md
             
         - name: Upload reports as artifacts
           if: always()
           uses: actions/upload-artifact@v4
           with:
             name: test-failure-reports
             path: |
               test-failures.json
               test-failures.md

**Daily Report Automation**

.. code-block:: python

   #!/usr/bin/env python3
   """Daily failure report automation"""

   import os
   import subprocess
   from datetime import datetime
   from pathlib import Path

   def generate_daily_report():
       """Generate daily failure summary."""
       
       # Create dated directory
       date_str = datetime.now().strftime("%Y-%m-%d")
       report_dir = Path(f"reports/{date_str}")
       report_dir.mkdir(parents=True, exist_ok=True)
       
       # Generate reports
       formats = ["json", "markdown", "csv"]
       
       for fmt in formats:
           output_file = report_dir / f"daily_failures.{fmt}"
           
           try:
               subprocess.run([
                   "failextract", "report",
                   "--format", fmt,
                   "--output", str(output_file)
               ], check=True)
               print(f"✓ Generated {output_file}")
           except subprocess.CalledProcessError as e:
               print(f"✗ Failed to generate {fmt} report: {e}")
       
       # Check if any failures were found
       json_file = report_dir / "daily_failures.json"
       if json_file.exists() and json_file.stat().st_size > 20:  # More than empty array
           print(f"⚠ Failures detected - check reports in {report_dir}")
           return True
       else:
           print("✅ No failures detected")
           return False

   if __name__ == "__main__":
       has_failures = generate_daily_report()
       exit(1 if has_failures else 0)

Report Content and Structure
----------------------------

**Understanding JSON Report Structure**

.. code-block:: json

   [
     {
       "test_name": "test_user_authentication",
       "test_module": "__main__",
       "test_file": "/path/to/test.py",
       "exception_type": "AssertionError",
       "exception_message": "Authentication failed for user: test_user",
       "timestamp": "2025-06-06T10:30:45.123456",
       "local_variables": {
         "username": "test_user",
         "password": "wrong_password",
         "authenticated": false
       }
     }
   ]

**Markdown Report Format**

.. code-block:: markdown

   # Test Failures Report
   
   Generated on: 2025-06-06 10:30:45
   
   ## test_user_authentication
   
   **Exception:** AssertionError  
   **Message:** Authentication failed for user: test_user  
   **File:** /path/to/test.py  
   **Module:** __main__
   
   **Local Variables:**
   - username: test_user
   - password: wrong_password  
   - authenticated: False

**CSV Report Format**

.. code-block:: text

   Test Name,Module,File,Timestamp,Exception Type,Exception Message,Line Number
   test_user_authentication,__main__,/path/to/test.py,2025-06-06T10:30:45.123456,AssertionError,"Authentication failed for user: test_user",

Report Management and Cleanup
------------------------------

**Checking Report Status**

.. code-block:: python

   # Check if there are failures to report
   extractor = FailureExtractor()
   
   if extractor.failures:
       print(f"Found {len(extractor.failures)} failures to report")
       # Generate reports
   else:
       print("No failures to report")

.. code-block:: bash

   # CLI equivalent
   failextract stats

**Clearing Data After Reporting**

.. code-block:: python

   # Generate report and clear data
   extractor = FailureExtractor()
   
   if extractor.failures:
       # Generate report
       config = OutputConfig("final_report.json")
       extractor.save_report(config)
       
       # Clear data for next test run
       extractor.clear()
       print("Report generated and data cleared")

.. code-block:: bash

   # CLI equivalent
   failextract report --format json --output final_report.json
   failextract clear --confirm

Error Handling for Report Generation
-------------------------------------

**Robust Report Generation**

.. code-block:: python

   def safe_report_generation():
       """Generate reports with proper error handling."""
       extractor = FailureExtractor()
       
       if not extractor.failures:
           print("No failures to report")
           return []
       
       generated_files = []
       
       # Try each format with individual error handling
       formats_to_try = [
           ("json", "failures.json"),
           ("markdown", "failures.md"),
           ("xml", "failures.xml"),
           ("csv", "failures.csv")
       ]
       
       for format_name, filename in formats_to_try:
           try:
               config = OutputConfig(filename, format=format_name)
               extractor.save_report(config)
               generated_files.append(filename)
               print(f"✓ Generated {filename}")
           except Exception as e:
               print(f"✗ Failed to generate {filename}: {e}")
       
       # Try optional YAML format
       try:
           config = OutputConfig("failures.yaml", format="yaml")
           extractor.save_report(config)
           generated_files.append("failures.yaml")
           print("✓ Generated failures.yaml")
       except ImportError:
           print("⚠ YAML format requires: pip install failextract[formatters]")
       except Exception as e:
           print(f"✗ Failed to generate YAML: {e}")
       
       return generated_files

   # Use the safe function
   files = safe_report_generation()
   print(f"Successfully generated {len(files)} report files")

Integration with External Tools
--------------------------------

**Email Reports**

.. code-block:: python

   import smtplib
   from email.mime.text import MIMEText
   from email.mime.multipart import MIMEMultipart

   def email_failure_report():
       """Email failure report if failures exist."""
       extractor = FailureExtractor()
       
       if not extractor.failures:
           return
       
       # Generate Markdown report for email
       config = OutputConfig("email_report.md", format="markdown")
       extractor.save_report(config)
       
       # Read report content
       with open("email_report.md", "r") as f:
           report_content = f.read()
       
       # Send email (configure SMTP settings as needed)
       msg = MIMEText(report_content)
       msg["Subject"] = f"Test Failures - {len(extractor.failures)} failures"
       msg["From"] = "test-system@company.com"
       msg["To"] = "team@company.com"
       
       # Send via SMTP (configuration required)
       # smtp_server.send_message(msg)
       
       print("Failure report sent via email")

**Webhook Integration**

.. code-block:: python

   import requests
   import json

   def post_to_webhook():
       """Post failure data to webhook endpoint."""
       extractor = FailureExtractor()
       
       if extractor.failures:
           # Prepare webhook payload
           payload = {
               "failures": len(extractor.failures),
               "timestamp": extractor.failures[0]["timestamp"],
               "details": extractor.failures[:5]  # Limit for webhook
           }
           
           # Post to webhook
           try:
               response = requests.post(
                   "https://your-webhook-url.com/failures",
                   json=payload,
                   timeout=30
               )
               response.raise_for_status()
               print(f"Posted {len(extractor.failures)} failures to webhook")
           except requests.RequestException as e:
               print(f"Failed to post to webhook: {e}")

Next Steps
----------

After mastering report generation:

1. **Automate Integration**: Set up automatic report generation in CI/CD
2. **Customize Formats**: :doc:`../tutorials/custom_formatters` - Create specialized output formats
3. **Monitor Production**: Set up regular automated reporting for production systems
4. **Share with Team**: Integrate reports with your team's communication tools

Key Report Generation Takeaways
--------------------------------

| ✅ **Multiple formats available** - JSON, Markdown, XML, CSV (+ YAML with optional install)  
| ✅ **Programmatic and CLI access** - Use Python API or command-line tools  
| ✅ **Flexible configuration** - Control content, limits, and output paths  
| ✅ **Error handling** - Graceful degradation when formats aren't available  
| ✅ **Integration ready** - Easy automation with CI/CD and external tools  
| ✅ **Production scalable** - Memory management and cleanup capabilities  

**You can now generate reports for any workflow or tool integration!**