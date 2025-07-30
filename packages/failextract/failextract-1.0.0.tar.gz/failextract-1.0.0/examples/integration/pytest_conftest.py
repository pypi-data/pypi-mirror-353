#!/usr/bin/env python3
"""
Integration example: pytest conftest.py integration

This example shows how to integrate FailExtract with pytest using conftest.py
for automatic failure capture across your entire test suite.
"""

import pytest
from pathlib import Path
from failextract import FailureExtractor, OutputConfig


# conftest.py content for pytest integration
CONFTEST_CONTENT = '''
"""
Pytest configuration with FailExtract integration.

Add this to your project's conftest.py to automatically capture
test failures and generate reports.
"""

import pytest
from failextract import FailureExtractor, OutputConfig, extract_on_failure


# Option 1: Use pytest hooks for automatic capture
def pytest_runtest_makereport(item, call):
    """Capture test results automatically."""
    if call.when == "call":  # Only capture during test execution
        extractor = FailureExtractor()
        
        if call.excinfo is not None:  # Test failed
            # Extract test function
            test_func = item.function
            
            # Apply extraction decorator dynamically
            if not hasattr(test_func, '_failextract_wrapped'):
                decorated_func = extract_on_failure(test_func)
                decorated_func._failextract_wrapped = True
                
                # Execute the decorated function to capture failure
                try:
                    decorated_func(*item.funcargs.values() if hasattr(item, 'funcargs') else [])
                except:
                    pass  # Failure already captured


def pytest_sessionfinish(session, exitstatus):
    """Generate failure report at end of test session."""
    extractor = FailureExtractor()
    
    if extractor.failures:
        print(f"\\nGenerating failure report for {len(extractor.failures)} failures...")
        
        # Generate HTML report
        config = OutputConfig("test_failures.html", format="html")
        extractor.save_report(config)
        print("Generated test_failures.html")
        
        # Generate JSON report for CI/CD
        config = OutputConfig("test_failures.json", format="json")
        extractor.save_report(config)
        print("Generated test_failures.json")
    else:
        print("\\n✅ All tests passed - no failure report needed")


# Option 2: Fixture-based approach for selective capture
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
    
    yield
    
    # Optional: Clean up or additional processing after test


# Option 3: Custom pytest plugin
class FailExtractPlugin:
    """Custom pytest plugin for FailExtract integration."""
    
    def __init__(self):
        self.extractor = FailureExtractor()
    
    def pytest_runtest_setup(self, item):
        """Setup before each test."""
        # You can add pre-test setup here
        pass
    
    def pytest_runtest_call(self, pyfuncitem):
        """Called during test execution."""
        # Apply extraction decorator if test has the marker
        if pyfuncitem.get_closest_marker("extract_failures"):
            original_func = pyfuncitem.obj
            if not hasattr(original_func, '_failextract_wrapped'):
                decorated_func = extract_on_failure(original_func)
                decorated_func._failextract_wrapped = True
                pyfuncitem.obj = decorated_func
    
    def pytest_terminal_summary(self, terminalreporter, exitstatus):
        """Print summary at end of test session."""
        if self.extractor.failures:
            terminalreporter.write_sep("=", "FailExtract Summary")
            terminalreporter.write_line(f"Captured {len(self.extractor.failures)} test failures")
            
            # Generate reports
            config = OutputConfig("pytest_failures.html", format="html")
            self.extractor.save_report(config)
            terminalreporter.write_line("Generated pytest_failures.html")


# Register the plugin
def pytest_configure(config):
    """Register the FailExtract plugin."""
    config.pluginmanager.register(FailExtractPlugin(), "failextract")


# Custom markers
def pytest_configure(config):
    """Register custom markers."""
    config.addinivalue_line(
        "markers", "capture_failures: mark test to capture failures with FailExtract"
    )
    config.addinivalue_line(
        "markers", "extract_failures: mark test for automatic failure extraction"
    )
'''


# Example test files to demonstrate integration
TEST_FILE_CONTENT = '''
"""
Example test file showing different integration approaches.
"""

import pytest
from failextract import extract_on_failure


# Method 1: Direct decorator usage
@extract_on_failure
def test_direct_decorator():
    """Test with direct decorator application."""
    assert 1 == 2, "This will be captured directly"


# Method 2: Using pytest marker for selective capture
@pytest.mark.capture_failures
def test_with_marker():
    """Test marked for failure capture via fixture."""
    data = {"key": "value"}
    assert data["missing_key"] == "expected", "Missing key error"


# Method 3: Using custom plugin marker
@pytest.mark.extract_failures
def test_with_plugin_marker():
    """Test marked for failure extraction via plugin."""
    numbers = [1, 2, 3]
    assert len(numbers) > 5, "Not enough numbers in list"


# Regular test without any special handling
def test_regular_test():
    """Regular test that won't be captured unless hooks are used."""
    result = 2 + 2
    assert result == 5, "Math is broken"


# Test that passes (for comparison)
def test_passing_test():
    """This test should pass."""
    assert True, "This always passes"


class TestClassExample:
    """Example test class."""
    
    @extract_on_failure
    def test_class_method(self):
        """Test method in a class."""
        self.data = {"status": "error"}
        assert self.data["status"] == "success", "Status check failed"
    
    @pytest.mark.capture_failures
    def test_marked_class_method(self):
        """Class method with marker."""
        assert hasattr(self, "non_existent_attr"), "Missing attribute"


# Parametrized test example
@pytest.mark.parametrize("value,expected", [
    (1, 2),
    (2, 4),
    (3, 6),
    (4, 9),  # This will fail
])
@extract_on_failure
def test_parametrized(value, expected):
    """Parametrized test with extraction."""
    result = value * 2
    assert result == expected, f"Expected {expected}, got {result}"


# Fixture-dependent test
@pytest.fixture
def sample_data():
    """Sample fixture providing test data."""
    return {"users": ["alice", "bob"], "count": 2}


@extract_on_failure  
def test_with_fixture(sample_data):
    """Test using a fixture."""
    assert len(sample_data["users"]) > 5, "Not enough users in sample data"
'''


def create_integration_files():
    """Create example integration files."""
    
    # Create conftest.py
    with open("example_conftest.py", "w") as f:
        f.write(CONFTEST_CONTENT)
    
    # Create test file
    with open("example_test_integration.py", "w") as f:
        f.write(TEST_FILE_CONTENT)
    
    print("Created integration example files:")
    print("  - example_conftest.py (copy to your conftest.py)")
    print("  - example_test_integration.py (example test file)")


def demonstrate_manual_integration():
    """Demonstrate manual integration without pytest."""
    
    print("\\nDemonstrating manual integration...")
    
    # Simulate running tests manually
    from failextract import extract_on_failure
    
    @extract_on_failure
    def test_integration_example():
        """Example test for integration demo."""
        config = {"debug": False, "timeout": 30}
        assert config["debug"] == True, "Debug mode should be enabled"
    
    # Run the test
    try:
        test_integration_example()
    except AssertionError:
        pass
    
    # Generate report
    extractor = FailureExtractor()
    if extractor.failures:
        config = OutputConfig("integration_demo.html", format="html") 
        extractor.save_report(config)
        print(f"Generated integration_demo.html with {len(extractor.failures)} failures")


if __name__ == "__main__":
    print("FailExtract pytest integration example")
    print("=" * 50)
    
    create_integration_files()
    demonstrate_manual_integration()
    
    print("\\nTo use with pytest:")
    print("1. Copy example_conftest.py content to your conftest.py")
    print("2. Run: pytest example_test_integration.py -v")
    print("3. Check generated reports: test_failures.html and test_failures.json")
    
    print("\\nIntegration approaches:")
    print("• Direct decorator: @extract_on_failure")
    print("• Pytest markers: @pytest.mark.capture_failures") 
    print("• Automatic hooks: pytest_runtest_makereport")
    print("• Custom plugin: FailExtractPlugin")