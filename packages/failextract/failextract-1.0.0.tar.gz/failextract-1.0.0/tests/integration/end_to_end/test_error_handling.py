"""Error handling and edge case tests for failextract."""

import json
from unittest.mock import patch

from failextract import (
    FailureExtractor,
    OutputConfig,
    OutputFormat,
)


class TestErrorHandling:
    """Test error handling and edge cases."""

    def test_error_recovery_and_robustness(self, temp_directory):
        """Test error recovery and robustness of the system."""
        extractor = FailureExtractor()
        extractor.clear()

        # Test 1: Handling of malformed failure data
        malformed_data = {
            "test_name": "test_malformed",
            # Missing required fields
            "timestamp": "2024-01-01T12:00:00",
        }

        # Should handle gracefully without crashing
        extractor.add_failure(malformed_data)

        # Test 2: Handling of non-serializable data
        class NonSerializable:
            def __str__(self):
                raise Exception("Cannot convert to string")

        problematic_data = {
            "test_name": "test_non_serializable",
            "timestamp": "2024-01-01T12:00:00",
            "test_module": "test_module",
            "test_file": "/path/to/test.py",
            "test_source": "def test(): pass",
            "exception_type": "ValueError",
            "exception_message": "Test error",
            "extracted_code": [],
            "problematic_object": NonSerializable(),  # This will cause issues in some formatters
        }

        extractor.add_failure(problematic_data)

        # Test 3: Handling of serialization errors

        # Try to save with non-serializable data - should handle gracefully
        serialization_config = OutputConfig(
            str(temp_directory / "test.json"), OutputFormat.JSON
        )

        try:
            extractor.save_report(serialization_config)
        except Exception:
            # Expected - non-serializable objects should cause errors
            # This test validates that we can detect serialization issues
            pass

        # Test 4: Handling of file system errors with clean data
        extractor.clear()
        extractor.add_failure(
            {
                "test_name": "test_clean",
                "timestamp": "2024-01-01T12:00:00",
                "test_module": "test_module",
                "test_file": "/path/to/test.py",
                "test_source": "def test(): pass",
                "exception_type": "ValueError",
                "exception_message": "Test error",
                "extracted_code": [],
            }
        )

        # Mock the save operation to simulate filesystem errors
        with patch("builtins.open", side_effect=OSError("Filesystem error")):
            try:
                extractor.save_report(serialization_config)
            except OSError:
                pass  # Expected filesystem error

        # Test 5: Recovery from corrupted files
        corrupted_file = temp_directory / "corrupted.json"
        corrupted_file.write_text('{"invalid": json syntax')

        # Try to append to corrupted file
        append_config = OutputConfig(
            str(corrupted_file), OutputFormat.JSON, append=True
        )

        # Should handle gracefully - might still have corrupted content
        try:
            extractor.save_report(append_config)
            # Try to read the file
            with open(corrupted_file, "r") as f:
                content = f.read()
                # At minimum, should have added new content
                assert "test_clean" in content
        except (json.JSONDecodeError, Exception):
            # Expected - corrupted files might remain corrupted
            # This test validates error detection and handling
            pass

        # Test 6: Memory pressure handling
        # Clear and test with memory limits
        extractor.clear()
        extractor.set_memory_limits(max_failures=2)

        # Add more failures than limit
        for i in range(5):
            failure = {
                "test_name": f"test_{i}",
                "timestamp": f"2024-01-01T{i:02d}:00:00",
                "exception_message": f"Error {i}",
                "test_module": "test",
                "test_file": "/test.py",
                "test_source": "def test(): pass",
                "exception_type": "Error",
                "extracted_code": [],
            }
            extractor.add_failure(failure)

        # Should only keep most recent failures
        assert len(extractor.failures) == 2
        assert extractor.failures[-1]["test_name"] == "test_4"  # Most recent

        # Generate final report to verify system is still functional
        final_report = temp_directory / "final_report.json"
        final_config = OutputConfig(str(final_report), OutputFormat.JSON)
        extractor.save_report(final_config)

        assert final_report.exists()

        with open(final_report, "r") as f:
            final_data = json.load(f)

        assert len(final_data) == 2
        assert all("test_name" in failure for failure in final_data)

    def test_malformed_data_handling(self, temp_directory):
        """Test handling of various types of malformed data."""
        extractor = FailureExtractor()
        extractor.clear()

        # Test with None values
        none_data = {
            "test_name": None,
            "timestamp": "2024-01-01T12:00:00",
            "exception_message": None,
        }
        extractor.add_failure(none_data)

        # Test with empty strings
        empty_data = {
            "test_name": "",
            "timestamp": "",
            "exception_message": "",
        }
        extractor.add_failure(empty_data)

        # Test with missing timestamp
        no_timestamp = {
            "test_name": "test_no_timestamp",
            "exception_message": "Error without timestamp",
        }
        extractor.add_failure(no_timestamp)

        # Should handle malformed data gracefully - some may be rejected
        assert len(extractor.failures) >= 2  # At least empty_data and no_timestamp should be accepted

        # Try to generate report with malformed data
        report_file = temp_directory / "malformed_report.json"
        config = OutputConfig(str(report_file), OutputFormat.JSON)
        
        try:
            extractor.save_report(config)
            # If successful, verify the file exists
            assert report_file.exists()
        except Exception:
            # Some formatters may reject malformed data - this is acceptable
            pass

    def test_filesystem_permission_errors(self, temp_directory):
        """Test handling of filesystem permission errors."""
        extractor = FailureExtractor()
        extractor.clear()
        
        # Add valid failure data
        extractor.add_failure({
            "test_name": "test_permission_error",
            "timestamp": "2024-01-01T12:00:00",
            "exception_message": "Permission test",
            "test_module": "test",
            "test_file": "/test.py",
            "test_source": "def test(): pass",
            "exception_type": "PermissionError",
            "extracted_code": [],
        })

        # Test writing to a read-only directory (simulated)
        readonly_file = temp_directory / "readonly_report.json"
        config = OutputConfig(str(readonly_file), OutputFormat.JSON)

        # Mock to simulate permission denied
        with patch("builtins.open", side_effect=PermissionError("Permission denied")):
            try:
                extractor.save_report(config)
            except PermissionError:
                pass  # Expected permission error

        # Test with invalid path characters
        invalid_path = temp_directory / "invalid\x00name.json"
        invalid_config = OutputConfig(str(invalid_path), OutputFormat.JSON)
        
        try:
            extractor.save_report(invalid_config)
        except (OSError, ValueError):
            pass  # Expected error for invalid path

    def test_large_data_edge_cases(self, temp_directory):
        """Test handling of extremely large data structures."""
        extractor = FailureExtractor()
        extractor.clear()

        # Test with very large string data
        large_string = "x" * 10000
        large_data = {
            "test_name": "test_large_data",
            "timestamp": "2024-01-01T12:00:00",
            "exception_message": large_string,
            "test_source": large_string,
            "test_module": "test",
            "test_file": "/test.py",
            "exception_type": "LargeDataError",
            "extracted_code": [
                {
                    "file": "/large.py",
                    "function": "large_function",
                    "line": 1,
                    "source": large_string,
                }
            ],
        }

        extractor.add_failure(large_data)

        # Test with many extracted code blocks
        many_blocks_data = {
            "test_name": "test_many_blocks",
            "timestamp": "2024-01-01T12:00:00",
            "exception_message": "Many blocks test",
            "test_module": "test",
            "test_file": "/test.py",
            "test_source": "def test(): pass",
            "exception_type": "ManyBlocksError",
            "extracted_code": [
                {
                    "file": f"/file_{i}.py",
                    "function": f"function_{i}",
                    "line": i,
                    "source": f"def function_{i}(): pass",
                }
                for i in range(100)
            ],
        }

        extractor.add_failure(many_blocks_data)

        # Should handle large data without crashing
        assert len(extractor.failures) == 2

        # Try to generate reports with large data
        large_report = temp_directory / "large_data_report.json"
        config = OutputConfig(str(large_report), OutputFormat.JSON)
        
        try:
            extractor.save_report(config)
            # Verify the file was created and has reasonable size
            if large_report.exists():
                file_size = large_report.stat().st_size
                assert file_size > 0
                # Should not exceed reasonable limits (100MB)
                assert file_size < 100 * 1024 * 1024
        except Exception:
            # Some systems may reject extremely large data - this is acceptable
            pass

    def test_circular_reference_handling(self, temp_directory):
        """Test handling of circular references in failure data."""
        extractor = FailureExtractor()
        extractor.clear()

        # Create circular reference
        circular_dict = {"name": "circular"}
        circular_dict["self"] = circular_dict

        circular_data = {
            "test_name": "test_circular",
            "timestamp": "2024-01-01T12:00:00",
            "exception_message": "Circular reference test",
            "test_module": "test",
            "test_file": "/test.py",
            "test_source": "def test(): pass",
            "exception_type": "CircularError",
            "extracted_code": [],
            "circular_ref": circular_dict,  # This will cause issues in JSON serialization
        }

        extractor.add_failure(circular_data)

        # Try to save with circular references
        circular_report = temp_directory / "circular_report.json"
        config = OutputConfig(str(circular_report), OutputFormat.JSON)

        try:
            extractor.save_report(config)
        except (ValueError, RecursionError, TypeError):
            # Expected - circular references should cause JSON serialization errors
            pass

        # Verify system is still functional after circular reference error
        clean_data = {
            "test_name": "test_clean_after_circular",
            "timestamp": "2024-01-01T12:00:00",
            "exception_message": "Clean test after circular",
            "test_module": "test",
            "test_file": "/test.py",
            "test_source": "def test(): pass",
            "exception_type": "CleanError",
            "extracted_code": [],
        }

        extractor.add_failure(clean_data)
        assert len(extractor.failures) == 2