"""End-to-end performance tests."""

import time

from failextract import FailureExtractor, OutputConfig, OutputFormat, extract_on_failure


class TestEndToEndPerformance:
    """End-to-end performance tests."""

    def test_report_generation_performance(self, temp_directory):
        """Test performance of report generation."""
        extractor = FailureExtractor()
        extractor.clear()

        # Generate substantial failure dataset
        num_failures = 100
        for i in range(num_failures):
            failure_data = {
                "timestamp": f"2024-01-01T{i:02d}:00:00",
                "test_name": f"test_report_perf_{i}",
                "test_module": f"test_module_{i % 10}",
                "test_file": f"/path/to/test_{i}.py",
                "test_source": f'def test_report_perf_{i}():\n    # Test function {i}\n    assert False, "Performance test"',
                "test_args": f'({i}, "arg_{i}")',
                "test_kwargs": f'{{"param_{i}": {i}}}',
                "exception_type": "AssertionError",
                "exception_message": f"Performance test failure {i} with detailed message explaining the error",
                "exception_traceback": f'Traceback (most recent call last):\n  File "/test_{i}.py", line {i + 1}, in test\n    assert False\nAssertionError: Performance test',
                "extracted_code": [
                    {
                        "file": f"/path/to/code_{i}.py",
                        "function": f"function_{i}",
                        "line": i + 1,
                        "source": f"def function_{i}():\n    # Function {i} implementation\n    return {i}",
                    }
                ],
                "fixtures": [
                    {
                        "name": f"fixture_{i % 5}",
                        "type": "fixture",
                        "scope": "function",
                        "source": f'@pytest.fixture\ndef fixture_{i % 5}():\n    return "value_{i % 5}"',
                    }
                ],
            }
            extractor.add_failure(failure_data)

        # Test performance of different output formats
        formats_to_test = [
            (OutputFormat.JSON, ".json"),
            (OutputFormat.MARKDOWN, ".md"),
            # HTML format has been removed from the codebase
            # (OutputFormat.HTML, ".html"),
            (OutputFormat.XML, ".xml"),
            (OutputFormat.CSV, ".csv"),
        ]

        performance_results = {}

        for output_format, extension in formats_to_test:
            output_file = temp_directory / f"perf_report{extension}"
            config = OutputConfig(str(output_file), output_format)

            # Benchmark report generation
            start_time = time.time()
            extractor.save_report(config)
            end_time = time.time()

            generation_time = end_time - start_time
            performance_results[output_format.value] = generation_time

            # Should generate reports quickly
            assert generation_time < 5.0, (
                f"{output_format.value} report generation too slow: {generation_time:.3f}s"
            )

            # Verify file was created and has reasonable size
            assert output_file.exists()
            file_size = output_file.stat().st_size
            assert file_size > 1000, f"{output_format.value} report too small"
            assert file_size < 50 * 1024 * 1024, (
                f"{output_format.value} report too large: {file_size} bytes"
            )

        # JSON should generally be the fastest format
        json_time = performance_results.get("json", float("inf"))
        for format_name, time_taken in performance_results.items():
            if format_name != "json":
                # Other formats can be slower but not excessively so
                assert time_taken < json_time * 10, (
                    f"{format_name} format {time_taken / json_time:.1f}x slower than JSON"
                )

    def test_decorator_overhead_performance(self):
        """Test performance overhead of the extract_on_failure decorator."""

        # Test function without decorator (more realistic workload)
        def plain_test_function():
            """Plain test function for baseline."""
            # Simulate typical test work
            data = list(range(100))
            result = sum(x * 2 for x in data if x % 2 == 0)
            return result == 9900

        # Test function with decorator
        @extract_on_failure
        def decorated_test_function():
            """Decorated test function."""
            # Same workload as plain function
            data = list(range(100))
            result = sum(x * 2 for x in data if x % 2 == 0)
            return result == 9900

        # Benchmark plain function
        iterations = 1000

        start_time = time.time()
        for _ in range(iterations):
            plain_test_function()
        plain_time = time.time() - start_time

        # Benchmark decorated function (successful cases)
        start_time = time.time()
        for _ in range(iterations):
            decorated_test_function()
        decorated_time = time.time() - start_time

        # Decorator overhead should be minimal for successful tests
        overhead = decorated_time - plain_time
        overhead_per_call = overhead / iterations

        assert overhead_per_call < 0.01, (
            f"Decorator overhead too high: {overhead_per_call:.6f}s per call"
        )

        # Relative overhead should be reasonable for successful tests
        if plain_time > 0:
            relative_overhead = decorated_time / plain_time
            assert relative_overhead < 5.0, (
                f"Decorator adds {relative_overhead:.1f}x overhead"
            )