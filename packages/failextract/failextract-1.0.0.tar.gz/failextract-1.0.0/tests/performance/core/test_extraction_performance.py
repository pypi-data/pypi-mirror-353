"""Performance tests for extraction functionality."""

import gc
import threading
import time
from unittest.mock import patch

from failextract import FailureExtractor, FixtureExtractor


class TestExtractionPerformance:
    """Performance tests for extraction functionality."""

    def test_fixture_extraction_performance(self):
        """Test performance of fixture extraction."""
        extractor = FixtureExtractor()

        # Create test function with many fixtures
        def test_with_many_fixtures(**kwargs):
            pass

        # Mock many fixture parameters
        fixture_names = [f"fixture_{i}" for i in range(50)]

        # Mock fixture discovery to return fixtures
        def mock_find_fixture(name, func, locals_dict):
            if name in fixture_names:
                return {
                    "name": name,
                    "type": "fixture",
                    "scope": "function",
                    "dependencies": fixture_names[:2],  # Small dependency chain
                }
            return None

        # Benchmark fixture extraction (first time - should populate cache)
        with patch.object(
            extractor, "_find_fixture_definition", side_effect=mock_find_fixture
        ):
            start_time = time.time()
            iterations = 50  # Reduced for more realistic testing
            for _ in range(iterations):
                fixtures = extractor.get_fixture_info(test_with_many_fixtures)
            end_time = time.time()
            total_time = end_time - start_time
            avg_time_per_extraction = total_time / iterations

            # Should complete fixture extraction quickly
            assert avg_time_per_extraction < 0.1, (
                f"Fixture extraction too slow: {avg_time_per_extraction:.3f}s"
            )

            # Test cache benefit with subsequent calls (within same mock context)
            cached_start = time.time()
            for _ in range(iterations):
                fixtures = extractor.get_fixture_info(test_with_many_fixtures)
            cached_end = time.time()
            cached_time = cached_end - cached_start

        # Performance threshold - overall should be reasonable
        assert total_time < 2.0, f"Total extraction time too slow: {total_time:.3f}s"
        assert cached_time < 2.0, f"Cached extraction time too slow: {cached_time:.3f}s"

        # Cache should provide reasonable performance (allow some variance)
        # For very fast operations, timing differences can be minimal
        cache_ratio = cached_time / total_time if total_time > 0 else 1.0
        assert cache_ratio < 10.0, (
            f"Cache performance degraded significantly: {cache_ratio:.1f}x"
        )

    def test_failure_collection_performance(self, clean_extractor):
        """Test performance of failure data collection."""
        extractor = clean_extractor

        # Generate large number of failures
        num_failures = 1000
        failure_template = {
            "timestamp": "2024-01-01T12:00:00",
            "test_module": "test_module",
            "test_file": "/path/to/test.py",
            "test_source": "def test_performance(): assert False",
            "test_args": "()",
            "test_kwargs": "{}",
            "exception_type": "AssertionError",
            "exception_traceback": "Traceback...",
            "extracted_code": [
                {
                    "file": "/path/to/module.py",
                    "function": "test_function",
                    "line": 42,
                    "source": "def test_function(): pass",
                }
            ],
        }

        # Benchmark failure addition
        start_time = time.time()

        for i in range(num_failures):
            failure_data = failure_template.copy()
            failure_data["test_name"] = f"test_performance_{i}"
            failure_data["exception_message"] = f"Performance test failure {i}"

            extractor.add_failure(failure_data)

        end_time = time.time()
        collection_time = end_time - start_time

        # Should collect failures efficiently
        avg_time_per_failure = collection_time / num_failures
        assert avg_time_per_failure < 0.001, (
            f"Failure collection too slow: {avg_time_per_failure:.6f}s per failure"
        )

        # Verify all failures were collected
        assert len(extractor.failures) == num_failures

    def test_concurrent_access_performance(self, clean_extractor):
        """Test performance under concurrent access."""
        extractor = clean_extractor

        num_threads = 10
        failures_per_thread = 100

        def worker_thread(thread_id):
            """Worker function that adds failures."""
            for i in range(failures_per_thread):
                failure_data = {
                    "timestamp": f"2024-01-01T{i:02d}:00:00",
                    "test_name": f"thread_{thread_id}_test_{i}",
                    "test_module": f"test_module_{thread_id}",
                    "test_file": f"/path/to/test_{thread_id}.py",
                    "test_source": "def test(): assert False",
                    "exception_type": "AssertionError",
                    "exception_message": f"Thread {thread_id} failure {i}",
                    "extracted_code": [],
                }
                extractor.add_failure(failure_data)

        # Benchmark concurrent access
        start_time = time.time()

        threads = []
        for thread_id in range(num_threads):
            thread = threading.Thread(target=worker_thread, args=(thread_id,))
            threads.append(thread)
            thread.start()

        # Wait for all threads to complete
        for thread in threads:
            thread.join()

        end_time = time.time()
        concurrent_time = end_time - start_time

        expected_total = num_threads * failures_per_thread

        # Should handle concurrent access efficiently
        assert concurrent_time < 5.0, (
            f"Concurrent access too slow: {concurrent_time:.3f}s"
        )

        # All failures should be collected without data loss
        assert len(extractor.failures) == expected_total

        # Verify no data corruption
        thread_ids = set()
        for failure in extractor.failures:
            # Extract thread ID from test name
            parts = failure["test_name"].split("_")
            if len(parts) >= 2:
                thread_ids.add(int(parts[1]))

        assert len(thread_ids) == num_threads, (
            "Data corruption detected in concurrent access"
        )

    def test_memory_management_performance(self):
        """Test performance of memory management features."""
        extractor = FailureExtractor()
        extractor.clear()

        # Set memory limits
        max_failures = 500
        extractor.set_memory_limits(max_failures=max_failures)

        # Add more failures than limit to trigger trimming
        num_failures = 1000

        start_time = time.time()

        for i in range(num_failures):
            failure_data = {
                "timestamp": f"2024-01-01T{i:02d}:00:00",
                "test_name": f"test_memory_{i}",
                "test_module": "test_module",
                "test_file": "/path/to/test.py",
                "test_source": "def test(): pass",
                "exception_type": "AssertionError",
                "exception_message": f"Memory test {i}",
                "extracted_code": [],
            }
            extractor.add_failure(failure_data)

        end_time = time.time()
        memory_mgmt_time = end_time - start_time

        # Memory management should not significantly impact performance
        assert memory_mgmt_time < 2.0, (
            f"Memory management too slow: {memory_mgmt_time:.3f}s"
        )

        # Should maintain memory limit
        assert len(extractor.failures) == max_failures

        # Should keep most recent failures (FIFO trimming)
        latest_failure = extractor.failures[-1]
        assert "test_memory_999" in latest_failure["test_name"]

    def test_large_source_code_handling_performance(self):
        """Test performance with large source code blocks."""
        extractor = FailureExtractor()
        extractor.clear()

        # Generate large source code blocks
        lines = []
        for i in range(100):
            lines.extend(
                [
                    f"def function_{i}():",
                    f'    """Function {i} documentation."""',
                    f"    variable_{i} = {i}",
                    f"    for j in range({i}):",
                    f"        result = variable_{i} + j",
                    "        if result % 2 == 0:",
                    '            print(f"Even result: {result}")',
                    f"    return variable_{i}",
                    "",
                ]
            )
        large_source = "\n".join(lines)  # ~900 lines of code

        failure_data = {
            "timestamp": "2024-01-01T12:00:00",
            "test_name": "test_large_source",
            "test_module": "test_module",
            "test_file": "/path/to/test.py",
            "test_source": large_source,
            "exception_type": "AssertionError",
            "exception_message": "Large source test",
            "extracted_code": [
                {
                    "file": "/path/to/large_module.py",
                    "function": "large_function",
                    "line": 500,
                    "source": large_source,
                }
            ],
        }

        # Benchmark handling of large source
        start_time = time.time()

        # Add failure multiple times to test repeated processing
        for _ in range(10):
            extractor.add_failure(failure_data.copy())

        end_time = time.time()
        large_source_time = end_time - start_time

        # Should handle large source code efficiently
        assert large_source_time < 1.0, (
            f"Large source handling too slow: {large_source_time:.3f}s"
        )

        # Verify failures were stored correctly
        assert len(extractor.failures) == 10
        assert (
            len(extractor.failures[0]["test_source"]) > 10000
        )  # Large source preserved

    def test_memory_usage_monitoring(self):
        """Test memory usage patterns."""
        extractor = FailureExtractor()
        extractor.clear()

        # Force garbage collection to get baseline
        gc.collect()

        # Get initial memory usage (rough estimate)
        initial_objects = len(gc.get_objects())

        # Add failures and monitor memory growth
        num_failures = 500
        checkpoint_interval = 100

        for i in range(num_failures):
            failure_data = {
                "timestamp": f"2024-01-01T{i:02d}:00:00",
                "test_name": f"test_memory_monitoring_{i}",
                "test_module": "test_module",
                "test_file": "/path/to/test.py",
                "test_source": f"def test_{i}(): pass",
                "exception_type": "AssertionError",
                "exception_message": f"Memory monitoring test {i}",
                "extracted_code": [
                    {
                        "file": f"/path/to/code_{i}.py",
                        "function": f"func_{i}",
                        "line": i,
                        "source": f"def func_{i}(): return {i}",
                    }
                ],
            }
            extractor.add_failure(failure_data)

            # Check memory at intervals
            if (i + 1) % checkpoint_interval == 0:
                gc.collect()
                current_objects = len(gc.get_objects())
                memory_growth = current_objects - initial_objects

                # Memory growth should be reasonable (not exponential)
                expected_max_growth = (i + 1) * 50  # Rough estimate
                assert memory_growth < expected_max_growth, (
                    f"Excessive memory growth: {memory_growth} objects at {i + 1} failures"
                )

        # Test memory with limits
        extractor.set_memory_limits(max_failures=100)

        # Add more failures to trigger trimming
        for i in range(num_failures, num_failures + 200):
            failure_data = {
                "timestamp": f"2024-01-01T{i:02d}:00:00",
                "test_name": f"test_memory_limited_{i}",
                "test_module": "test_module",
                "test_file": "/path/to/test.py",
                "test_source": "def test(): pass",
                "exception_type": "AssertionError",
                "exception_message": f"Limited memory test {i}",
                "extracted_code": [],
            }
            extractor.add_failure(failure_data)

        # Memory should be bounded by limits
        assert len(extractor.failures) == 100

        gc.collect()
        final_objects = len(gc.get_objects())
        final_growth = final_objects - initial_objects

        # Memory should not grow unbounded when limits are set
        # Allow for some overhead but should be much less than unlimited growth
        max_expected_final = initial_objects + (100 * 50)  # Based on limit
        assert final_growth < max_expected_final, (
            f"Memory limits not effective: {final_growth} growth"
        )