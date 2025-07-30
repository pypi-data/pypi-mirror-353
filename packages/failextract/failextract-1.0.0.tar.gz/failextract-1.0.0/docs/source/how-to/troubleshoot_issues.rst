How to Troubleshoot Issues
==========================

**Task**: Diagnose and fix common FailExtract problems quickly

This guide provides systematic troubleshooting steps for common issues, error messages, and unexpected behavior when using FailExtract.

Installation and Import Issues
-------------------------------

**Problem: "No module named 'failextract'"**

.. code-block:: text

   ImportError: No module named 'failextract'

**Diagnosis Steps:**

.. code-block:: bash

   # Check if FailExtract is installed
   pip list | grep failextract
   
   # Check which Python interpreter you're using
   which python
   python --version
   
   # Try importing in Python directly
   python -c "import failextract; print('FailExtract available')"

**Solutions:**

.. code-block:: bash

   # Install FailExtract
   pip install failextract
   
   # If using virtual environment, ensure it's activated
   source venv/bin/activate  # Linux/Mac
   # venv\Scripts\activate   # Windows
   
   # Install in user directory if permission issues
   pip install --user failextract
   
   # Force reinstall if corrupted
   pip uninstall failextract
   pip install failextract

**Problem: "ImportError: No module named 'yaml'"**

.. code-block:: text

   ImportError: No module named 'yaml'

**Cause:** YAML formatter requested but optional dependency not installed.

**Solution:**

.. code-block:: bash

   # Install YAML support
   pip install failextract[formatters]
   
   # Or install PyYAML directly
   pip install pyyaml

**Alternative:** Use other formats if YAML isn't essential:

.. code-block:: python

   from failextract import OutputConfig, FailureExtractor

   # Use JSON instead of YAML
   config = OutputConfig("failures.json", format="json")
   # Instead of: config = OutputConfig("failures.yaml", format="yaml")

Decorator and Capture Issues
-----------------------------

**Problem: "No failures captured" despite test failures**

**Diagnosis Steps:**

.. code-block:: python

   # Check if decorator is properly applied
   from failextract import extract_on_failure, FailureExtractor

   @extract_on_failure
   def test_debug():
       assert False, "This should be captured"

   # Run test and check
   try:
       test_debug()
   except AssertionError:
       pass

   extractor = FailureExtractor()
   print(f"Captured failures: {len(extractor.failures)}")
   
   # If zero, decorator isn't working properly

**Common Causes and Solutions:**

1. **Decorator not applied:**

   .. code-block:: python

      # Wrong - decorator missing
      def test_example():
          assert False, "Not captured"
      
      # Correct - decorator applied
      @extract_on_failure
      def test_example():
          assert False, "Will be captured"

2. **Test doesn't actually fail:**

   .. code-block:: python

      # Debug the test logic
      @extract_on_failure
      def test_debug():
          result = some_function()
          print(f"Debug: result = {result}")  # Add debug output
          assert result == expected_value, f"Expected {expected_value}, got {result}"

3. **Exception handled before extraction:**

   .. code-block:: python

      # Problematic - exception caught
      @extract_on_failure
      def test_with_handler():
          try:
              assert False, "This won't be captured"
          except AssertionError:
              pass  # Exception handled, not extracted
      
      # Better - let extraction happen first
      @extract_on_failure
      def test_proper():
          assert False, "This will be captured"

**Problem: Extraction happens but no local variables captured**

**Diagnosis:**

.. code-block:: python

   # Check decorator configuration
   @extract_on_failure(include_locals=True)  # Explicitly enable locals
   def test_with_locals():
       important_data = {"key": "value"}
       assert False, "Check if important_data is captured"

**Solution:** Ensure ``include_locals=True`` (it's the default, but verify):

.. code-block:: python

   @extract_on_failure(
       include_locals=True,    # Capture local variables
       max_depth=10           # Ensure sufficient depth
   )
   def test_with_variables():
       user_data = {"id": 123, "name": "Alice"}
       config = {"timeout": 30}
       assert False, "Both variables should be captured"

Report Generation Issues
------------------------

**Problem: "Permission denied" when saving reports**

.. code-block:: text

   PermissionError: [Errno 13] Permission denied: 'failures.json'

**Solutions:**

.. code-block:: python

   import os
   from pathlib import Path
   from failextract import OutputConfig, FailureExtractor

   # Check current directory permissions
   print(f"Current directory: {os.getcwd()}")
   print(f"Can write: {os.access('.', os.W_OK)}")

   # Use alternative directory
   reports_dir = Path("reports")
   reports_dir.mkdir(exist_ok=True)
   
   config = OutputConfig(str(reports_dir / "failures.json"))
   
   # Or use temporary directory
   import tempfile
   with tempfile.TemporaryDirectory() as temp_dir:
       config = OutputConfig(f"{temp_dir}/failures.json")

**Problem: "No data available for operation"**

**Cause:** Trying to generate report when no failures exist.

**Solution:**

.. code-block:: python

   extractor = FailureExtractor()
   
   # Check before generating report
   if extractor.failures:
       config = OutputConfig("failures.json")
       extractor.save_report(config)
       print(f"Generated report with {len(extractor.failures)} failures")
   else:
       print("No failures to report")

**Problem: Reports are empty or have unexpected content**

**Diagnosis:**

.. code-block:: python

   # Debug the extraction process
   extractor = FailureExtractor()
   
   print(f"Total failures: {len(extractor.failures)}")
   print(f"Total passed: {len(extractor.passed)}")
   
   # Examine failure structure
   if extractor.failures:
       print("Sample failure:")
       import json
       print(json.dumps(extractor.failures[0], indent=2, default=str))

**Problem: Format-specific errors**

.. code-block:: python

   # Test each format individually
   def test_formats():
       extractor = FailureExtractor()
       
       if not extractor.failures:
           print("No failures to test with")
           return
       
       formats = ["json", "markdown", "xml", "csv"]
       
       for fmt in formats:
           try:
               config = OutputConfig(f"test.{fmt}", format=fmt)
               extractor.save_report(config)
               print(f"✓ {fmt} format works")
           except Exception as e:
               print(f"✗ {fmt} format error: {e}")

Memory and Performance Issues
-----------------------------

**Problem: Excessive memory usage**

**Diagnosis:**

.. code-block:: python

   from failextract import FailureExtractor

   # Check memory usage
   extractor = FailureExtractor()
   stats = extractor.get_stats()
   limits = extractor.get_memory_limits()
   
   print(f"Memory usage:")
   print(f"  Failures: {stats['failures_count']}/{limits['max_failures']}")
   print(f"  Passed: {stats['passed_count']}/{limits['max_passed']}")
   print(f"  At limits: {stats['failures_at_limit']}, {stats['passed_at_limit']}")

**Solutions:**

.. code-block:: python

   # Set conservative memory limits
   extractor.set_memory_limits(
       max_failures=100,    # Reduce from default
       max_passed=50        # Reduce from default
   )
   
   # Clear data regularly
   def run_test_batch():
       # Run tests...
       
       # Generate report and clear
       if extractor.failures:
           config = OutputConfig("batch_failures.json")
           extractor.save_report(config)
           extractor.clear()

**Problem: Tests running slowly**

**Diagnosis:**

.. code-block:: python

   import time
   from failextract import extract_on_failure

   # Measure overhead
   def measure_decorator_overhead():
       # Test without decorator
       def baseline_test():
           assert False, "Baseline"
       
       # Test with decorator
       @extract_on_failure
       def decorated_test():
           assert False, "Decorated"
       
       # Time both
       iterations = 100
       
       # Baseline
       start = time.time()
       for _ in range(iterations):
           try:
               baseline_test()
           except:
               pass
       baseline_time = time.time() - start
       
       # Decorated
       start = time.time()
       for _ in range(iterations):
           try:
               decorated_test()
           except:
               pass
       decorated_time = time.time() - start
       
       overhead = (decorated_time / baseline_time - 1) * 100
       print(f"Overhead: {overhead:.1f}%")

**Solutions:**

.. code-block:: python

   # Use performance-optimized configuration
   @extract_on_failure(
       include_locals=False,    # Skip variables for speed
       max_depth=3,            # Minimal depth
       skip_stdlib=True        # Skip standard library frames
   )
   def optimized_test():
       assert False, "Fast extraction"

Configuration and Environment Issues
------------------------------------

**Problem: Configuration not working as expected**

**Diagnosis:**

.. code-block:: python

   from failextract import OutputConfig

   # Test configuration parsing
   def debug_config():
       # Test different configurations
       configs = [
           OutputConfig("test.json"),
           OutputConfig("test.yaml", format="yaml"),
           OutputConfig("test.md", format="markdown"),
       ]
       
       for config in configs:
           print(f"File: {config.filename}")
           print(f"Format: {config.format}")
           print(f"Append: {config.append}")
           print("---")

**Problem: Environment-specific behavior**

.. code-block:: python

   import os

   # Debug environment detection
   def debug_environment():
       print("Environment variables:")
       relevant_vars = ["CI", "PYTEST_CURRENT_TEST", "PYTHONPATH"]
       
       for var in relevant_vars:
           value = os.getenv(var)
           print(f"  {var}: {value}")
       
       print(f"Current working directory: {os.getcwd()}")
       print(f"Python path: {os.sys.path[:3]}...")  # First 3 entries

Integration Issues
------------------

**Problem: pytest integration not working**

**Diagnosis:**

.. code-block:: python

   # Check if conftest.py is being loaded
   # Add this to your conftest.py for debugging
   print("conftest.py loaded")

   # Check if hooks are being called
   def pytest_runtest_makereport(item, call):
       print(f"Hook called for: {item.name}, phase: {call.when}")

**Problem: CI/CD integration failures**

**Common Issues and Solutions:**

1. **Path issues in CI:**

   .. code-block:: bash

      # Debug paths in CI
      echo "Current directory: $(pwd)"
      echo "Python path: $PYTHONPATH"
      ls -la  # Check file permissions
      
      # Generate reports with explicit paths
      failextract report --format json --output ./reports/failures.json

2. **Missing dependencies in CI:**

   .. code-block:: yaml

      # .github/workflows/test.yml
      - name: Install dependencies with all extras
        run: |
          pip install failextract[formatters,cli]
          pip list | grep failextract  # Verify installation

3. **Timeout issues:**

   .. code-block:: yaml

      - name: Run tests with timeout
        run: |
          timeout 30m pytest --tb=short || true
          timeout 5m failextract report --format json --output failures.json

**Problem: Report artifacts not uploading**

.. code-block:: yaml

   # Debug artifact creation
   - name: Debug report generation
     run: |
       failextract stats
       ls -la *.json *.md 2>/dev/null || echo "No report files found"
       
   - name: Generate reports with error handling
     run: |
       if ! failextract report --format json --output failures.json; then
         echo "Failed to generate JSON report"
         exit 1
       fi

Error Message Decoder
---------------------

**Common Error Patterns:**

.. code-block:: text

   # Error: "AttributeError: module 'failextract' has no attribute 'extract_on_failure'"
   # Cause: Import error or wrong package
   # Solution: pip install failextract

.. code-block:: text

   # Error: "ValueError: Invalid format 'invalid_format'"
   # Cause: Unsupported output format specified
   # Solution: Use json, markdown, xml, csv, or yaml

.. code-block:: text

   # Error: "TypeError: OutputConfig() missing 1 required positional argument"
   # Cause: Filename not provided to OutputConfig
   # Solution: config = OutputConfig("filename.json")

.. code-block:: text

   # Error: "RuntimeError: No data available"
   # Cause: Trying to generate report with no failures
   # Solution: Check if failures exist before generating report

Debugging Tools and Utilities
------------------------------

**Create a Debug Test Suite**

.. code-block:: python

   #!/usr/bin/env python3
   """FailExtract debugging utility"""

   from failextract import extract_on_failure, FailureExtractor, OutputConfig
   import json
   import os

   def run_debug_tests():
       """Run comprehensive debugging tests."""
       
       print("FailExtract Debug Test Suite")
       print("=" * 40)
       
       # Test 1: Basic functionality
       print("1. Testing basic functionality...")
       
       @extract_on_failure
       def debug_test():
           test_data = {"value": 42}
           assert test_data["value"] == 99, "Debug test assertion"
       
       try:
           debug_test()
       except AssertionError:
           pass
       
       extractor = FailureExtractor()
       print(f"   Captured failures: {len(extractor.failures)}")
       
       # Test 2: Report generation
       print("2. Testing report generation...")
       
       if extractor.failures:
           formats = ["json", "markdown", "xml", "csv"]
           for fmt in formats:
               try:
                   config = OutputConfig(f"debug.{fmt}", format=fmt)
                   extractor.save_report(config)
                   print(f"   ✓ {fmt} format works")
               except Exception as e:
                   print(f"   ✗ {fmt} format failed: {e}")
       
       # Test 3: Memory management
       print("3. Testing memory management...")
       stats = extractor.get_stats()
       limits = extractor.get_memory_limits()
       print(f"   Current usage: {stats['failures_count']} failures, {stats['passed_count']} passed")
       print(f"   Memory limits: {limits['max_failures']} failures, {limits['max_passed']} passed")
       
       # Test 4: Configuration
       print("4. Testing configuration...")
       try:
           config = OutputConfig("test.yaml", format="yaml")
           print("   ✓ YAML configuration accepted")
       except Exception as e:
           print(f"   ⚠ YAML not available: {e}")
       
       print("\nDebug test complete!")

   if __name__ == "__main__":
       run_debug_tests()

**Environment Information Script**

.. code-block:: python

   #!/usr/bin/env python3
   """Collect environment information for troubleshooting"""

   import sys
   import os
   import platform
   
   def collect_environment_info():
       """Collect comprehensive environment information."""
       
       print("FailExtract Environment Information")
       print("=" * 50)
       
       # Python information
       print(f"Python version: {sys.version}")
       print(f"Python executable: {sys.executable}")
       print(f"Platform: {platform.platform()}")
       
       # FailExtract information
       try:
           import failextract
           print(f"FailExtract version: {failextract.__version__}")
           print(f"FailExtract location: {failextract.__file__}")
       except ImportError as e:
           print(f"FailExtract import error: {e}")
       
       # Dependencies
       print("\nDependencies:")
       try:
           import yaml
           print("  ✓ PyYAML available")
       except ImportError:
           print("  ✗ PyYAML not available")
       
       try:
           import rich
           print("  ✓ Rich available")
       except ImportError:
           print("  ✗ Rich not available")
       
       # Environment variables
       print("\nRelevant environment variables:")
       env_vars = ["CI", "PYTEST_CURRENT_TEST", "PYTHONPATH", "PATH"]
       for var in env_vars:
           value = os.getenv(var, "Not set")
           print(f"  {var}: {value}")
       
       # File system
       print(f"\nCurrent directory: {os.getcwd()}")
       print(f"Directory writable: {os.access('.', os.W_OK)}")

   if __name__ == "__main__":
       collect_environment_info()

Getting Help
------------

**Escalation Steps:**

1. **Check this troubleshooting guide** for common issues
2. **Run debug utilities** to gather information
3. **Search existing issues** in the project repository
4. **Create a minimal reproduction case**
5. **Report the issue** with environment information

**Information to Include in Bug Reports:**

.. code-block:: text

   - FailExtract version
   - Python version and platform
   - Minimal code example that reproduces the issue
   - Full error message and traceback
   - Environment information (CI/local, OS, etc.)
   - Expected vs. actual behavior

**Quick Health Check Script:**

.. code-block:: python

   #!/usr/bin/env python3
   """Quick health check for FailExtract"""

   def health_check():
       """Perform quick health check."""
       checks = []
       
       # Import test
       try:
           import failextract
           checks.append(("Import", True, ""))
       except Exception as e:
           checks.append(("Import", False, str(e)))
           return checks
       
       # Basic functionality
       try:
           from failextract import extract_on_failure, FailureExtractor
           
           @extract_on_failure
           def test():
               assert False, "Test"
           
           try:
               test()
           except AssertionError:
               pass
           
           extractor = FailureExtractor()
           if len(extractor.failures) > 0:
               checks.append(("Capture", True, ""))
           else:
               checks.append(("Capture", False, "No failures captured"))
       except Exception as e:
           checks.append(("Capture", False, str(e)))
       
       # Report generation
       try:
           from failextract import OutputConfig
           config = OutputConfig("test.json")
           extractor.save_report(config)
           checks.append(("Reporting", True, ""))
       except Exception as e:
           checks.append(("Reporting", False, str(e)))
       
       # Print results
       print("FailExtract Health Check:")
       for check_name, passed, error in checks:
           status = "✓" if passed else "✗"
           print(f"  {status} {check_name}")
           if error:
               print(f"    Error: {error}")
       
       return all(check[1] for check in checks)

   if __name__ == "__main__":
       healthy = health_check()
       exit(0 if healthy else 1)

Prevention Strategies
---------------------

**Best Practices to Avoid Issues:**

1. **Use virtual environments** to avoid dependency conflicts
2. **Pin versions** in production environments
3. **Test in CI** before deploying
4. **Monitor memory usage** in long-running tests
5. **Clear data regularly** to prevent memory issues
6. **Use proper error handling** around report generation
7. **Validate configurations** before using them

**Monitoring Setup:**

.. code-block:: python

   def setup_monitoring():
       """Set up monitoring to catch issues early."""
       extractor = FailureExtractor()
       
       # Check memory usage periodically
       stats = extractor.get_stats()
       limits = extractor.get_memory_limits()
       
       usage_percent = stats['failures_count'] / limits['max_failures'] * 100
       
       if usage_percent > 80:
           print(f"⚠ High memory usage: {usage_percent:.1f}%")
           # Could trigger alert or automatic cleanup

**You now have comprehensive troubleshooting capabilities for any FailExtract issue!**