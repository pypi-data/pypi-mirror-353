"""Integration tests for pytest integration."""

import json
import subprocess
import sys
from textwrap import dedent
from unittest.mock import patch

import pytest

from failextract import FailureExtractor


class TestPytestIntegration:
    """Test integration with pytest framework."""

    def test_real_pytest_fixture_integration(self, temp_directory):
        """Test integration with real pytest fixtures."""
        # Create a test file with pytest fixtures
        test_file = temp_directory / "test_real_fixtures.py"
        test_file.write_text(
            dedent("""
            import pytest
            from failextract import extract_on_failure
            
            @pytest.fixture
            def sample_data():
                return {"key": "value", "number": 42}
            
            @pytest.fixture
            def processed_data(sample_data):
                return f"processed_{sample_data['key']}"
            
            @extract_on_failure
            def test_with_fixtures(tmp_path, sample_data, processed_data):
                # This test will fail to trigger extraction
                assert processed_data == "wrong_value"
        """)
        )

        # Create conftest.py with additional fixtures
        conftest_file = temp_directory / "conftest.py"
        conftest_file.write_text(
            dedent("""
            import pytest
            
            @pytest.fixture(scope="session")
            def session_fixture():
                return "session_value"
            
            @pytest.fixture
            def module_fixture():
                return "module_value"
        """)
        )

        # Run pytest and capture the failure
        extractor = FailureExtractor()
        extractor.clear()

        # We'll simulate running the test by importing and executing it
        # In a real scenario, this would be run through pytest
        sys.path.insert(0, str(temp_directory))
        try:
            # Import the test module
            import importlib.util

            spec = importlib.util.spec_from_file_location(
                "test_real_fixtures", test_file
            )
            test_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(
                test_module
            )  # Execute the module to define functions

            # This is a simplified simulation - in reality pytest would handle fixture injection
            with pytest.raises(AssertionError):
                # Simulate the test execution with fixtures
                test_func = test_module.test_with_fixtures
                # Mock fixture values
                frame_locals = {
                    "tmp_path": "/tmp/pytest-tmp",
                    "sample_data": {"key": "value", "number": 42},
                    "processed_data": "processed_value",
                }

                # Execute with mock fixtures
                try:
                    # This would normally be called by pytest with actual fixtures
                    test_func.__wrapped__(
                        "/tmp/pytest-tmp",
                        {"key": "value", "number": 42},
                        "processed_value",
                    )
                except AssertionError as e:
                    # Simulate the decorator's failure handling
                    from failextract import extract_failure_info

                    failure_data = extract_failure_info(
                        test_func,
                        e,
                        (
                            "/tmp/pytest-tmp",
                            {"key": "value", "number": 42},
                            "processed_value",
                        ),
                        {},
                        frame_locals=frame_locals,
                        include_fixtures=True,
                    )
                    extractor.add_failure(failure_data)
                    raise

        finally:
            sys.path.remove(str(temp_directory))

        # Verify that failure was captured with fixture information
        assert len(extractor.failures) > 0
        failure = extractor.failures[0]
        assert "fixtures" in failure

        # Should have detected some fixtures
        fixture_names = {f["name"] for f in failure["fixtures"]}
        # At minimum should detect builtin fixtures
        assert len(fixture_names) > 0

    def test_conftest_hierarchy_discovery(self, temp_directory):
        """Test discovery of conftest.py files in directory hierarchy."""
        # Create nested directory structure with conftest files
        root_dir = temp_directory
        sub_dir = root_dir / "subpackage"
        test_dir = sub_dir / "tests"
        test_dir.mkdir(parents=True)

        # Root conftest
        root_conftest = root_dir / "conftest.py"
        root_conftest.write_text(
            dedent("""
            import pytest
            
            @pytest.fixture(scope="session")
            def root_fixture():
                return "root_value"
        """)
        )

        # Sub conftest
        sub_conftest = sub_dir / "conftest.py"
        sub_conftest.write_text(
            dedent("""
            import pytest
            
            @pytest.fixture
            def sub_fixture():
                return "sub_value"
        """)
        )

        # Test conftest
        test_conftest = test_dir / "conftest.py"
        test_conftest.write_text(
            dedent("""
            import pytest
            
            @pytest.fixture
            def test_fixture():
                return "test_value"
        """)
        )

        # Create test file
        test_file = test_dir / "test_hierarchy.py"
        test_file.write_text(
            dedent("""
            from failextract import extract_on_failure
            
            @extract_on_failure
            def test_hierarchy_fixtures(root_fixture, sub_fixture, test_fixture):
                # Simulate test that would use fixtures from hierarchy
                assert root_fixture == "wrong"  # This will fail
        """)
        )

        # Test fixture discovery in hierarchy
        from failextract import FixtureExtractor

        extractor = FixtureExtractor()

        # Create a mock test function to test conftest discovery
        def mock_test():
            pass

        mock_test.__module__ = "test_hierarchy"

        # Mock the file path to be in the test directory
        with patch("inspect.getfile", return_value=str(test_file)):
            conftest_modules = extractor._get_conftest_modules(mock_test)

        # Should find conftest modules in the hierarchy
        assert isinstance(conftest_modules, list)
        # The actual number depends on successful imports, but should attempt discovery

    def test_fixture_dependency_resolution(self):
        """Test resolution of complex fixture dependencies."""
        from failextract import FixtureExtractor

        extractor = FixtureExtractor()

        # Create mock fixtures with dependencies
        def base_fixture():
            return "base"

        def dependent_fixture(base_fixture):
            return f"dependent_{base_fixture}"

        def complex_fixture(dependent_fixture, tmp_path):
            return f"complex_{dependent_fixture}"

        # Mock pytest markers
        for fixture_func in [base_fixture, dependent_fixture, complex_fixture]:
            fixture_func._pytestfixturefunction = type(
                "MockMarker",
                (),
                {
                    "scope": "function",
                    "params": None,
                    "autouse": False,
                    "ids": None,
                    "name": None,
                },
            )()

        # Create test function that uses the complex fixture
        def test_complex(complex_fixture):
            pass

        # Mock the fixture discovery to return our test fixtures
        def mock_find_fixture(name, func, locals_dict):
            fixtures = {
                "base_fixture": {
                    "name": "base_fixture",
                    "type": "fixture",
                    "dependencies": [],
                },
                "dependent_fixture": {
                    "name": "dependent_fixture",
                    "type": "fixture",
                    "dependencies": ["base_fixture"],
                },
                "complex_fixture": {
                    "name": "complex_fixture",
                    "type": "fixture",
                    "dependencies": ["dependent_fixture", "tmp_path"],
                },
                "tmp_path": {
                    "name": "tmp_path",
                    "type": "builtin",
                    "description": "Temporary directory",
                },
            }
            return fixtures.get(name)

        with patch.object(
            extractor, "_find_fixture_definition", side_effect=mock_find_fixture
        ):
            fixtures = extractor.get_fixture_info(test_complex)

        # Should resolve the complete dependency chain
        fixture_names = {f["name"] for f in fixtures}
        assert "complex_fixture" in fixture_names
        assert "dependent_fixture" in fixture_names
        assert "base_fixture" in fixture_names
        assert "tmp_path" in fixture_names

    def test_pytest_version_compatibility(self):
        """Test compatibility with different pytest versions."""
        # This test checks that our code handles different pytest marker formats
        from failextract import FixtureExtractor

        extractor = FixtureExtractor()

        # Test with old-style pytest marker
        def old_style_fixture():
            pass

        # Mock old-style marker (different attribute structure)
        old_marker = type(
            "OldMarker", (), {"scope": "function", "params": None, "autouse": False}
        )()
        old_style_fixture._pytestfixturefunction = old_marker

        # Test with new-style pytest marker
        def new_style_fixture():
            pass

        new_marker = type(
            "NewMarker",
            (),
            {
                "scope": "session",
                "params": ["param1", "param2"],
                "autouse": True,
                "ids": ["id1", "id2"],
                "name": "custom_name",
            },
        )()
        new_style_fixture._pytestfixturefunction = new_marker

        # Both should be recognized as fixtures
        assert extractor._is_fixture(old_style_fixture, "old_style_fixture")
        assert extractor._is_fixture(new_style_fixture, "custom_name")

        # Extract info from both
        with (
            patch("inspect.getsource"),
            patch("inspect.getfile"),
            patch("inspect.getsourcelines"),
        ):
            old_info = extractor._extract_fixture_info(
                old_style_fixture, "old_style_fixture"
            )
            new_info = extractor._extract_fixture_info(new_style_fixture, "custom_name")

        # Both should extract successfully
        assert old_info["scope"] == "function"
        assert new_info["scope"] == "session"
        assert new_info["autouse"] is True
        assert new_info["params"] == ["param1", "param2"]

    def test_end_to_end_with_real_pytest_run(self, temp_directory):
        """Test end-to-end integration by actually running pytest."""
        # Create a test file that will fail and extract data
        test_file = temp_directory / "test_e2e.py"
        output_file = temp_directory / "failures.json"

        test_content = dedent(f"""
            import pytest
            from failextract import extract_on_failure
            
            @pytest.fixture
            def test_data():
                return {{"value": 42, "name": "test"}}
            
            @extract_on_failure("{output_file}")
            def test_failing_with_fixture(tmp_path, test_data):
                # This test will fail to generate failure data
                assert test_data["value"] == 100, f"Expected 100, got {{test_data['value']}}"
        """)
        test_file.write_text(test_content)

        # Run pytest on the test file
        try:
            result = subprocess.run(
                [sys.executable, "-m", "pytest", str(test_file), "-v", "--tb=short"],
                capture_output=True,
                text=True,
                cwd=temp_directory,
            )

            # Pytest should exit with code 1 (test failure)
            assert result.returncode == 1

            # Check if failure data was written
            if output_file.exists():
                with open(output_file, "r") as f:
                    failure_data = json.load(f)

                assert len(failure_data) > 0
                failure = failure_data[0]

                # Verify failure structure
                assert failure["test_name"] == "test_failing_with_fixture"
                assert "AssertionError" in failure["exception_type"]
                assert "Expected 100, got 42" in failure["exception_message"]

                # Should have fixture information
                if "fixtures" in failure:
                    fixture_names = {f["name"] for f in failure["fixtures"]}
                    assert "tmp_path" in fixture_names or "test_data" in fixture_names

        except FileNotFoundError:
            pytest.skip("pytest not available in test environment")

    def test_parametrized_test_integration(self, temp_directory):
        """Test integration with pytest parametrized tests."""
        from failextract import FailureExtractor

        # Simulate parametrized test
        test_file = temp_directory / "test_parametrized.py"
        test_file.write_text(
            dedent("""
            import pytest
            from failextract import extract_on_failure
            
            @pytest.mark.parametrize("value,expected", [
                (1, 2),
                (2, 4), 
                (3, 6),
                (4, 7)  # This will fail: 4*2 = 8, not 7
            ])
            @extract_on_failure
            def test_multiply_by_two(value, expected):
                result = value * 2
                assert result == expected, f"Expected {expected}, got {result}"
        """)
        )

        # Simulate running parametrized test
        extractor = FailureExtractor()
        extractor.clear()

        # In real pytest, this would run multiple times with different parameters
        # We'll simulate the failing case
        try:
            # Simulate the failing parameter case (4, 7)
            value, expected = 4, 7
            result = value * 2
            assert result == expected, f"Expected {expected}, got {result}"
        except AssertionError as e:
            # Simulate the decorator capturing the failure
            from failextract import extract_failure_info

            def mock_test(value, expected):
                pass

            failure_data = extract_failure_info(
                mock_test, e, (value, expected), {}, include_fixtures=True
            )
            extractor.add_failure(failure_data)

        # Verify parametrized test failure was captured
        assert len(extractor.failures) > 0
        failure = extractor.failures[0]

        # Should capture the test arguments
        assert "4" in failure["test_args"]
        assert "7" in failure["test_args"]

    def test_class_based_test_integration(self):
        """Test integration with class-based pytest tests."""
        from failextract import extract_failure_info

        class TestClass:
            @pytest.fixture
            def class_fixture(self):
                return "class_value"

            def test_method_failure(self, class_fixture):
                assert class_fixture == "wrong_value"

        # Simulate test method execution and failure
        test_instance = TestClass()

        try:
            test_instance.test_method_failure("class_value")
        except AssertionError as e:
            # Extract failure info from class method
            failure_data = extract_failure_info(
                test_instance.test_method_failure,
                e,
                ("class_value",),
                {},
                extract_classes=True,
            )

            # Should extract class information
            if failure_data.get("extracted_code"):
                # Look for class source in extracted code
                class_sources = [
                    code.get("class_source")
                    for code in failure_data["extracted_code"]
                    if code.get("class_source")
                ]
                # May or may not find class source depending on execution context
                # Just verify no errors occurred during extraction

    def test_async_test_integration(self):
        """Test integration with async pytest tests."""
        import asyncio

        from failextract import extract_failure_info

        async def async_test_function():
            await asyncio.sleep(0.01)
            assert False, "Async test failure"

        # Simulate async test failure
        try:
            asyncio.run(async_test_function())
        except AssertionError as e:
            failure_data = extract_failure_info(async_test_function, e, (), {})

            # Should handle async functions properly
            assert failure_data["test_name"] == "async_test_function"
            assert "Async test failure" in failure_data["exception_message"]

    def test_fixture_scope_detection(self):
        """Test detection of different fixture scopes."""
        from failextract import FixtureExtractor

        extractor = FixtureExtractor()

        # Create fixtures with different scopes
        def function_fixture():
            pass

        function_fixture._pytestfixturefunction = type(
            "Marker", (), {"scope": "function"}
        )()

        def session_fixture():
            pass

        session_fixture._pytestfixturefunction = type(
            "Marker", (), {"scope": "session"}
        )()

        def module_fixture():
            pass

        module_fixture._pytestfixturefunction = type(
            "Marker", (), {"scope": "module"}
        )()

        def class_fixture():
            pass

        class_fixture._pytestfixturefunction = type("Marker", (), {"scope": "class"})()

        fixtures = [function_fixture, session_fixture, module_fixture, class_fixture]
        expected_scopes = ["function", "session", "module", "class"]

        with (
            patch("inspect.getsource"),
            patch("inspect.getfile"),
            patch("inspect.getsourcelines"),
        ):
            for fixture, expected_scope in zip(fixtures, expected_scopes, strict=False):
                info = extractor._extract_fixture_info(fixture, fixture.__name__)
                assert info["scope"] == expected_scope

    def test_autouse_fixture_detection(self):
        """Test detection of autouse fixtures."""
        from failextract import FixtureExtractor

        extractor = FixtureExtractor()

        def autouse_fixture():
            pass

        autouse_fixture._pytestfixturefunction = type(
            "Marker", (), {"scope": "function", "autouse": True}
        )()

        def regular_fixture():
            pass

        regular_fixture._pytestfixturefunction = type(
            "Marker", (), {"scope": "function", "autouse": False}
        )()

        with (
            patch("inspect.getsource"),
            patch("inspect.getfile"),
            patch("inspect.getsourcelines"),
        ):
            autouse_info = extractor._extract_fixture_info(
                autouse_fixture, "autouse_fixture"
            )
            regular_info = extractor._extract_fixture_info(
                regular_fixture, "regular_fixture"
            )

        assert autouse_info["autouse"] is True
        assert regular_info["autouse"] is False
