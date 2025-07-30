"""Performance tests for formatters."""

import time

from failextract import FormatterRegistry, OutputFormat


class TestFormatterPerformance:
    """Performance tests for formatters."""

    def test_formatter_performance_comparison(self, temp_directory):
        """Compare performance of different formatters."""
        # Create test data
        test_failures = []
        for i in range(50):
            failure = {
                "timestamp": f"2024-01-01T{i:02d}:00:00",
                "test_name": f"test_formatter_perf_{i}",
                "test_module": f"module_{i}",
                "test_file": f"/path/test_{i}.py",
                "test_source": f'def test_{i}():\n    assert False, "Test {i}"',
                "exception_type": "AssertionError",
                "exception_message": f"Formatter performance test {i}",
                "extracted_code": [
                    {
                        "file": f"/code_{i}.py",
                        "function": f"func_{i}",
                        "line": i,
                        "source": f"def func_{i}(): return {i}",
                    }
                ],
            }
            test_failures.append(failure)

        # Test each formatter
        formatters = [
            ("JSON", FormatterRegistry.get_formatter("json")),
            ("Markdown", FormatterRegistry.get_formatter("markdown")),
            # HTML format has been removed from the codebase
            # ("HTML", FormatterRegistry.get_formatter("html")),
            ("XML", FormatterRegistry.get_formatter("xml")),
            ("CSV", FormatterRegistry.get_formatter("csv")),
        ]

        performance_data = {}

        for format_name, formatter in formatters:
            # Benchmark formatting
            start_time = time.time()

            # Run multiple iterations for better measurement
            iterations = 10
            for _ in range(iterations):
                result = formatter.format(test_failures)

            end_time = time.time()
            avg_time = (end_time - start_time) / iterations

            performance_data[format_name] = avg_time

            # Each formatter should complete reasonably quickly
            assert avg_time < 1.0, f"{format_name} formatter too slow: {avg_time:.3f}s"

            # Verify output is substantial
            assert len(result) > 1000, f"{format_name} output too small"

        # CSV should generally be fastest (simplest format)
        csv_time = performance_data.get("CSV", float("inf"))

        # HTML and Markdown might be slower due to formatting
        for format_name, time_taken in performance_data.items():
            if format_name not in ["CSV", "JSON"]:
                # Allow some overhead for complex formatting
                assert time_taken < csv_time * 20, (
                    f"{format_name} formatter excessively slow compared to CSV"
                )