"""Unit tests for FailureExtractor class."""

import json
import threading
import time
from pathlib import Path

import pytest

from failextract import FailureExtractor, OutputConfig, OutputFormat


class TestFailureExtractor:
    """Test cases for FailureExtractor singleton."""

    def test_singleton_behavior(self, clean_extractor):
        """Test that FailureExtractor maintains singleton behavior."""
        # Get first instance
        instance1 = FailureExtractor()

        # Get second instance
        instance2 = FailureExtractor()

        # Should be the same object
        assert instance1 is instance2
        assert id(instance1) == id(instance2)

    def test_singleton_initialization(self, clean_extractor):
        """Test singleton initialization attributes."""
        extractor = FailureExtractor()

        assert hasattr(extractor, "failures")
        assert hasattr(extractor, "passed")
        assert hasattr(extractor, "fixture_extractor")
        assert hasattr(extractor, "_data_lock")
        assert hasattr(extractor, "_max_failures")
        assert hasattr(extractor, "_max_passed")

        assert isinstance(extractor.failures, list)
        assert isinstance(extractor.passed, list)
        assert isinstance(extractor._data_lock, type(threading.Lock()))
        assert extractor._max_failures is None
        assert extractor._max_passed is None

    def test_add_failure(self, clean_extractor, sample_failure_data):
        """Test adding failure data."""
        extractor = FailureExtractor()

        # Initially empty
        assert len(extractor.failures) == 0

        # Add failure
        extractor.add_failure(sample_failure_data)

        # Should have one failure
        assert len(extractor.failures) == 1
        assert extractor.failures[0] == sample_failure_data

    def test_add_multiple_failures(self, clean_extractor, multiple_failure_data):
        """Test adding multiple failures."""
        extractor = FailureExtractor()

        for failure in multiple_failure_data:
            extractor.add_failure(failure)

        assert len(extractor.failures) == len(multiple_failure_data)

        # Check all failures are present
        for i, failure in enumerate(multiple_failure_data):
            assert extractor.failures[i] == failure

    def test_add_passed(self, clean_extractor):
        """Test adding passed test data."""
        extractor = FailureExtractor()

        passed_data = {
            "test_name": "test_success",
            "timestamp": "2024-01-01T12:00:00",
            "status": "passed",
        }

        # Initially empty
        assert len(extractor.passed) == 0

        # Add passed test
        extractor.add_passed(passed_data)

        # Should have one passed test
        assert len(extractor.passed) == 1
        assert extractor.passed[0] == passed_data

    def test_memory_limits_failures(self, clean_extractor, multiple_failure_data):
        """Test memory limits for failures."""
        extractor = FailureExtractor()

        # Set limit to 2
        extractor.set_memory_limits(max_failures=2)

        # Add more failures than limit
        for failure in multiple_failure_data:  # 3 failures
            extractor.add_failure(failure)

        # Should only keep the last 2
        assert len(extractor.failures) == 2
        assert extractor.failures[0] == multiple_failure_data[1]  # Second failure
        assert extractor.failures[1] == multiple_failure_data[2]  # Third failure

    def test_memory_limits_passed(self, clean_extractor):
        """Test memory limits for passed tests."""
        extractor = FailureExtractor()

        # Set limit to 2
        extractor.set_memory_limits(max_passed=2)

        # Add more passed tests than limit
        for i in range(3):
            passed_data = {"test_name": f"test_{i}", "status": "passed"}
            extractor.add_passed(passed_data)

        # Should only keep the last 2
        assert len(extractor.passed) == 2
        assert extractor.passed[0]["test_name"] == "test_1"
        assert extractor.passed[1]["test_name"] == "test_2"

    def test_set_memory_limits_validation(self, clean_extractor):
        """Test memory limits validation."""
        extractor = FailureExtractor()

        # Test valid limits
        extractor.set_memory_limits(max_failures=10, max_passed=5)
        assert extractor._max_failures == 10
        assert extractor._max_passed == 5

        # Test invalid limits
        with pytest.raises(ValueError, match="max_failures must be positive"):
            extractor.set_memory_limits(max_failures=0)

        with pytest.raises(ValueError, match="max_passed must be positive"):
            extractor.set_memory_limits(max_passed=-1)

        # Test None limits (unlimited)
        extractor.set_memory_limits(max_failures=None, max_passed=None)
        assert extractor._max_failures is None
        assert extractor._max_passed is None

    def test_get_memory_limits(self, clean_extractor):
        """Test getting memory limits."""
        extractor = FailureExtractor()

        # Default limits
        limits = extractor.get_memory_limits()
        assert limits["max_failures"] is None
        assert limits["max_passed"] is None

        # Set custom limits
        extractor.set_memory_limits(max_failures=100, max_passed=50)
        limits = extractor.get_memory_limits()
        assert limits["max_failures"] == 100
        assert limits["max_passed"] == 50

    def test_get_stats(self, clean_extractor, sample_failure_data):
        """Test getting statistics."""
        extractor = FailureExtractor()

        # Initial stats
        stats = extractor.get_stats()
        assert stats["failures_count"] == 0
        assert stats["passed_count"] == 0
        assert stats["total_count"] == 0
        assert stats["max_failures_limit"] is None
        assert stats["max_passed_limit"] is None
        assert stats["failures_at_limit"] is False
        assert stats["passed_at_limit"] is False

        # Add some data
        extractor.add_failure(sample_failure_data)
        extractor.add_passed({"test_name": "test_pass", "status": "passed"})

        stats = extractor.get_stats()
        assert stats["failures_count"] == 1
        assert stats["passed_count"] == 1
        assert stats["total_count"] == 2

        # Test at limit
        extractor.set_memory_limits(max_failures=1, max_passed=1)
        stats = extractor.get_stats()
        assert stats["failures_at_limit"] is True
        assert stats["passed_at_limit"] is True

    def test_reset(self, clean_extractor, sample_failure_data):
        """Test resetting all data and limits."""
        extractor = FailureExtractor()

        # Add data and set limits
        extractor.add_failure(sample_failure_data)
        extractor.add_passed({"test_name": "test_pass"})
        extractor.set_memory_limits(max_failures=10, max_passed=5)

        # Verify data exists
        assert len(extractor.failures) == 1
        assert len(extractor.passed) == 1
        assert extractor._max_failures == 10
        assert extractor._max_passed == 5

        # Reset
        extractor.reset()

        # Everything should be cleared
        assert len(extractor.failures) == 0
        assert len(extractor.passed) == 0
        assert extractor._max_failures is None
        assert extractor._max_passed is None

    def test_clear(self, clean_extractor, sample_failure_data):
        """Test clearing data but keeping limits."""
        extractor = FailureExtractor()

        # Add data and set limits
        extractor.add_failure(sample_failure_data)
        extractor.add_passed({"test_name": "test_pass"})
        extractor.set_memory_limits(max_failures=10, max_passed=5)

        # Clear data
        extractor.clear()

        # Data should be cleared but limits preserved
        assert len(extractor.failures) == 0
        assert len(extractor.passed) == 0
        assert extractor._max_failures == 10
        assert extractor._max_passed == 5

    def test_thread_safety_concurrent_access(self, clean_extractor):
        """Test thread safety with concurrent access."""
        extractor = FailureExtractor()
        num_threads = 5
        operations_per_thread = 10
        results = []

        def worker_thread(thread_id):
            """Worker function for concurrent testing."""
            thread_results = []
            for i in range(operations_per_thread):
                failure_data = {
                    "test_name": f"thread_{thread_id}_test_{i}",
                    "thread_id": thread_id,
                    "operation": i,
                }
                extractor.add_failure(failure_data)
                thread_results.append(failure_data)
            results.append(thread_results)

        # Start multiple threads
        threads = []
        for thread_id in range(num_threads):
            thread = threading.Thread(target=worker_thread, args=(thread_id,))
            threads.append(thread)
            thread.start()

        # Wait for all threads to complete
        for thread in threads:
            thread.join()

        # Verify all data was added
        expected_total = num_threads * operations_per_thread
        assert len(extractor.failures) == expected_total

        # Verify no data corruption
        all_thread_ids = set()
        for failure in extractor.failures:
            assert "thread_id" in failure
            assert "operation" in failure
            all_thread_ids.add(failure["thread_id"])

        # All threads should have contributed
        assert all_thread_ids == set(range(num_threads))

    def test_thread_safety_with_memory_limits(self, clean_extractor):
        """Test thread safety with memory limits."""
        extractor = FailureExtractor()
        extractor.set_memory_limits(max_failures=10)

        def add_failures():
            for i in range(20):  # More than limit
                failure_data = {"test_name": f"test_{i}", "value": i}
                extractor.add_failure(failure_data)
                time.sleep(0.001)  # Small delay to increase contention

        # Start multiple threads
        threads = []
        for _ in range(3):
            thread = threading.Thread(target=add_failures)
            threads.append(thread)
            thread.start()

        # Wait for completion
        for thread in threads:
            thread.join()

        # Should respect memory limit
        assert len(extractor.failures) == 10

    def test_save_report_json(
        self, clean_extractor, sample_failure_data, temp_output_file
    ):
        """Test saving JSON report."""
        extractor = FailureExtractor()
        extractor.add_failure(sample_failure_data)

        config = OutputConfig(temp_output_file, OutputFormat.JSON)
        extractor.save_report(config)

        # Verify file was created and contains correct data
        assert Path(temp_output_file).exists()

        with open(temp_output_file, "r") as f:
            saved_data = json.load(f)

        assert len(saved_data) == 1
        assert saved_data[0]["test_name"] == sample_failure_data["test_name"]

    def test_save_report_with_passed_tests(
        self, clean_extractor, sample_failure_data, temp_output_file
    ):
        """Test saving report including passed tests."""
        extractor = FailureExtractor()
        extractor.add_failure(sample_failure_data)
        extractor.add_passed({"test_name": "test_pass", "status": "passed"})

        config = OutputConfig(temp_output_file, OutputFormat.JSON, include_passed=True)
        extractor.save_report(config)

        with open(temp_output_file, "r") as f:
            saved_data = json.load(f)

        # Should include both failure and passed test
        assert len(saved_data) == 2
        test_names = {item["test_name"] for item in saved_data}
        assert "test_sample_failure" in test_names
        assert "test_pass" in test_names

    def test_save_report_max_failures_limit(
        self, clean_extractor, multiple_failure_data, temp_output_file
    ):
        """Test saving report with max failures limit."""
        extractor = FailureExtractor()

        for failure in multiple_failure_data:
            extractor.add_failure(failure)

        config = OutputConfig(temp_output_file, OutputFormat.JSON, max_failures=2)
        extractor.save_report(config)

        with open(temp_output_file, "r") as f:
            saved_data = json.load(f)

        # Should only save first 2 failures
        assert len(saved_data) == 2

    def test_save_report_no_data(self, clean_extractor, temp_output_file):
        """Test saving report with no data."""
        extractor = FailureExtractor()

        config = OutputConfig(temp_output_file, OutputFormat.JSON)
        extractor.save_report(config)

        # File should not be created if no data
        assert not Path(temp_output_file).exists()

    def test_prepare_data_failures_only(self, clean_extractor, sample_failure_data):
        """Test data preparation with failures only."""
        extractor = FailureExtractor()
        extractor.add_failure(sample_failure_data)

        config = OutputConfig(include_passed=False)
        data = extractor._prepare_data(config)

        assert len(data) == 1
        assert data[0] == sample_failure_data

    def test_prepare_data_with_passed(self, clean_extractor, sample_failure_data):
        """Test data preparation including passed tests."""
        extractor = FailureExtractor()
        extractor.add_failure(sample_failure_data)
        extractor.add_passed({"test_name": "test_pass"})

        config = OutputConfig(include_passed=True)
        data = extractor._prepare_data(config)

        assert len(data) == 2
        # Passed test should have status added
        passed_test = next(
            item for item in data if item.get("test_name") == "test_pass"
        )
        assert passed_test["status"] == "passed"

    def test_append_json_new_file(
        self, clean_extractor, sample_failure_data, temp_output_file
    ):
        """Test JSON append to new file."""
        extractor = FailureExtractor()

        # Remove file if it exists
        Path(temp_output_file).unlink(missing_ok=True)

        with open(temp_output_file, "w") as f:
            extractor._append_json(f, [sample_failure_data])

        with open(temp_output_file, "r") as f:
            data = json.load(f)

        assert len(data) == 1
        assert data[0] == sample_failure_data

    def test_append_json_existing_array(
        self, clean_extractor, sample_failure_data, temp_output_file
    ):
        """Test JSON append to existing array."""
        extractor = FailureExtractor()

        # Create initial file with array
        initial_data = [{"test_name": "existing_test"}]
        with open(temp_output_file, "w") as f:
            json.dump(initial_data, f)

        # Append new data
        with open(temp_output_file, "r+") as f:
            extractor._append_json(f, [sample_failure_data])

        with open(temp_output_file, "r") as f:
            data = json.load(f)

        assert len(data) == 2
        assert data[0]["test_name"] == "existing_test"
        assert data[1] == sample_failure_data

    def test_append_json_existing_object(
        self, clean_extractor, sample_failure_data, temp_output_file
    ):
        """Test JSON append to existing single object."""
        extractor = FailureExtractor()

        # Create initial file with single object
        initial_data = {"test_name": "existing_test"}
        with open(temp_output_file, "w") as f:
            json.dump(initial_data, f)

        # Append new data
        with open(temp_output_file, "r+") as f:
            extractor._append_json(f, [sample_failure_data])

        with open(temp_output_file, "r") as f:
            data = json.load(f)

        assert len(data) == 2
        assert data[0] == initial_data
        assert data[1] == sample_failure_data

    def test_append_json_corrupted_file(
        self, clean_extractor, sample_failure_data, temp_output_file
    ):
        """Test JSON append with corrupted existing file."""
        extractor = FailureExtractor()

        # Create corrupted JSON file
        with open(temp_output_file, "w") as f:
            f.write('{"invalid": json syntax')

        # Should handle gracefully and create new data
        with open(temp_output_file, "r+") as f:
            extractor._append_json(f, [sample_failure_data])

        with open(temp_output_file, "r") as f:
            data = json.load(f)

        assert len(data) == 1
        assert data[0] == sample_failure_data

    def test_singleton_across_modules(self):
        """Test singleton behavior across different import contexts."""
        # This test ensures the singleton works even with different import patterns

        # Reset singleton
        FailureExtractor._instance = None

        # Get instance through direct class access
        instance1 = FailureExtractor()

        # Import and get instance (simulating different module import)
        from failextract import FailureExtractor as ImportedExtractor

        instance2 = ImportedExtractor()

        assert instance1 is instance2

    def test_memory_trimming_fifo(self, clean_extractor):
        """Test that memory trimming follows FIFO (First In, First Out) order."""
        extractor = FailureExtractor()
        extractor.set_memory_limits(max_failures=3)

        # Add failures in order
        failure_order = []
        for i in range(5):
            failure_data = {"test_name": f"test_{i}", "order": i}
            extractor.add_failure(failure_data)
            failure_order.append(failure_data)

        # Should keep last 3 (most recent)
        assert len(extractor.failures) == 3
        assert extractor.failures[0]["order"] == 2  # test_2
        assert extractor.failures[1]["order"] == 3  # test_3
        assert extractor.failures[2]["order"] == 4  # test_4
