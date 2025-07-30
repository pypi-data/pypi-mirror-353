"""Edge case tests for FailureExtractor core functionality."""

import json
import tempfile
import threading
from unittest.mock import Mock

import pytest

from failextract import FailureExtractor, OutputConfig


class TestFailureExtractorEdgeCases:
    """Test edge cases for FailureExtractor core functionality."""

    def test_failure_extractor_edge_cases(self):
        """Test FailureExtractor edge cases."""
        extractor = FailureExtractor()
        extractor.clear()

        # Test save_report with no data and include_passed=False
        config = OutputConfig(include_passed=False)
        # Should return early without creating file
        extractor.save_report(config)

        # Test _append_json with empty file
        with tempfile.NamedTemporaryFile(mode="w+", delete=False) as f:
            # Empty file should be handled
            extractor._append_json(f, [{"test": "data"}])

            f.seek(0)
            data = json.load(f)
            assert len(data) == 1

    def test_memory_management_edge_cases(self):
        """Test memory management edge cases."""
        extractor = FailureExtractor()
        extractor.clear()

        # Test setting limits to exact current size
        extractor.add_failure({"test_name": "test1"})
        extractor.add_failure({"test_name": "test2"})
        extractor.add_failure({"test_name": "test3"})

        # Set limit to current size
        extractor.set_memory_limits(max_failures=3)

        # Add one more to trigger trimming
        extractor.add_failure({"test_name": "test4"})

        assert len(extractor.failures) == 3
        # Should keep most recent
        assert extractor.failures[-1]["test_name"] == "test4"

    def test_threading_edge_cases(self):
        """Test threading edge cases."""
        extractor = FailureExtractor()
        extractor.clear()

        # Test concurrent memory limit changes
        def add_failures():
            for i in range(10):
                extractor.add_failure({"test_name": f"thread_test_{i}"})

        def change_limits():
            extractor.set_memory_limits(max_failures=5)

        thread1 = threading.Thread(target=add_failures)
        thread2 = threading.Thread(target=change_limits)

        thread1.start()
        thread2.start()

        thread1.join()
        thread2.join()

        # Should handle concurrent operations safely
        assert len(extractor.failures) <= 10