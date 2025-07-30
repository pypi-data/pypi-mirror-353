How to Optimize Performance
===========================

**Task**: Configure FailExtract for optimal performance in different environments

This guide shows you how to optimize FailExtract's performance for development, CI/CD, and production environments through configuration and usage patterns.

Understanding Performance Modes
--------------------------------

FailExtract operates in different performance modes based on configuration:

**Static Mode (<5% overhead)**
- Minimal data capture
- Basic exception information only
- Fastest execution
- Best for production monitoring

**Profile Mode (~50% overhead)**  
- Balanced data capture
- Local variables and basic context
- Good performance/detail trade-off
- Best for CI/CD environments

**Trace Mode (~300% overhead)**
- Maximum data capture
- Full context, deep inspection
- Detailed debugging information
- Best for development and debugging

Configuring for Development
---------------------------

**Maximum Detail for Debugging**

.. code-block:: python

   from failextract import extract_on_failure

   # Development mode: capture everything
   @extract_on_failure(
       include_locals=True,      # Capture local variables
       include_fixtures=True,    # Capture pytest fixtures
       max_depth=20,            # Deep variable inspection
       extract_classes=True,     # Extract class instance details
       skip_stdlib=False        # Include all stack frames
   )
   def test_complex_logic():
       # Complex test logic with detailed context capture
       user_data = {"id": 123, "permissions": ["read", "write"]}
       processing_config = {"timeout": 30, "retries": 3}
       
       # This failure will capture all the above context
       assert False, "Development test with full context"

**Development Environment Settings**

.. code-block:: python

   # Configure for development environment
   from failextract import FailureExtractor

   def setup_development_environment():
       extractor = FailureExtractor()
       
       # Set generous memory limits for development
       extractor.set_memory_limits(
           max_failures=2000,    # Keep more failures for analysis
           max_passed=1000       # Track passed tests for statistics
       )
       
       print("Configured for development environment")
       return extractor

Configuring for CI/CD
---------------------

**Balanced Performance and Detail**

.. code-block:: python

   import os
   from failextract import extract_on_failure

   # Detect CI environment
   is_ci = os.getenv("CI") == "true"

   if is_ci:
       # CI mode: balanced performance
       decorator_config = {
           "include_locals": True,
           "include_fixtures": False,  # Skip fixtures for speed
           "max_depth": 8,            # Moderate depth
           "extract_classes": True,
           "skip_stdlib": True        # Skip stdlib frames for speed
       }
   else:
       # Local development: full detail
       decorator_config = {
           "include_locals": True,
           "include_fixtures": True,
           "max_depth": 15,
           "extract_classes": True,
           "skip_stdlib": False
       }

   # Apply environment-specific configuration
   @extract_on_failure(**decorator_config)
   def test_ci_optimized():
       # Test will adapt its capture behavior based on environment
       assert False, "CI-optimized failure capture"

**CI Memory Management**

.. code-block:: python

   def setup_ci_environment():
       """Configure FailExtract for CI/CD environments."""
       extractor = FailureExtractor()
       
       # Conservative memory limits for CI
       extractor.set_memory_limits(
           max_failures=500,     # Reasonable limit for CI
           max_passed=100        # Minimal passed test tracking
       )
       
       # Check current usage
       stats = extractor.get_stats()
       print(f"CI Environment - Current usage: {stats['total_count']} tests")
       
       return extractor

**GitHub Actions Configuration**

.. code-block:: yaml

   # .github/workflows/optimized-tests.yml
   name: Performance-Optimized Tests
   
   on: [push, pull_request]
   
   jobs:
     test:
       runs-on: ubuntu-latest
       steps:
         - uses: actions/checkout@v3
         - uses: actions/setup-python@v4
           with:
             python-version: 3.9
             
         - name: Install dependencies
           run: |
             pip install failextract
             pip install -r requirements.txt
             
         - name: Run tests with performance optimization
           env:
             FAILEXTRACT_MODE: ci
           run: |
             # Run tests with timeout to prevent hangs
             timeout 30m pytest --tb=short || true
             
         - name: Generate lightweight reports
           if: always()
           run: |
             # Generate only essential reports in CI
             failextract report --format json --max-failures 50 --output ci-failures.json

Configuring for Production
--------------------------

**Minimal Overhead for Production Monitoring**

.. code-block:: python

   from failextract import extract_on_failure

   # Production mode: minimal overhead
   @extract_on_failure(
       include_locals=False,     # Skip local variables for speed
       include_fixtures=False,   # Skip fixtures  
       max_depth=3,             # Minimal depth
       extract_classes=False,    # Skip class inspection
       skip_stdlib=True         # Skip stdlib frames
   )
   def test_production_health():
       # Basic health check with minimal capture overhead
       assert service_is_healthy(), "Production health check failed"

**Production Environment Setup**

.. code-block:: python

   def setup_production_environment():
       """Configure FailExtract for production monitoring."""
       extractor = FailureExtractor()
       
       # Strict memory limits for production
       extractor.set_memory_limits(
           max_failures=100,     # Keep only recent failures
           max_passed=50         # Minimal passed tracking
       )
       
       # Monitor memory usage
       stats = extractor.get_stats()
       limits = extractor.get_memory_limits()
       
       print(f"Production setup - Failures: {stats['failures_count']}/{limits['max_failures']}")
       print(f"Production setup - Passed: {stats['passed_count']}/{limits['max_passed']}")
       
       return extractor

Memory Optimization Strategies
------------------------------

**Regular Data Cleanup**

.. code-block:: python

   def memory_efficient_testing():
       """Example of memory-efficient test execution."""
       extractor = FailureExtractor()
       
       # Set strict limits
       extractor.set_memory_limits(max_failures=200, max_passed=100)
       
       # Run tests in batches with cleanup
       for batch in range(5):
           print(f"Running test batch {batch + 1}")
           
           # Run some tests...
           run_test_batch(batch)
           
           # Check memory usage
           stats = extractor.get_stats()
           
           if stats['failures_at_limit'] or stats['passed_at_limit']:
               print("Memory limit reached, generating report and clearing...")
               
               # Generate report before clearing
               config = OutputConfig(f"batch_{batch}_failures.json")
               extractor.save_report(config)
               
               # Clear data to free memory
               extractor.clear()
               print("Memory cleared for next batch")

**Monitoring Memory Usage**

.. code-block:: python

   def monitor_memory_usage():
       """Monitor and report memory usage."""
       extractor = FailureExtractor()
       
       # Get detailed statistics
       stats = extractor.get_stats()
       limits = extractor.get_memory_limits()
       
       print("Memory Usage Report:")
       print(f"  Failures: {stats['failures_count']}/{limits['max_failures']} "
             f"({stats['failures_count']/limits['max_failures']*100:.1f}%)")
       print(f"  Passed: {stats['passed_count']}/{limits['max_passed']} "
             f"({stats['passed_count']/limits['max_passed']*100:.1f}%)")
       print(f"  At limits: Failures={stats['failures_at_limit']}, "
             f"Passed={stats['passed_at_limit']}")
       
       # Return usage percentage
       failure_usage = stats['failures_count'] / limits['max_failures'] * 100
       return failure_usage

Performance Measurement and Benchmarking
-----------------------------------------

**Measuring Capture Overhead**

.. code-block:: python

   import time
   from failextract import extract_on_failure

   def benchmark_capture_overhead():
       """Measure the performance impact of different configurations."""
       
       # Test function without decoration
       def baseline_test():
           data = {"key": "value", "number": 42}
           assert data["key"] == "different", "Baseline test failure"
       
       # Test with minimal capture
       @extract_on_failure(include_locals=False, max_depth=1)
       def minimal_test():
           data = {"key": "value", "number": 42}
           assert data["key"] == "different", "Minimal capture test"
       
       # Test with full capture  
       @extract_on_failure(include_locals=True, max_depth=15)
       def full_test():
           data = {"key": "value", "number": 42}
           assert data["key"] == "different", "Full capture test"
       
       # Benchmark each approach
       iterations = 1000
       
       # Baseline measurement
       start_time = time.time()
       for _ in range(iterations):
           try:
               baseline_test()
           except AssertionError:
               pass
       baseline_time = time.time() - start_time
       
       # Minimal capture measurement
       start_time = time.time()
       for _ in range(iterations):
           try:
               minimal_test()
           except AssertionError:
               pass
       minimal_time = time.time() - start_time
       
       # Full capture measurement
       start_time = time.time()
       for _ in range(iterations):
           try:
               full_test()
           except AssertionError:
               pass
       full_time = time.time() - start_time
       
       # Report results
       print(f"Performance Benchmark ({iterations} iterations):")
       print(f"  Baseline (no capture): {baseline_time:.4f}s")
       print(f"  Minimal capture: {minimal_time:.4f}s ({minimal_time/baseline_time:.1f}x)")
       print(f"  Full capture: {full_time:.4f}s ({full_time/baseline_time:.1f}x)")

**Automated Performance Testing**

.. code-block:: python

   def performance_regression_test():
       """Test for performance regressions."""
       extractor = FailureExtractor()
       
       # Define performance budget (maximum acceptable overhead)
       max_overhead_percent = 10  # 10% maximum overhead
       
       # Run performance test
       overhead = measure_overhead()
       
       if overhead > max_overhead_percent:
           print(f"❌ Performance regression: {overhead:.1f}% overhead (max: {max_overhead_percent}%)")
           return False
       else:
           print(f"✅ Performance within budget: {overhead:.1f}% overhead")
           return True
       
   def measure_overhead():
       """Measure actual overhead of failure extraction."""
       # Implementation depends on your specific measurement approach
       return 5.2  # Example: 5.2% overhead

Optimizing for Large Test Suites
---------------------------------

**Batch Processing Strategy**

.. code-block:: python

   def process_large_test_suite():
       """Handle large test suites efficiently."""
       extractor = FailureExtractor()
       
       # Configure for large-scale processing
       extractor.set_memory_limits(max_failures=500, max_passed=200)
       
       test_batches = [
           "unit_tests", "integration_tests", "e2e_tests", 
           "performance_tests", "security_tests"
       ]
       
       all_reports = []
       
       for batch_name in test_batches:
           print(f"Processing {batch_name}...")
           
           # Run tests for this batch
           run_test_batch(batch_name)
           
           # Generate batch report
           batch_report = f"{batch_name}_failures.json"
           config = OutputConfig(batch_report)
           extractor.save_report(config)
           all_reports.append(batch_report)
           
           # Clear for next batch
           extractor.clear()
           print(f"Completed {batch_name}, memory cleared")
       
       return all_reports

**Selective Capture Strategy**

.. code-block:: python

   import random
   from failextract import extract_on_failure

   def selective_capture_decorator(capture_rate=0.1):
       """Decorator that captures only a percentage of failures."""
       def decorator(func):
           if random.random() < capture_rate:
               return extract_on_failure(func)
           else:
               return func
       return decorator

   # Use selective capture for performance-critical paths
   @selective_capture_decorator(capture_rate=0.05)  # Capture 5% of failures
   def test_high_volume():
       """High-volume test with selective capture."""
       assert False, "This will only be captured 5% of the time"

Environment-Specific Configuration
----------------------------------

**Dynamic Configuration Based on Environment**

.. code-block:: python

   import os
   from failextract import extract_on_failure, FailureExtractor

   class PerformanceConfigurator:
       """Dynamic performance configuration based on environment."""
       
       @staticmethod
       def get_environment():
           """Detect current environment."""
           if os.getenv("CI"):
               return "ci"
           elif os.getenv("PRODUCTION"):
               return "production"
           elif os.getenv("PYTEST_CURRENT_TEST"):
               return "test"
           else:
               return "development"
       
       @staticmethod
       def get_config(environment=None):
           """Get performance configuration for environment."""
           env = environment or PerformanceConfigurator.get_environment()
           
           configs = {
               "development": {
                   "include_locals": True,
                   "include_fixtures": True,
                   "max_depth": 20,
                   "extract_classes": True,
                   "skip_stdlib": False,
                   "memory_limits": {"max_failures": 2000, "max_passed": 1000}
               },
               "ci": {
                   "include_locals": True,
                   "include_fixtures": False,
                   "max_depth": 8,
                   "extract_classes": True,
                   "skip_stdlib": True,
                   "memory_limits": {"max_failures": 500, "max_passed": 100}
               },
               "production": {
                   "include_locals": False,
                   "include_fixtures": False,
                   "max_depth": 3,
                   "extract_classes": False,
                   "skip_stdlib": True,
                   "memory_limits": {"max_failures": 100, "max_passed": 50}
               }
           }
           
           return configs.get(env, configs["development"])
       
       @staticmethod
       def configure_extractor():
           """Configure extractor for current environment."""
           config = PerformanceConfigurator.get_config()
           extractor = FailureExtractor()
           
           # Apply memory limits
           extractor.set_memory_limits(**config["memory_limits"])
           
           print(f"Configured for {PerformanceConfigurator.get_environment()} environment")
           return extractor, config

   # Use dynamic configuration
   extractor, config = PerformanceConfigurator.configure_extractor()

   # Apply configuration to decorator
   @extract_on_failure(**{k: v for k, v in config.items() if k != "memory_limits"})
   def test_environment_optimized():
       """Test with environment-specific optimization."""
       assert False, "Environment-optimized test failure"

Performance Monitoring and Alerting
------------------------------------

**Performance Metrics Collection**

.. code-block:: python

   def collect_performance_metrics():
       """Collect performance metrics for monitoring."""
       extractor = FailureExtractor()
       stats = extractor.get_stats()
       limits = extractor.get_memory_limits()
       
       metrics = {
           "memory_usage_percent": {
               "failures": stats['failures_count'] / limits['max_failures'] * 100,
               "passed": stats['passed_count'] / limits['max_passed'] * 100
           },
           "at_limits": {
               "failures": stats['failures_at_limit'],
               "passed": stats['passed_at_limit']
           },
           "total_tests": stats['total_count']
       }
       
       # Send to monitoring system (example)
       # send_metrics_to_datadog(metrics)
       # send_metrics_to_prometheus(metrics)
       
       return metrics

**Performance Alerts**

.. code-block:: python

   def check_performance_alerts():
       """Check for performance issues and alert if necessary."""
       metrics = collect_performance_metrics()
       
       alerts = []
       
       # Memory usage alerts
       if metrics["memory_usage_percent"]["failures"] > 80:
           alerts.append("High failure memory usage")
       
       if metrics["at_limits"]["failures"]:
           alerts.append("Failure memory limit reached")
       
       # Performance degradation alerts
       current_overhead = measure_overhead()
       if current_overhead > 20:  # 20% overhead threshold
           alerts.append(f"High performance overhead: {current_overhead:.1f}%")
       
       if alerts:
           print("🚨 Performance Alerts:")
           for alert in alerts:
               print(f"  - {alert}")
           
           # Send alerts to monitoring system
           # send_alert_to_slack(alerts)
           # send_alert_to_pagerduty(alerts)
       
       return alerts

Best Practices Summary
----------------------

**Development Environment**
- Use maximum detail capture (include_locals=True, max_depth=20)
- Set generous memory limits (max_failures=2000)
- Include all context for debugging

**CI/CD Environment**  
- Use balanced configuration (include_locals=True, max_depth=8)
- Conservative memory limits (max_failures=500)
- Skip stdlib frames for speed

**Production Environment**
- Use minimal capture (include_locals=False, max_depth=3)
- Strict memory limits (max_failures=100)
- Regular cleanup and monitoring

**General Guidelines**
- Monitor memory usage regularly
- Clear data between test sessions
- Use environment-specific configuration
- Measure performance overhead periodically
- Set up alerts for performance degradation

Next Steps
----------

After optimizing performance:

1. **Monitor in Production**: Set up performance monitoring and alerting
2. **Benchmark Regularly**: Include performance tests in your CI/CD
3. **Profile Memory Usage**: Monitor memory patterns in long-running tests
4. **Customize Further**: Create environment-specific configuration files

Key Performance Optimization Takeaways
---------------------------------------

| ✅ **Environment-specific configuration** - Development, CI/CD, and production modes  
| ✅ **Memory management** - Limits, cleanup, and monitoring capabilities  
| ✅ **Performance measurement** - Overhead benchmarking and regression testing  
| ✅ **Selective capture** - Balance detail with performance requirements  
| ✅ **Batch processing** - Handle large test suites efficiently  
| ✅ **Monitoring and alerting** - Track performance metrics continuously  

**You now have complete control over FailExtract's performance characteristics!**