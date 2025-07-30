"""Advanced decorator features and edge cases tests for extract_on_failure decorator."""

import json
from unittest.mock import Mock, patch

import pytest

from failextract import FailureExtractor, extract_on_failure


class TestExtractOnFailureDecoratorAdvanced:
    """Advanced features and edge cases tests for extract_on_failure decorator."""

    def test_decorator_frame_inspection(self):
        """Test decorator's frame inspection functionality."""
        extractor = FailureExtractor()
        extractor.clear()

        @extract_on_failure
        def test_with_local_vars():
            local_variable = "test_value"
            test_dict = {"key": "value"}
            raise AssertionError("Frame inspection test")

        with pytest.raises(AssertionError):
            test_with_local_vars()

        # Should have captured failure with frame info
        assert len(extractor.failures) == 1
        failure = extractor.failures[0]
        assert "test_name" in failure
        assert failure["test_name"] == "test_with_local_vars"

    def test_decorator_with_include_locals_true(self):
        """Test decorator with include_locals=True parameter."""
        extractor = FailureExtractor()
        extractor.clear()

        @extract_on_failure(include_locals=True)
        def test_with_locals():
            important_var = "should_be_captured"
            raise ValueError("Locals test")

        with pytest.raises(ValueError):
            test_with_locals()

        # Verify failure was captured
        assert len(extractor.failures) == 1

    def test_decorator_with_extract_classes_true(self):
        """Test decorator with extract_classes=True parameter."""
        extractor = FailureExtractor()
        extractor.clear()

        @extract_on_failure(extract_classes=True)
        def test_with_classes():
            class LocalClass:
                def method(self):
                    pass

            raise RuntimeError("Classes test")

        with pytest.raises(RuntimeError):
            test_with_classes()

        # Verify failure was captured
        assert len(extractor.failures) == 1

    def test_decorator_with_skip_stdlib_false(self):
        """Test decorator with skip_stdlib=False parameter."""
        extractor = FailureExtractor()
        extractor.clear()

        @extract_on_failure(skip_stdlib=False)
        def test_without_skip_stdlib():
            import os

            os.path.join("test", "path")
            raise OSError("Stdlib test")

        with pytest.raises(OSError):
            test_without_skip_stdlib()

        # Verify failure was captured
        assert len(extractor.failures) == 1

    def test_decorator_with_max_depth(self):
        """Test decorator with max_depth parameter."""
        extractor = FailureExtractor()
        extractor.clear()

        @extract_on_failure(max_depth=5)
        def test_with_max_depth():
            def inner_function():
                def deeper_function():
                    raise Exception("Max depth test")

                deeper_function()

            inner_function()

        with pytest.raises(Exception):
            test_with_max_depth()

        # Verify failure was captured
        assert len(extractor.failures) == 1

    def test_decorator_frame_locals_extraction(self):
        """Test the frame locals extraction in decorator."""
        extractor = FailureExtractor()
        extractor.clear()

        @extract_on_failure
        def test_frame_extraction():
            # Create some frame context
            frame_var = "frame_test"
            nested_dict = {"nested": {"key": "value"}}

            # Mock the frame inspection to test the logic
            with patch("inspect.currentframe") as mock_frame:
                mock_frame_obj = Mock()
                mock_frame_obj.f_locals = {
                    "frame_var": frame_var,
                    "nested_dict": nested_dict,
                }
                mock_frame.return_value = mock_frame_obj

                raise TypeError("Frame locals test")

        with pytest.raises(TypeError):
            test_frame_extraction()

        # Verify failure was captured
        assert len(extractor.failures) == 1

    def test_decorator_parameter_combinations(self, temp_directory):
        """Test decorator with various parameter combinations."""
        output_file = temp_directory / "combo_test.json"
        extractor = FailureExtractor()
        extractor.clear()

        @extract_on_failure(
            output=str(output_file),
            include_locals=True,
            extract_classes=True,
            skip_stdlib=False,
            max_depth=10,
        )
        def test_all_parameters():
            local_var = "all params test"

            class TestClass:
                pass

            raise Exception("All parameters test")

        with pytest.raises(Exception):
            test_all_parameters()

        # Should work with all parameters
        assert output_file.exists()
        # When output file is specified, failures go to file not singleton
        assert len(extractor.failures) == 0