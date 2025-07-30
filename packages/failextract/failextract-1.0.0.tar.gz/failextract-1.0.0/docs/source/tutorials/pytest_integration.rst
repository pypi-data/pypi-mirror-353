Integrating FailExtract with pytest
====================================

**Purpose**: Set up automatic failure capture for your entire test suite

This tutorial shows you how to integrate FailExtract with pytest for seamless, automatic failure capture across all your tests. No more manual decorator application - just run your tests and get comprehensive failure reports.

What You'll Learn
-----------------

- How to set up automatic failure capture using pytest hooks
- How to create selective capture with pytest markers
- How to generate session-level reports after test runs
- How to configure different integration approaches for different needs
- How to handle parametrized tests and fixtures with FailExtract

Prerequisites
-------------

- Completed :doc:`getting_started`, :doc:`multiple_formats`, and :doc:`configuration`
- Working pytest installation (``pip install pytest``)
- Understanding of pytest basics (fixtures, conftest.py, markers)
- 20 minutes of time

Integration Overview
--------------------

FailExtract offers four integration approaches with pytest:

1. **Direct Decorator** - Apply ``@extract_on_failure`` to individual tests
2. **Pytest Markers** - Use markers for selective automatic capture
3. **Automatic Hooks** - Capture all test failures automatically
4. **Custom Plugin** - Full-featured plugin with advanced configuration

Each approach serves different use cases and complexity levels.

Quick Start: Basic conftest.py Setup
-------------------------------------

Create or update your project's ``conftest.py`` file:

.. code-block:: python

   # conftest.py
   import pytest
   from failextract import FailureExtractor, OutputConfig

   def pytest_sessionfinish(session, exitstatus):
       """Generate failure report at end of test session."""
       extractor = FailureExtractor()
       
       if extractor.failures:
           print(f"\\nGenerating failure report for {len(extractor.failures)} failures...")
           
           # Generate Markdown report for human review
           md_config = OutputConfig("test_failures.md", format="markdown")
           extractor.save_report(md_config)
           print("Generated test_failures.md")
           
           # Generate JSON report for CI/CD
           json_config = OutputConfig("test_failures.json", format="json")
           extractor.save_report(json_config)
           print("Generated test_failures.json")
       else:
           print("\\n✅ All tests passed - no failure report needed")

Now run your tests normally:

.. code-block:: bash

   pytest -v

If any tests decorated with ``@extract_on_failure`` fail, you'll get automatic reports!

Approach 1: Direct Decorator Usage
-----------------------------------

Apply decorators directly to tests you want to monitor:

.. code-block:: python

   # test_example.py
   import pytest
   from failextract import extract_on_failure

   @extract_on_failure
   def test_database_connection():
       """Test that will be captured if it fails."""
       connection = get_database_connection()
       assert connection.is_alive(), "Database connection failed"

   @extract_on_failure
   def test_api_response():
       """API test with failure capture."""
       response = api_client.get("/users")
       assert response.status_code == 200, f"API returned {response.status_code}"

   def test_regular_test():
       """Regular test without capture."""
       assert 2 + 2 == 4

**When to use**: When you want precise control over which tests are captured.

Approach 2: Selective Capture with Markers
-------------------------------------------

Use pytest markers for automatic capture without decorating every function:

**conftest.py setup:**

.. code-block:: python

   # conftest.py
   import pytest
   from failextract import FailureExtractor, OutputConfig, extract_on_failure

   @pytest.fixture(autouse=True)
   def failure_capture(request):
       """Fixture to automatically capture failures for marked tests."""
       
       # Only capture for tests marked with @pytest.mark.capture_failures
       if request.node.get_closest_marker("capture_failures"):
           # Wrap the test function
           original_func = request.function
           
           if not hasattr(original_func, '_failextract_wrapped'):
               decorated_func = extract_on_failure(original_func)
               decorated_func._failextract_wrapped = True
               request.function = decorated_func
       
       yield  # Test runs here

   def pytest_configure(config):
       """Register custom markers."""
       config.addinivalue_line(
           "markers", "capture_failures: mark test to capture failures with FailExtract"
       )

**Test file usage:**

.. code-block:: python

   # test_marked.py
   import pytest

   @pytest.mark.capture_failures
   def test_with_capture():
       """This test will be captured if it fails."""
       data = {"key": "value"}
       assert data["missing_key"] == "expected", "Missing key error"

   def test_without_capture():
       """This test won't be captured."""
       assert False, "This failure won't be captured"

**When to use**: When you want automatic capture for specific test categories.

Approach 3: Automatic Capture for All Failures
------------------------------------------------

Automatically capture ALL test failures without any decorators or markers:

**conftest.py setup:**

.. code-block:: python

   # conftest.py
   import pytest
   from failextract import FailureExtractor, OutputConfig, extract_on_failure

   def pytest_runtest_makereport(item, call):
       """Capture test results automatically."""
       if call.when == "call" and call.excinfo is not None:
           # Test failed - capture it
           extractor = FailureExtractor()
           
           # Create a failure record
           failure_data = {
               "test_name": item.name,
               "test_module": item.module.__name__ if item.module else "unknown",
               "test_file": str(item.fspath),
               "exception_type": call.excinfo.type.__name__,
               "exception_message": str(call.excinfo.value),
               "timestamp": call.start,
           }
           
           # Add local variables if available
           if hasattr(call.excinfo, 'tb') and call.excinfo.tb:
               frame = call.excinfo.tb.tb_frame
               failure_data["local_variables"] = dict(frame.f_locals)
           
           extractor.add_failure(failure_data)

   def pytest_sessionfinish(session, exitstatus):
       """Generate comprehensive report at end."""
       extractor = FailureExtractor()
       
       if extractor.failures:
           print(f"\\n📊 Captured {len(extractor.failures)} test failures")
           
           # Generate multiple format reports
           formats = ["json", "markdown", "csv", "xml"]
           for fmt in formats:
               try:
                   config = OutputConfig(f"all_failures.{fmt}", format=fmt)
                   extractor.save_report(config)
                   print(f"✓ Generated all_failures.{fmt}")
               except Exception as e:
                   print(f"✗ Failed to generate {fmt}: {e}")

**When to use**: For comprehensive test monitoring without any test file modifications.

Approach 4: Custom Plugin with Advanced Features
-------------------------------------------------

Create a full-featured plugin for maximum flexibility:

**conftest.py setup:**

.. code-block:: python

   # conftest.py
   import pytest
   from failextract import FailureExtractor, OutputConfig, extract_on_failure

   class FailExtractPlugin:
       """Advanced FailExtract pytest plugin."""
       
       def __init__(self):
           self.extractor = FailureExtractor()
           self.config = None
       
       def pytest_configure(self, config):
           """Configure plugin based on pytest options."""
           self.config = config
           
           # Set memory limits based on test count estimate
           self.extractor.set_memory_limits(max_failures=500, max_passed=100)
       
       def pytest_runtest_call(self, pyfuncitem):
           """Called during test execution."""
           # Apply extraction for marked tests
           if pyfuncitem.get_closest_marker("extract_failures"):
               original_func = pyfuncitem.obj
               if not hasattr(original_func, '_failextract_wrapped'):
                   decorated_func = extract_on_failure(
                       include_locals=True,
                       include_fixtures=True,
                       max_depth=10
                   )(original_func)
                   decorated_func._failextract_wrapped = True
                   pyfuncitem.obj = decorated_func
       
       def pytest_runtest_makereport(self, item, call):
           """Capture detailed test information."""
           if call.when == "call":
               if call.excinfo is not None:
                   # Test failed - enhanced capture
                   failure_data = {
                       "test_name": item.name,
                       "test_module": item.module.__name__ if item.module else "unknown",
                       "test_file": str(item.fspath),
                       "test_line": item.location[1] if item.location else None,
                       "exception_type": call.excinfo.type.__name__,
                       "exception_message": str(call.excinfo.value),
                       "timestamp": call.start,
                       "duration": call.stop - call.start,
                       "markers": [mark.name for mark in item.iter_markers()],
                   }
                   
                   self.extractor.add_failure(failure_data)
               else:
                   # Test passed - track for statistics
                   passed_data = {
                       "test_name": item.name,
                       "timestamp": call.start,
                       "duration": call.stop - call.start,
                   }
                   self.extractor.add_passed(passed_data)
       
       def pytest_terminal_summary(self, terminalreporter, exitstatus):
           """Enhanced terminal summary."""
           stats = self.extractor.get_stats()
           
           if stats['failures_count'] > 0:
               terminalreporter.write_sep("=", "FailExtract Summary")
               terminalreporter.write_line(
                   f"Captured {stats['failures_count']} failures "
                   f"out of {stats['total_count']} total tests"
               )
               
               # Generate reports
               formats = ["json", "xml"]
               for fmt in formats:
                   try:
                       config = OutputConfig(f"pytest_failures.{fmt}", format=fmt)
                       self.extractor.save_report(config)
                       terminalreporter.write_line(f"Generated pytest_failures.{fmt}")
                   except Exception as e:
                       terminalreporter.write_line(f"Failed to generate {fmt}: {e}")

   def pytest_configure(config):
       """Register the plugin and markers."""
       config.pluginmanager.register(FailExtractPlugin(), "failextract")
       
       config.addinivalue_line(
           "markers", "extract_failures: mark test for automatic failure extraction"
       )

**Test usage:**

.. code-block:: python

   # test_advanced.py
   import pytest

   @pytest.mark.extract_failures
   def test_with_advanced_capture():
       """Test with advanced plugin capture."""
       config = {"timeout": 30, "retries": 3}
       assert config["timeout"] > 60, "Timeout too short"

**When to use**: For production environments requiring detailed monitoring and statistics.

Handling Complex Test Scenarios
--------------------------------

**Parametrized Tests**

.. code-block:: python

   import pytest
   from failextract import extract_on_failure

   @pytest.mark.parametrize("value,expected", [
       (1, 2),
       (2, 4), 
       (3, 6),
       (4, 9),  # This will fail: 4*2=8, not 9
   ])
   @extract_on_failure
   def test_parametrized(value, expected):
       """Parametrized test with failure capture."""
       result = value * 2
       assert result == expected, f"Expected {expected}, got {result}"

**Fixture-Dependent Tests**

.. code-block:: python

   @pytest.fixture
   def database_connection():
       """Sample fixture providing database connection."""
       return MockDatabase(connected=False)  # Simulate connection failure

   @extract_on_failure
   def test_with_fixture(database_connection):
       """Test using fixture - fixture values will be captured."""
       assert database_connection.is_connected(), "Database should be connected"

**Class-Based Tests**

.. code-block:: python

   class TestUserService:
       """Test class with FailExtract integration."""
       
       @pytest.fixture(autouse=True)
       def setup(self):
           """Setup for test class."""
           self.user_service = UserService()
           self.test_user = {"id": 1, "name": "Alice"}
       
       @extract_on_failure
       def test_user_creation(self):
           """Test user creation with context capture."""
           new_user = self.user_service.create_user(self.test_user)
           assert new_user["status"] == "active", "New user should be active"

CI/CD Integration Patterns
---------------------------

**GitHub Actions Integration**

.. code-block:: yaml

   # .github/workflows/test.yml
   name: Tests with FailExtract
   
   on: [push, pull_request]
   
   jobs:
     test:
       runs-on: ubuntu-latest
       steps:
         - uses: actions/checkout@v2
         - name: Set up Python
           uses: actions/setup-python@v2
           with:
             python-version: 3.9
         
         - name: Install dependencies
           run: |
             pip install pytest failextract
             pip install -r requirements.txt
         
         - name: Run tests with FailExtract
           run: |
             pytest -v --tb=short
         
         - name: Upload failure reports
           if: failure()
           uses: actions/upload-artifact@v4
           with:
             name: test-failure-reports
             path: |
               test_failures.xml
               test_failures.json

**Production Configuration**

.. code-block:: python

   # conftest.py for production
   import os
   from failextract import FailureExtractor, OutputConfig

   def pytest_sessionfinish(session, exitstatus):
       """Production-optimized session reporting."""
       extractor = FailureExtractor()
       
       if extractor.failures:
           # Configure based on environment
           is_ci = os.getenv("CI") == "true"
           
           if is_ci:
               # CI environment - JSON for automation
               config = OutputConfig("ci_failures.json", format="json")
               extractor.save_report(config)
               print(f"Generated CI failure report with {len(extractor.failures)} failures")
           else:
               # Local development - Markdown for review
               config = OutputConfig("dev_failures.md", format="markdown")
               extractor.save_report(config)
               print(f"Generated development failure report: dev_failures.md")

Complete Integration Example
----------------------------

Here's a complete working example combining all approaches:

.. code-block:: python

   # conftest.py - Complete integration
   import pytest
   import os
   from failextract import FailureExtractor, OutputConfig, extract_on_failure

   class ComprehensiveFailExtractPlugin:
       """Complete integration plugin."""
       
       def __init__(self):
           self.extractor = FailureExtractor()
           self.setup_environment()
       
       def setup_environment(self):
           """Configure based on environment."""
           env = os.getenv("TEST_ENV", "development")
           
           if env == "production":
               self.extractor.set_memory_limits(max_failures=100, max_passed=50)
           else:
               self.extractor.set_memory_limits(max_failures=1000, max_passed=500)
       
       def pytest_runtest_call(self, pyfuncitem):
           """Handle different capture strategies."""
           # Strategy 1: Automatic for marked tests
           if pyfuncitem.get_closest_marker("capture_failures"):
               original_func = pyfuncitem.obj
               if not hasattr(original_func, '_failextract_wrapped'):
                   decorated_func = extract_on_failure(original_func)
                   decorated_func._failextract_wrapped = True
                   pyfuncitem.obj = decorated_func
       
       def pytest_terminal_summary(self, terminalreporter, exitstatus):
           """Generate comprehensive reports."""
           stats = self.extractor.get_stats()
           
           if stats['failures_count'] > 0:
               terminalreporter.write_sep("=", "Test Failure Summary")
               terminalreporter.write_line(
                   f"📊 {stats['failures_count']} failures captured"
               )
               
               # Generate environment-appropriate reports
               env = os.getenv("TEST_ENV", "development")
               
               if env == "ci":
                   # CI: JSON + CSV for automation
                   for fmt in ["json", "csv"]:
                       config = OutputConfig(f"ci_failures.{fmt}", format=fmt)
                       self.extractor.save_report(config)
                       terminalreporter.write_line(f"✓ Generated ci_failures.{fmt}")
               else:
                   # Development: Markdown + XML for review
                   for fmt in ["markdown", "xml"]:
                       config = OutputConfig(f"dev_failures.{fmt}", format=fmt)
                       self.extractor.save_report(config)
                       terminalreporter.write_line(f"✓ Generated dev_failures.{fmt}")

   def pytest_configure(config):
       """Register plugin and configure markers."""
       config.pluginmanager.register(ComprehensiveFailExtractPlugin(), "failextract")
       
       # Register markers
       config.addinivalue_line(
           "markers", "capture_failures: automatically capture test failures"
       )

Troubleshooting Integration Issues
----------------------------------

**Common Issues and Solutions**

1. **No failures captured**

   .. code-block:: python

      # Debug: Check if extractor has failures
      def pytest_sessionfinish(session, exitstatus):
          extractor = FailureExtractor()
          print(f"Debug: {len(extractor.failures)} failures captured")
          if not extractor.failures:
              print("No failures found - check decorator usage")

2. **Memory issues with large test suites**

   .. code-block:: python

      # Set appropriate limits
      def pytest_configure(config):
          extractor = FailureExtractor()
          extractor.set_memory_limits(max_failures=200, max_passed=100)

3. **Plugin conflicts**

   .. code-block:: python

      # Use unique plugin names
      def pytest_configure(config):
          if not config.pluginmanager.has_plugin("failextract"):
              config.pluginmanager.register(FailExtractPlugin(), "failextract")

Next Steps
----------

Now that you have pytest integration working:

- **Create Custom Formatters**: :doc:`custom_formatters` - Build specialized output for your tools
- **Optimize Performance**: Learn advanced configuration for large test suites
- **Set Up CI/CD**: Automate failure reporting in your deployment pipeline
- **Monitor Production**: Use FailExtract for production test monitoring

Key Integration Takeaways
--------------------------

| ✅ **Multiple integration patterns** for different complexity needs  
| ✅ **Automatic session reporting** with environment-aware configuration  
| ✅ **Selective capture** using pytest markers and fixtures  
| ✅ **Advanced plugin system** for comprehensive test monitoring  
| ✅ **CI/CD ready** with JSON output for automation  
| ✅ **Production scalable** with memory management and limits  

**Your test suite now has comprehensive failure monitoring!**