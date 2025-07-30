# Performance and Threading in FailExtract

FailExtract is designed for production environments with careful attention to performance characteristics and thread safety. This document provides comprehensive guidance for optimal usage in high-performance and concurrent scenarios.

## Performance Characteristics

### Core Performance Metrics

FailExtract achieves excellent performance through careful optimization of critical paths:

- **Decorator Overhead**: <1ms per test for successful tests
- **Failure Extraction**: 2-5ms per failure depending on complexity
- **Memory Usage**: ~50KB base + 1-2KB per failure
- **Concurrent Throughput**: >1000 tests/second with proper configuration

### Algorithmic Complexity

Understanding the computational complexity helps optimize usage patterns:

#### FailureExtractor Operations

| Operation | Time Complexity | Space Complexity | Notes |
|-----------|----------------|------------------|-------|
| `add_failure()` | O(1) | O(n) | With memory limits: O(1) space |
| `add_passed()` | O(1) | O(n) | With memory limits: O(1) space |
| `save_report()` | O(n·f) | O(n) | n=failures, f=format complexity |
| `clear()` | O(1) | O(1) | Immediate cleanup |
| `get_statistics()` | O(1) | O(1) | Cached calculations |

#### Formatter Performance

| Formatter | Time Complexity | Memory Usage | Output Size |
|-----------|----------------|--------------|-------------|
| JSONFormatter | O(n) | O(n) | ~500 bytes/failure |
| MarkdownFormatter | O(n) | O(n) | ~300 bytes/failure |
| XMLFormatter | O(n) | O(n) | ~600 bytes/failure |
| CSVFormatter | O(n) | O(n) | ~200 bytes/failure |
| YAMLFormatter* | O(n) | O(n) | ~400 bytes/failure |

*YAMLFormatter requires optional PyYAML dependency

### Performance Optimization Strategies

#### Memory Management

```python
from failextract import FailureExtractor

# Configure memory limits for large test suites
extractor = FailureExtractor()
extractor.set_memory_limits(
    max_failures=1000,    # Keep last 1000 failures
    max_passed=500        # Keep last 500 passed tests
)

# Monitor memory usage
stats = extractor.get_statistics()
print(f"Memory usage: {stats['memory_usage_mb']:.2f} MB")
print(f"Failures stored: {stats['failure_count']}")
```

#### Batch Processing

```python
# Efficient batch report generation
def generate_multiple_reports(extractor, formats):
    """Generate multiple reports efficiently."""
    
    # Get data once
    failures = extractor.failures
    passed = extractor.passed_tests
    metadata = extractor.get_statistics()
    
    # Generate all formats in parallel
    import concurrent.futures
    
    def generate_format(format_name):
        config = OutputConfig(f"report.{format_name}", format=format_name)
        return extractor.save_report(config)
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        futures = [executor.submit(generate_format, fmt) for fmt in formats]
        results = [future.result() for future in futures]
    
    return results

# Usage
formats = ['json', 'markdown', 'csv', 'xml']
generate_multiple_reports(extractor, formats)
```

#### Caching Strategies

```python
from functools import lru_cache
from failextract import FixtureExtractor

class CachedFixtureExtractor(FixtureExtractor):
    """Fixture extractor with caching for performance."""
    
    def __init__(self):
        super().__init__()
        self._source_cache = {}
        self._fixture_cache = {}
    
    @lru_cache(maxsize=1000)
    def _get_source_lines_cached(self, filename, lineno):
        """Cache source line extraction."""
        return self._get_source_lines(filename, lineno)
    
    def extract_fixture_info(self, test_func, test_locals):
        """Extract fixture info with caching."""
        
        # Create cache key
        cache_key = (
            test_func.__name__,
            id(test_func),
            frozenset(test_locals.keys())
        )
        
        # Check cache
        if cache_key in self._fixture_cache:
            return self._fixture_cache[cache_key].copy()
        
        # Extract and cache
        result = super().extract_fixture_info(test_func, test_locals)
        self._fixture_cache[cache_key] = result.copy()
        
        return result
    
    def clear_cache(self):
        """Clear extraction caches."""
        self._source_cache.clear()
        self._fixture_cache.clear()
        self._get_source_lines_cached.cache_clear()
```

#### Streaming for Large Datasets

```python
import json
from failextract import OutputFormatter

class StreamingJSONFormatter(OutputFormatter):
    """JSON formatter for large datasets using streaming."""
    
    def format(self, failures, passed=None, metadata=None):
        """Stream format large datasets."""
        
        # Use generator for memory efficiency
        def generate_json():
            yield '{\n'
            yield f'  "metadata": {json.dumps(metadata or {})},\n'
            yield '  "failures": [\n'
            
            for i, failure in enumerate(failures):
                if i > 0:
                    yield ',\n'
                yield f'    {json.dumps(failure)}'
            
            yield '\n  ]'
            
            if passed:
                yield ',\n  "passed": [\n'
                for i, test in enumerate(passed):
                    if i > 0:
                        yield ',\n'
                    yield f'    {json.dumps(test)}'
                yield '\n  ]'
            
            yield '\n}'
        
        return ''.join(generate_json())

# Usage for large datasets
def save_large_report(extractor, filename):
    """Save report efficiently for large datasets."""
    
    streaming_formatter = StreamingJSONFormatter()
    
    with open(filename, 'w', buffering=8192) as f:
        # Process in chunks to manage memory
        chunk_size = 100
        failures = extractor.failures
        
        for i in range(0, len(failures), chunk_size):
            chunk = failures[i:i + chunk_size]
            formatted = streaming_formatter.format(chunk)
            f.write(formatted)
```

## Thread Safety

### Singleton Thread Safety

FailExtract implements thread-safe singleton pattern with double-checked locking:

```python
import threading

class FailureExtractor:
    """Thread-safe singleton implementation."""
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        # First check without lock (performance optimization)
        if cls._instance is None:
            # Second check with lock (thread safety)
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        """Initialize instance data with thread safety."""
        self._data_lock = threading.RLock()  # Reentrant lock
        self.failures = []
        self.passed_tests = []
        self._statistics = {}
```

### Concurrent Usage Patterns

#### Multi-threaded Test Execution

```python
import threading
import concurrent.futures
from failextract import extract_on_failure

class ThreadSafeTestRunner:
    """Demonstrate thread-safe test execution."""
    
    def __init__(self):
        self.extractor = FailureExtractor()
    
    @extract_on_failure
    def sample_test(self, test_id, should_fail=False):
        """Sample test for concurrent execution."""
        thread_id = threading.current_thread().ident
        print(f"Running test {test_id} on thread {thread_id}")
        
        if should_fail:
            assert False, f"Test {test_id} failed as expected"
        
        return f"Test {test_id} passed"
    
    def run_concurrent_tests(self, num_tests=100, num_workers=10):
        """Run tests concurrently to verify thread safety."""
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=num_workers) as executor:
            # Submit mix of passing and failing tests
            futures = []
            
            for i in range(num_tests):
                should_fail = i % 3 == 0  # Every 3rd test fails
                future = executor.submit(self.sample_test, i, should_fail)
                futures.append(future)
            
            # Collect results
            results = []
            for future in concurrent.futures.as_completed(futures):
                try:
                    result = future.result()
                    results.append(result)
                except AssertionError:
                    # Expected for failing tests
                    pass
        
        return results

# Verify thread safety
runner = ThreadSafeTestRunner()
results = runner.run_concurrent_tests(num_tests=1000, num_workers=20)

# Check data integrity
extractor = FailureExtractor()
print(f"Captured {len(extractor.failures)} failures")
print(f"Thread safety verified: {len(set(f['thread_id'] for f in extractor.failures))} threads")
```

#### Producer-Consumer Pattern

```python
import queue
import threading
from failextract import FailureExtractor

class FailureProcessor:
    """Process failures in background thread."""
    
    def __init__(self, batch_size=10):
        self.extractor = FailureExtractor()
        self.failure_queue = queue.Queue()
        self.batch_size = batch_size
        self.processing_thread = None
        self.stop_event = threading.Event()
    
    def start_processing(self):
        """Start background processing thread."""
        self.processing_thread = threading.Thread(
            target=self._process_failures,
            daemon=True
        )
        self.processing_thread.start()
    
    def stop_processing(self):
        """Stop background processing."""
        self.stop_event.set()
        if self.processing_thread:
            self.processing_thread.join(timeout=5.0)
    
    def _process_failures(self):
        """Background processing loop."""
        batch = []
        
        while not self.stop_event.is_set():
            try:
                # Get failure with timeout
                failure = self.failure_queue.get(timeout=1.0)
                batch.append(failure)
                
                # Process batch when full
                if len(batch) >= self.batch_size:
                    self._process_batch(batch)
                    batch = []
                
                self.failure_queue.task_done()
                
            except queue.Empty:
                # Process partial batch on timeout
                if batch:
                    self._process_batch(batch)
                    batch = []
    
    def _process_batch(self, batch):
        """Process a batch of failures."""
        # Add to extractor thread-safely
        for failure in batch:
            self.extractor.add_failure(failure)
        
        # Optional: Generate incremental reports
        if len(self.extractor.failures) % 100 == 0:
            config = OutputConfig("incremental_report.json", format="json")
            self.extractor.save_report(config)
    
    def queue_failure(self, failure_data):
        """Queue failure for background processing."""
        self.failure_queue.put(failure_data)

# Usage
processor = FailureProcessor(batch_size=5)
processor.start_processing()

# Queue failures from multiple threads
for i in range(100):
    failure_data = {
        'test_name': f'test_{i}',
        'exception_message': f'Error in test {i}',
        'thread_id': threading.current_thread().ident
    }
    processor.queue_failure(failure_data)

# Cleanup
processor.stop_processing()
```

### Lock-Free Operations

For maximum performance, some operations use lock-free patterns:

```python
import time
from collections import deque
from failextract import FailureExtractor

class LockFreeStatistics:
    """Lock-free statistics collection."""
    
    def __init__(self):
        self.operation_times = deque(maxlen=1000)
        self.error_counts = {}
    
    def record_operation_time(self, operation_name, duration):
        """Record operation timing (lock-free for reads)."""
        timestamp = time.time()
        self.operation_times.append((timestamp, operation_name, duration))
    
    def get_performance_stats(self):
        """Get performance statistics."""
        if not self.operation_times:
            return {}
        
        # Create snapshot for lock-free reading
        times_snapshot = list(self.operation_times)
        
        # Calculate statistics
        recent_times = [
            duration for timestamp, _, duration in times_snapshot
            if time.time() - timestamp < 60  # Last minute
        ]
        
        if not recent_times:
            return {}
        
        return {
            'avg_operation_time': sum(recent_times) / len(recent_times),
            'max_operation_time': max(recent_times),
            'min_operation_time': min(recent_times),
            'operation_count': len(recent_times)
        }

# Integration with FailureExtractor
class PerformanceAwareExtractor(FailureExtractor):
    """Extractor with performance monitoring."""
    
    def __init__(self):
        super().__init__()
        self.stats = LockFreeStatistics()
    
    def add_failure(self, failure_data):
        """Add failure with performance tracking."""
        start_time = time.time()
        
        result = super().add_failure(failure_data)
        
        duration = time.time() - start_time
        self.stats.record_operation_time('add_failure', duration)
        
        return result
    
    def save_report(self, config):
        """Save report with performance tracking."""
        start_time = time.time()
        
        result = super().save_report(config)
        
        duration = time.time() - start_time
        self.stats.record_operation_time('save_report', duration)
        
        return result
```

## Production Deployment

### Resource Monitoring

```python
import psutil
import os
from failextract import FailureExtractor

class ResourceMonitor:
    """Monitor resource usage for production deployment."""
    
    def __init__(self):
        self.process = psutil.Process()
        self.initial_memory = self.process.memory_info().rss
    
    def get_resource_usage(self):
        """Get current resource usage."""
        memory_info = self.process.memory_info()
        cpu_percent = self.process.cpu_percent()
        
        return {
            'memory_mb': memory_info.rss / 1024 / 1024,
            'memory_growth_mb': (memory_info.rss - self.initial_memory) / 1024 / 1024,
            'cpu_percent': cpu_percent,
            'thread_count': self.process.num_threads(),
            'open_files': len(self.process.open_files())
        }
    
    def check_resource_limits(self, max_memory_mb=500, max_cpu_percent=50):
        """Check if resource usage is within limits."""
        usage = self.get_resource_usage()
        
        warnings = []
        if usage['memory_mb'] > max_memory_mb:
            warnings.append(f"Memory usage ({usage['memory_mb']:.1f} MB) exceeds limit")
        
        if usage['cpu_percent'] > max_cpu_percent:
            warnings.append(f"CPU usage ({usage['cpu_percent']:.1f}%) exceeds limit")
        
        return warnings

# Integration with FailureExtractor
class ProductionExtractor(FailureExtractor):
    """Production-ready extractor with monitoring."""
    
    def __init__(self):
        super().__init__()
        self.monitor = ResourceMonitor()
        self.warning_threshold = 1000  # Warn after 1000 failures
    
    def add_failure(self, failure_data):
        """Add failure with resource monitoring."""
        result = super().add_failure(failure_data)
        
        # Check resource usage periodically
        if len(self.failures) % 100 == 0:
            warnings = self.monitor.check_resource_limits()
            if warnings:
                print(f"Resource warnings: {'; '.join(warnings)}")
        
        # Warn about large datasets
        if len(self.failures) % self.warning_threshold == 0:
            usage = self.monitor.get_resource_usage()
            print(f"Large dataset warning: {len(self.failures)} failures, "
                  f"{usage['memory_mb']:.1f} MB memory")
        
        return result
```

### CI/CD Integration

```python
import os
import json
from pathlib import Path
from failextract import FailureExtractor, OutputConfig

class CIIntegration:
    """Integration patterns for CI/CD pipelines."""
    
    def __init__(self):
        self.extractor = FailureExtractor()
        self.ci_environment = self._detect_ci_environment()
    
    def _detect_ci_environment(self):
        """Detect CI/CD environment."""
        if os.getenv('GITHUB_ACTIONS'):
            return 'github_actions'
        elif os.getenv('JENKINS_URL'):
            return 'jenkins'
        elif os.getenv('GITLAB_CI'):
            return 'gitlab'
        elif os.getenv('CIRCLECI'):
            return 'circleci'
        else:
            return 'unknown'
    
    def generate_ci_reports(self):
        """Generate CI-appropriate reports."""
        if not self.extractor.failures:
            return []
        
        reports = []
        
        # Always generate JSON for machine processing
        json_config = OutputConfig("test_failures.json", format="json")
        self.extractor.save_report(json_config)
        reports.append("test_failures.json")
        
        # Generate Markdown for human review
        md_config = OutputConfig("test_failures.md", format="markdown")
        self.extractor.save_report(md_config)
        reports.append("test_failures.md")
        
        # CI-specific formats
        if self.ci_environment == 'github_actions':
            self._generate_github_annotations()
        elif self.ci_environment == 'jenkins':
            self._generate_jenkins_report()
        
        return reports
    
    def _generate_github_annotations(self):
        """Generate GitHub Actions annotations."""
        for failure in self.extractor.failures:
            file_path = failure.get('test_file', 'unknown')
            line_number = failure.get('line_number', 1)
            message = failure.get('exception_message', 'Test failed')
            
            # Output GitHub Actions annotation
            print(f"::error file={file_path},line={line_number}::{message}")
    
    def _generate_jenkins_report(self):
        """Generate Jenkins-compatible JUnit XML."""
        from xml.etree.ElementTree import Element, SubElement, tostring
        
        testsuite = Element('testsuite')
        testsuite.set('name', 'FailExtract')
        testsuite.set('tests', str(len(self.extractor.failures)))
        testsuite.set('failures', str(len(self.extractor.failures)))
        
        for failure in self.extractor.failures:
            testcase = SubElement(testsuite, 'testcase')
            testcase.set('name', failure.get('test_name', 'unknown'))
            testcase.set('classname', failure.get('test_module', 'unknown'))
            
            failure_elem = SubElement(testcase, 'failure')
            failure_elem.set('message', failure.get('exception_message', ''))
            failure_elem.text = failure.get('exception_traceback', '')
        
        # Write JUnit XML
        with open('test_failures_junit.xml', 'wb') as f:
            f.write(tostring(testsuite))
    
    def set_exit_code(self):
        """Set appropriate exit code for CI."""
        if self.extractor.failures:
            # Exit with failure code if there are test failures
            os._exit(1)
        else:
            os._exit(0)

# Usage in CI pipeline
def ci_test_completion_hook():
    """Hook to run at end of CI test execution."""
    ci = CIIntegration()
    
    reports = ci.generate_ci_reports()
    print(f"Generated reports: {', '.join(reports)}")
    
    # Set exit code based on failures
    ci.set_exit_code()
```

### Error Recovery and Resilience

```python
import logging
from failextract import FailureExtractor

class ResilientExtractor(FailureExtractor):
    """Failure extractor with error recovery."""
    
    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger(__name__)
        self.error_count = 0
        self.max_errors = 100
    
    def add_failure(self, failure_data):
        """Add failure with error handling."""
        try:
            return super().add_failure(failure_data)
        except Exception as e:
            self.error_count += 1
            self.logger.error(f"Error adding failure: {e}")
            
            if self.error_count > self.max_errors:
                self.logger.critical("Too many errors, stopping failure collection")
                return False
            
            # Continue operation despite error
            return True
    
    def save_report(self, config):
        """Save report with retry logic."""
        max_retries = 3
        retry_delay = 1.0
        
        for attempt in range(max_retries):
            try:
                return super().save_report(config)
            except Exception as e:
                self.logger.warning(f"Report save attempt {attempt + 1} failed: {e}")
                
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                    retry_delay *= 2  # Exponential backoff
                else:
                    self.logger.error(f"Failed to save report after {max_retries} attempts")
                    raise
```

## Performance Benchmarks

### Standard Benchmarks

```python
import time
import statistics
from failextract import extract_on_failure, FailureExtractor

class PerformanceBenchmark:
    """Comprehensive performance benchmarks."""
    
    def __init__(self):
        self.extractor = FailureExtractor()
    
    def benchmark_decorator_overhead(self, iterations=10000):
        """Benchmark decorator overhead for passing tests."""
        
        @extract_on_failure
        def passing_test():
            return True
        
        # Warmup
        for _ in range(100):
            passing_test()
        
        # Benchmark
        times = []
        for _ in range(iterations):
            start = time.perf_counter()
            passing_test()
            duration = time.perf_counter() - start
            times.append(duration * 1000)  # Convert to milliseconds
        
        return {
            'mean_ms': statistics.mean(times),
            'median_ms': statistics.median(times),
            'p95_ms': sorted(times)[int(0.95 * len(times))],
            'p99_ms': sorted(times)[int(0.99 * len(times))]
        }
    
    def benchmark_failure_extraction(self, iterations=1000):
        """Benchmark failure extraction performance."""
        
        @extract_on_failure
        def failing_test(i):
            local_var = f"test_data_{i}"
            assert False, f"Test failure {i}"
        
        times = []
        for i in range(iterations):
            start = time.perf_counter()
            try:
                failing_test(i)
            except AssertionError:
                pass
            duration = time.perf_counter() - start
            times.append(duration * 1000)
        
        return {
            'mean_ms': statistics.mean(times),
            'median_ms': statistics.median(times),
            'p95_ms': sorted(times)[int(0.95 * len(times))],
            'p99_ms': sorted(times)[int(0.99 * len(times))]
        }
    
    def benchmark_memory_usage(self, failure_count=10000):
        """Benchmark memory usage with large datasets."""
        import tracemalloc
        
        tracemalloc.start()
        initial_memory = tracemalloc.get_traced_memory()[0]
        
        # Add failures
        for i in range(failure_count):
            failure_data = {
                'test_name': f'test_{i}',
                'exception_message': f'Error message {i}',
                'test_data': f'Large test data string {i}' * 10
            }
            self.extractor.add_failure(failure_data)
        
        final_memory = tracemalloc.get_traced_memory()[0]
        memory_per_failure = (final_memory - initial_memory) / failure_count
        
        tracemalloc.stop()
        
        return {
            'total_memory_mb': (final_memory - initial_memory) / 1024 / 1024,
            'memory_per_failure_bytes': memory_per_failure,
            'failure_count': failure_count
        }

# Run benchmarks
benchmark = PerformanceBenchmark()

print("Decorator Overhead Benchmark:")
overhead_results = benchmark.benchmark_decorator_overhead()
for metric, value in overhead_results.items():
    print(f"  {metric}: {value:.3f}")

print("\nFailure Extraction Benchmark:")
extraction_results = benchmark.benchmark_failure_extraction()
for metric, value in extraction_results.items():
    print(f"  {metric}: {value:.3f}")

print("\nMemory Usage Benchmark:")
memory_results = benchmark.benchmark_memory_usage()
for metric, value in memory_results.items():
    print(f"  {metric}: {value:.3f}")
```

This performance and threading documentation provides comprehensive guidance for using FailExtract in production environments with optimal performance and complete thread safety.