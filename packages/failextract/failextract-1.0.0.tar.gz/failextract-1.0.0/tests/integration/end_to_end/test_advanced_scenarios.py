"""Advanced scenario tests for failextract."""

import json
import threading
import time

from failextract import (
    FailureExtractor,
    FormatterRegistry,
    OutputConfig,
    OutputFormat,
    OutputFormatter,
    extract_on_failure,
)


class TestAdvancedScenarios:
    """Test advanced features and complex scenarios."""

    def test_concurrent_test_execution_simulation(self, temp_directory):
        """Test handling of concurrent test execution."""
        extractor = FailureExtractor()
        extractor.clear()

        def simulate_test_worker(worker_id, num_tests):
            """Simulate a worker thread running tests."""
            for test_id in range(num_tests):

                @extract_on_failure
                def worker_test():
                    # Simulate some work
                    time.sleep(0.001)
                    # Fail occasionally
                    if test_id % 3 == 0:
                        raise ValueError(f"Worker {worker_id} test {test_id} failed")
                    return "success"

                try:
                    worker_test()
                except Exception:
                    pass  # Expected failures

        # Start multiple worker threads
        num_workers = 3
        tests_per_worker = 10
        threads = []

        for worker_id in range(num_workers):
            thread = threading.Thread(
                target=simulate_test_worker, args=(worker_id, tests_per_worker)
            )
            threads.append(thread)
            thread.start()

        # Wait for all threads to complete
        for thread in threads:
            thread.join()

        # Verify thread-safe collection of failures
        total_expected_failures = num_workers * (
            tests_per_worker // 3 + (1 if tests_per_worker % 3 != 0 else 0)
        )

        # Should have captured failures from all workers
        assert len(extractor.failures) > 0
        assert len(extractor.failures) <= total_expected_failures

        # Verify no data corruption
        for failure in extractor.failures:
            assert "test_name" in failure
            assert "exception_type" in failure
            assert "Worker" in failure["exception_message"]

        # Generate report from concurrent execution
        concurrent_report = temp_directory / "concurrent_report.json"
        config = OutputConfig(str(concurrent_report), OutputFormat.JSON)
        extractor.save_report(config)

        assert concurrent_report.exists()

        with open(concurrent_report, "r") as f:
            report_data = json.load(f)

        assert len(report_data) == len(extractor.failures)

    def test_large_scale_failure_handling(self, temp_directory):
        """Test handling of large numbers of failures."""
        extractor = FailureExtractor()
        extractor.clear()

        # Set memory limits to test memory management
        extractor.set_memory_limits(max_failures=50, max_passed=20)

        # Generate large number of failures
        num_failures = 100
        num_passed = 40

        for i in range(num_failures):
            failure_data = {
                "timestamp": f"2024-01-01T{i:02d}:00:00",
                "test_name": f"test_failure_{i}",
                "test_module": f"test_module_{i % 10}",
                "test_file": f"/path/to/test_{i}.py",
                "test_source": f'def test_failure_{i}():\n    assert False, "Failure {i}"',
                "exception_type": "AssertionError",
                "exception_message": f"Failure {i}",
                "extracted_code": [
                    {
                        "file": f"/path/to/code_{i}.py",
                        "function": f"function_{i}",
                        "line": i + 1,
                        "source": f"def function_{i}():\n    pass",
                    }
                ],
            }
            extractor.add_failure(failure_data)

        for i in range(num_passed):
            passed_data = {
                "test_name": f"test_passed_{i}",
                "timestamp": f"2024-01-01T{i:02d}:30:00",
                "status": "passed",
            }
            extractor.add_passed(passed_data)

        # Verify memory limits are enforced
        stats = extractor.get_stats()
        assert stats["failures_count"] == 50  # Limited by max_failures
        assert stats["passed_count"] == 20  # Limited by max_passed
        assert stats["failures_at_limit"] is True
        assert stats["passed_at_limit"] is True

        # Verify FIFO behavior - should have most recent failures
        latest_failure = extractor.failures[-1]
        assert "test_failure_99" in latest_failure["test_name"]

        # Generate report with large dataset
        large_report = temp_directory / "large_report.json"
        config = OutputConfig(str(large_report), OutputFormat.JSON, include_passed=True)
        extractor.save_report(config)

        assert large_report.exists()

        with open(large_report, "r") as f:
            report_data = json.load(f)

        # Should include both failures and passed tests
        assert len(report_data) == 70  # 50 failures + 20 passed

        # Verify performance with large dataset
        file_size = large_report.stat().st_size
        assert file_size > 0
        # Large report should still be reasonable size (less than 10MB for this test)
        assert file_size < 10 * 1024 * 1024

    def test_custom_formatter_integration(self, temp_directory):
        """Test integration with custom formatters."""
        # Create custom formatter
        class CustomFormatter(OutputFormatter):
            def format(self, failures):
                """Custom format: simple text summary."""
                lines = ["CUSTOM FAILURE REPORT", "=" * 20, ""]

                for i, failure in enumerate(failures, 1):
                    lines.append(f"{i}. {failure['test_name']}")
                    lines.append(f"   Error: {failure['exception_message']}")
                    lines.append(f"   Time: {failure['timestamp']}")
                    lines.append("")

                return "\n".join(lines)

            def get_extension(self):
                return ".txt"

        # Import the correct FormatterRegistry from the same module as FailureExtractor
        from failextract.failextract import FormatterRegistry as InternalFormatterRegistry
        
        # Register custom formatter with the internal registry
        custom_formatter = CustomFormatter()
        InternalFormatterRegistry.register_formatter(OutputFormat.CUSTOM, custom_formatter)

        # Add test failure
        extractor = FailureExtractor()
        extractor.clear()

        failure_data = {
            "timestamp": "2024-01-01T12:00:00",
            "test_name": "test_custom_format",
            "test_module": "test_module",
            "test_file": "/path/to/test.py",
            "test_source": "def test_custom_format(): pass",
            "exception_type": "ValueError",
            "exception_message": "Custom formatter test error",
            "extracted_code": [],
        }

        extractor.add_failure(failure_data)

        # Generate report with custom formatter
        custom_report = temp_directory / "custom_report.txt"
        config = OutputConfig(str(custom_report), OutputFormat.CUSTOM)
        extractor.save_report(config)

        assert custom_report.exists()
        content = custom_report.read_text()

        # Verify custom format
        assert "CUSTOM FAILURE REPORT" in content
        assert "test_custom_format" in content
        assert "Custom formatter test error" in content
        assert "2024-01-01T12:00:00" in content