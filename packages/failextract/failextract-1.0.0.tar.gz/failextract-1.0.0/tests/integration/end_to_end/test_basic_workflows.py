"""Basic end-to-end workflow tests for failextract."""

import json
from unittest.mock import patch

from failextract import (
    FailureExtractor,
    OutputConfig,
    OutputFormat,
    extract_on_failure,
    generate_session_report,
)


class TestBasicWorkflows:
    """Test basic end-to-end workflows and common scenarios."""

    def test_complete_test_suite_extraction(self, temp_directory):
        """Test extraction from a complete test suite with multiple test types."""
        extractor = FailureExtractor()
        extractor.clear()

        # Create a mock test suite with different types of tests

        # Simple failing test
        @extract_on_failure
        def test_simple_failure():
            """Simple test that fails."""
            assert 1 == 2, "Basic arithmetic failure"

        # Test with fixtures
        @extract_on_failure
        def test_with_builtin_fixtures(tmp_path, request):
            """Test using builtin pytest fixtures."""
            test_file = tmp_path / "test.txt"
            test_file.write_text("content")
            assert test_file.read_text() == "wrong_content"

        # Test with custom logic
        @extract_on_failure
        def test_custom_logic():
            """Test with custom business logic."""
            data = {"users": [{"name": "Alice", "age": 30}]}
            user = data["users"][0]
            assert user["age"] == 25, f"Expected age 25, got {user['age']}"

        # Class-based test
        class TestClassExample:
            @extract_on_failure
            def test_method_failure(self):
                """Test method in a class."""
                self.helper_method()

            def helper_method(self):
                """Helper method that will fail."""
                raise ValueError("Helper method failed")

        # Execute all tests and capture failures
        test_functions = [
            test_simple_failure,
            test_with_builtin_fixtures,
            test_custom_logic,
        ]

        test_instance = TestClassExample()

        for test_func in test_functions:
            try:
                if test_func == test_with_builtin_fixtures:
                    # Mock fixtures for this test
                    with patch("pathlib.Path") as mock_path:
                        mock_file = mock_path.return_value
                        mock_file.__truediv__.return_value = mock_file
                        mock_file.write_text.return_value = None
                        mock_file.read_text.return_value = "content"
                        test_func()
                else:
                    test_func()
            except Exception:
                pass  # Expected failures

        # Execute class-based test
        try:
            test_instance.test_method_failure()
        except Exception:
            pass  # Expected failure

        # Verify all failures were captured
        assert len(extractor.failures) >= 3

        # Verify different types of failures were captured
        test_names = {f["test_name"] for f in extractor.failures}
        assert "test_simple_failure" in test_names
        assert "test_custom_logic" in test_names

        # Verify failure details
        simple_failure = next(
            f for f in extractor.failures if f["test_name"] == "test_simple_failure"
        )
        assert "Basic arithmetic failure" in simple_failure["exception_message"]

        custom_failure = next(
            f for f in extractor.failures if f["test_name"] == "test_custom_logic"
        )
        assert "Expected age 25, got 30" in custom_failure["exception_message"]

    def test_multi_format_report_generation(self, temp_directory):
        """Test generation of reports in multiple formats."""
        extractor = FailureExtractor()
        extractor.clear()

        # Add sample failure data
        failure_data = {
            "timestamp": "2024-01-01T12:00:00",
            "test_name": "test_multi_format",
            "test_module": "test_module",
            "test_file": "/path/to/test.py",
            "test_source": 'def test_multi_format():\n    assert False, "Multi-format test"',
            "test_args": "()",
            "test_kwargs": "{}",
            "exception_type": "AssertionError",
            "exception_message": "Multi-format test",
            "exception_traceback": "Traceback...",
            "extracted_code": [
                {
                    "file": "/path/to/module.py",
                    "function": "failing_function",
                    "line": 42,
                    "source": "def failing_function():\n    assert False",
                }
            ],
            "fixtures": [
                {
                    "name": "tmp_path",
                    "type": "builtin",
                    "description": "Temporary directory",
                }
            ],
        }

        extractor.add_failure(failure_data)

        # Generate reports in all supported formats
        formats_to_test = [
            (OutputFormat.JSON, ".json"),
            (OutputFormat.MARKDOWN, ".md"),
            # HTML format has been removed from the codebase
            # (OutputFormat.HTML, ".html"),
            (OutputFormat.XML, ".xml"),
            (OutputFormat.CSV, ".csv"),
            (OutputFormat.YAML, ".yaml"),
        ]

        generated_files = []

        for output_format, extension in formats_to_test:
            output_file = temp_directory / f"report{extension}"
            config = OutputConfig(str(output_file), output_format)

            try:
                extractor.save_report(config)
                generated_files.append((output_file, output_format))
            except ImportError as e:
                if "PyYAML" in str(e) and output_format == OutputFormat.YAML:
                    # Skip YAML test if PyYAML not available
                    continue
                raise

        # Verify all files were generated and contain expected content
        for output_file, output_format in generated_files:
            assert output_file.exists(), f"Report file not created for {output_format}"
            assert output_file.stat().st_size > 0, (
                f"Report file is empty for {output_format}"
            )

            content = output_file.read_text()

            # Each format should contain the test name
            assert "test_multi_format" in content

            # Format-specific checks
            if output_format == OutputFormat.JSON:
                # Should be valid JSON
                data = json.loads(content)
                assert len(data) == 1
                assert data[0]["test_name"] == "test_multi_format"

            elif output_format == OutputFormat.MARKDOWN:
                assert "# Test Failure Report" in content
                assert "## Failure 1:" in content

            # HTML format has been removed from the codebase
            # elif output_format == OutputFormat.HTML:
            #     assert "<!DOCTYPE html>" in content
            #     assert "FailExtract" in content and "Test Failure" in content  # Enhanced title

            elif output_format == OutputFormat.XML:
                assert '<?xml version="1.0"' in content
                assert "<testFailureReport>" in content

            elif output_format == OutputFormat.CSV:
                lines = content.strip().split("\n")
                assert len(lines) >= 2  # Header + data
                assert "Test Name" in lines[0]

    def test_session_level_reporting_workflow(self, temp_directory):
        """Test complete session-level reporting workflow."""
        extractor = FailureExtractor()
        extractor.clear()

        # Simulate a test session with multiple test files

        # Test file 1: Database tests
        @extract_on_failure
        def test_database_connection():
            """Test database connection."""
            raise ConnectionError("Could not connect to database")

        @extract_on_failure
        def test_database_query():
            """Test database query."""
            raise ValueError("Invalid SQL query")

        # Test file 2: API tests
        @extract_on_failure
        def test_api_endpoint():
            """Test API endpoint response."""
            response = {"status": "error", "code": 500}
            assert response["status"] == "success"

        @extract_on_failure
        def test_api_authentication():
            """Test API authentication."""
            token = None
            assert token is not None, "Authentication token is required"

        # Test file 3: Integration tests
        @extract_on_failure
        def test_end_to_end_workflow():
            """Test complete workflow."""
            steps_completed = 3
            total_steps = 5
            assert steps_completed == total_steps, (
                f"Only {steps_completed}/{total_steps} steps completed"
            )

        # Execute all tests
        test_functions = [
            test_database_connection,
            test_database_query,
            test_api_endpoint,
            test_api_authentication,
            test_end_to_end_workflow,
        ]

        for test_func in test_functions:
            try:
                test_func()
            except Exception:
                pass  # Expected failures

        # Add some passed tests to the session
        extractor.add_passed(
            {
                "test_name": "test_successful_unit_test",
                "timestamp": "2024-01-01T12:00:00",
                "status": "passed",
            }
        )

        extractor.add_passed(
            {
                "test_name": "test_successful_integration",
                "timestamp": "2024-01-01T12:01:00",
                "status": "passed",
            }
        )

        # Generate comprehensive session report
        session_report = temp_directory / "session_report.md"
        generate_session_report(str(session_report), "markdown", clear=False)

        assert session_report.exists()
        content = session_report.read_text()

        # Verify report contains all failures
        assert "test_database_connection" in content
        assert "test_api_endpoint" in content
        assert "test_end_to_end_workflow" in content

        # Verify statistics
        assert "Total Failures: 5" in content

        # Also generate JSON summary for programmatic access
        json_summary = temp_directory / "session_summary.json"
        generate_session_report(str(json_summary), "json", clear=False)

        with open(json_summary, "r") as f:
            summary_data = json.load(f)

        assert len(summary_data) == 5

        # Verify we still have passed tests (clear=False)
        stats = extractor.get_stats()
        assert stats["passed_count"] == 2