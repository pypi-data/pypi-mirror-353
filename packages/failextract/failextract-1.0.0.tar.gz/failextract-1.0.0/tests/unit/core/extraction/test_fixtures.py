"""Unit tests for FixtureExtractor class."""

from unittest.mock import Mock, patch

from failextract import BUILTIN_FIXTURES, FixtureExtractor


class TestFixtureExtractor:
    """Test cases for FixtureExtractor."""

    def test_initialization(self):
        """Test FixtureExtractor initialization."""
        extractor = FixtureExtractor()
        assert hasattr(extractor, "_fixture_cache")
        assert isinstance(extractor._fixture_cache, dict)
        assert len(extractor._fixture_cache) == 0

    def test_get_fixture_info_simple_function(self, mock_test_function):
        """Test fixture extraction from simple function with no fixtures."""
        extractor = FixtureExtractor()

        def test_no_fixtures():
            pass

        fixtures = extractor.get_fixture_info(test_no_fixtures)
        assert fixtures == []

    def test_get_fixture_info_with_fixtures(self):
        """Test fixture extraction from function with fixtures."""
        extractor = FixtureExtractor()

        def test_with_fixtures(tmp_path, request):
            pass

        fixtures = extractor.get_fixture_info(test_with_fixtures)

        # Should find at least the builtin fixtures
        fixture_names = {f["name"] for f in fixtures}
        assert "tmp_path" in fixture_names
        assert "request" in fixture_names

    def test_get_fixture_info_excludes_self_cls(self):
        """Test that self and cls parameters are excluded from fixtures."""
        extractor = FixtureExtractor()

        class TestClass:
            def test_method(self, tmp_path):
                pass

            @classmethod
            def test_classmethod(cls, request):
                pass

        # Test instance method
        fixtures = extractor.get_fixture_info(TestClass.test_method)
        fixture_names = {f["name"] for f in fixtures}
        assert "self" not in fixture_names
        assert "tmp_path" in fixture_names

        # Test class method
        fixtures = extractor.get_fixture_info(TestClass.test_classmethod)
        fixture_names = {f["name"] for f in fixtures}
        assert "cls" not in fixture_names
        assert "request" in fixture_names

    def test_extract_fixture_chain_circular_dependency(self):
        """Test handling of circular fixture dependencies."""
        extractor = FixtureExtractor()
        seen = set()

        # Mock a circular dependency scenario
        def mock_find_fixture(name, *args):
            if name == "fixture_a":
                return {"name": "fixture_a", "dependencies": ["fixture_b"]}
            elif name == "fixture_b":
                return {
                    "name": "fixture_b",
                    "dependencies": ["fixture_a"],  # Creates circular dependency
                }
            return None

        with patch.object(
            extractor, "_find_fixture_definition", side_effect=mock_find_fixture
        ):
            result = extractor._extract_fixture_chain(
                "fixture_a", lambda: None, {}, seen
            )

            # Should not infinite loop and should handle seen fixtures
            # Should return both fixtures but only once each due to circular dependency handling
            assert len(result) == 2
            fixture_names = [f["name"] for f in result]
            assert "fixture_a" in fixture_names
            assert "fixture_b" in fixture_names

    def test_find_fixture_definition_builtin(self):
        """Test finding builtin fixtures."""
        extractor = FixtureExtractor()

        def dummy_test():
            pass

        # Test finding a builtin fixture
        result = extractor._find_fixture_definition("tmp_path", dummy_test, {})

        assert result is not None
        assert result["name"] == "tmp_path"
        assert result["type"] == "builtin"
        assert "description" in result

    def test_find_fixture_definition_caching(self):
        """Test that fixture definitions are cached properly."""
        extractor = FixtureExtractor()

        def dummy_test():
            pass

        # First call
        result1 = extractor._find_fixture_definition("tmp_path", dummy_test, {})

        # Second call should use cache
        result2 = extractor._find_fixture_definition("tmp_path", dummy_test, {})

        assert result1 == result2

        # Check cache
        cache_key = f"{dummy_test.__module__}:tmp_path"
        assert cache_key in extractor._fixture_cache

    def test_is_fixture_with_pytest_marker(self):
        """Test fixture detection with pytest markers."""
        extractor = FixtureExtractor()

        # Mock function with pytest fixture marker
        mock_func = Mock()
        mock_func.__name__ = "test_fixture"
        mock_func._pytestfixturefunction = Mock()
        mock_func._pytestfixturefunction.name = None  # Use function name

        assert extractor._is_fixture(mock_func, "test_fixture") is True
        assert extractor._is_fixture(mock_func, "different_name") is False

    def test_is_fixture_with_custom_name(self):
        """Test fixture detection with custom fixture names."""
        extractor = FixtureExtractor()

        # Mock function with custom fixture name
        mock_func = Mock()
        mock_func.__name__ = "actual_function_name"
        mock_func._pytestfixturefunction = Mock()
        mock_func._pytestfixturefunction.name = "custom_fixture_name"

        assert extractor._is_fixture(mock_func, "custom_fixture_name") is True
        assert extractor._is_fixture(mock_func, "actual_function_name") is False

    def test_is_fixture_non_callable(self):
        """Test fixture detection with non-callable objects."""
        extractor = FixtureExtractor()

        # Non-callable object
        non_callable = "not a function"

        assert extractor._is_fixture(non_callable, "anything") is False

    def test_extract_fixture_info_basic(self):
        """Test basic fixture information extraction."""
        extractor = FixtureExtractor()

        def sample_fixture():
            """Sample fixture docstring."""
            return "value"

        # Mock pytest marker
        sample_fixture._pytestfixturefunction = Mock()
        sample_fixture._pytestfixturefunction.scope = "function"
        sample_fixture._pytestfixturefunction.params = None
        sample_fixture._pytestfixturefunction.autouse = False
        sample_fixture._pytestfixturefunction.ids = None

        with patch(
            "inspect.getsource",
            return_value='def sample_fixture():\n    return "value"',
        ):
            with patch("inspect.getfile", return_value="/path/to/file.py"):
                with patch("inspect.getsourcelines", return_value=([], 10)):
                    result = extractor._extract_fixture_info(
                        sample_fixture, "sample_fixture"
                    )

        assert result["name"] == "sample_fixture"
        assert result["type"] == "fixture"
        assert result["function_name"] == "sample_fixture"
        assert result["scope"] == "function"
        assert result["autouse"] is False
        assert "source" in result

    def test_extract_fixture_info_with_dependencies(self):
        """Test fixture information extraction with dependencies."""
        extractor = FixtureExtractor()

        def dependent_fixture(tmp_path, request):
            """Fixture with dependencies."""
            return "dependent_value"

        # Mock pytest marker
        dependent_fixture._pytestfixturefunction = Mock()
        dependent_fixture._pytestfixturefunction.scope = "function"

        with (
            patch("inspect.getsource"),
            patch("inspect.getfile"),
            patch("inspect.getsourcelines"),
        ):
            result = extractor._extract_fixture_info(
                dependent_fixture, "dependent_fixture"
            )

        assert "dependencies" in result
        assert "tmp_path" in result["dependencies"]
        # Note: 'request' is filtered out as it's a special pytest parameter
        assert "request" not in result["dependencies"]
        assert "self" not in result["dependencies"]
        assert "cls" not in result["dependencies"]

    def test_extract_fixture_info_yield_fixture(self):
        """Test detection of yield fixtures."""
        extractor = FixtureExtractor()

        def yield_fixture():
            yield "value"

        yield_fixture._pytestfixturefunction = Mock()

        with patch(
            "inspect.getsource", return_value='def yield_fixture():\n    yield "value"'
        ):
            with patch("inspect.getfile"), patch("inspect.getsourcelines"):
                result = extractor._extract_fixture_info(yield_fixture, "yield_fixture")

        assert result["is_yield_fixture"] is True

    def test_extract_fixture_info_source_extraction_failure(self):
        """Test handling of source extraction failures."""
        extractor = FixtureExtractor()

        def problematic_fixture():
            pass

        problematic_fixture._pytestfixturefunction = Mock()

        with patch("inspect.getsource", side_effect=OSError("Source not available")):
            result = extractor._extract_fixture_info(
                problematic_fixture, "problematic_fixture"
            )

        assert "source" in result
        assert "Could not extract source" in result["source"]

    def test_get_conftest_modules(self):
        """Test conftest module discovery."""
        extractor = FixtureExtractor()

        def test_function():
            pass

        # Mock the file structure
        with patch("inspect.getfile", return_value="/project/tests/test_file.py"):
            with patch("pathlib.Path.exists") as mock_exists:
                with patch("importlib.util.spec_from_file_location") as mock_spec:
                    with patch("importlib.util.module_from_spec") as mock_module:
                        # Setup mocks
                        mock_exists.return_value = True
                        mock_spec.return_value = Mock()
                        mock_spec.return_value.loader = Mock()
                        mock_module.return_value = Mock()
                        mock_module.return_value.__dict__ = {"fixture_func": "value"}

                        result = extractor._get_conftest_modules(test_function)

                        # Should attempt to load conftest modules
                        assert isinstance(result, list)

    def test_get_conftest_modules_error_handling(self):
        """Test conftest module discovery error handling."""
        extractor = FixtureExtractor()

        def test_function():
            pass

        # Mock to raise exception
        with patch("inspect.getfile", side_effect=Exception("File not found")):
            result = extractor._get_conftest_modules(test_function)

            # Should return empty list on error
            assert result == []

    def test_builtin_fixtures_coverage(self):
        """Test that all expected builtin fixtures are defined."""
        expected_builtins = [
            "request",
            "tmp_path",
            "tmp_path_factory",
            "pytestconfig",
            "cache",
            "capfd",
            "capfdbinary",
            "caplog",
            "capsys",
            "capsysbinary",
            "doctest_namespace",
            "monkeypatch",
            "pytester",
            "recwarn",
            "tmpdir",
        ]

        for fixture_name in expected_builtins:
            assert fixture_name in BUILTIN_FIXTURES
            assert isinstance(BUILTIN_FIXTURES[fixture_name], str)
            assert len(BUILTIN_FIXTURES[fixture_name]) > 0

    def test_complex_fixture_scenario(self):
        """Test complex fixture extraction scenario."""
        extractor = FixtureExtractor()

        def complex_test(tmp_path, request, custom_fixture):
            """Test with multiple fixtures including custom ones."""
            pass

        with patch.object(extractor, "_find_fixture_definition") as mock_find:

            def side_effect(name, func, locals_dict):
                if name in BUILTIN_FIXTURES:
                    return {
                        "name": name,
                        "type": "builtin",
                        "description": BUILTIN_FIXTURES[name],
                    }
                elif name == "custom_fixture":
                    return {
                        "name": "custom_fixture",
                        "type": "fixture",
                        "scope": "session",
                        "dependencies": ["tmp_path"],
                    }
                return None

            mock_find.side_effect = side_effect

            fixtures = extractor.get_fixture_info(complex_test)

            # Verify all fixtures were found
            fixture_names = {f["name"] for f in fixtures}
            assert "tmp_path" in fixture_names
            assert "request" in fixture_names
            assert "custom_fixture" in fixture_names

            # Verify fixture types
            fixture_types = {f["name"]: f["type"] for f in fixtures}
            assert fixture_types["tmp_path"] == "builtin"
            assert fixture_types["custom_fixture"] == "fixture"

    def test_frame_locals_integration(self):
        """Test integration with frame locals."""
        extractor = FixtureExtractor()

        def test_with_frame_locals(fixture_param):
            pass

        frame_locals = {"fixture_param": "test_value", "other_var": "ignored"}

        # Mock finding fixture in frame locals
        with patch.object(extractor, "_find_fixture_definition") as mock_find:
            mock_find.return_value = {
                "name": "fixture_param",
                "type": "runtime",
                "value": "test_value",
            }

            fixtures = extractor.get_fixture_info(test_with_frame_locals, frame_locals)

            assert len(fixtures) > 0
            assert fixtures[0]["name"] == "fixture_param"

    def test_cache_key_generation(self):
        """Test that cache keys are generated correctly."""
        extractor = FixtureExtractor()

        def test_function():
            pass

        test_function.__module__ = "test_module"

        # Test with builtin fixture (which will be cached)
        result = extractor._find_fixture_definition("request", test_function, {})

        # Check cache key format for builtin fixture
        expected_key = "test_module:request"
        assert expected_key in extractor._fixture_cache
        assert result is not None
        assert result["name"] == "request"
        assert result["type"] == "builtin"

    def test_edge_case_empty_signature(self):
        """Test handling of functions with empty signatures."""
        extractor = FixtureExtractor()

        def test_no_params():
            pass

        fixtures = extractor.get_fixture_info(test_no_params)
        assert fixtures == []

    def test_memory_efficiency(self):
        """Test that cache doesn't grow unbounded."""
        extractor = FixtureExtractor()

        # Test with many different fixtures
        for i in range(100):

            def test_func():
                pass

            test_func.__module__ = f"module_{i}"
            test_func.__name__ = f"test_{i}"

            with patch.object(extractor, "_find_fixture_definition") as mock_find:
                mock_find.return_value = None  # No fixtures found
                extractor.get_fixture_info(test_func)

        # Cache should not grow excessively for non-existent fixtures
        assert len(extractor._fixture_cache) <= 100  # Reasonable upper bound
