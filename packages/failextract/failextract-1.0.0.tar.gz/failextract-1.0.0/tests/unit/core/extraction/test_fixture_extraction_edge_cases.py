"""Edge case tests for fixture extraction functionality."""

import inspect
from unittest.mock import Mock, patch

import pytest

from failextract import FixtureExtractor


class TestFixtureExtractionEdgeCases:
    """Test edge cases for fixture extraction functionality."""

    def test_fixture_extractor_edge_cases(self):
        """Test FixtureExtractor edge cases for coverage."""
        extractor = FixtureExtractor()

        # Test with function that has no module
        def test_no_module():
            pass

        test_no_module.__module__ = None

        fixtures = extractor.get_fixture_info(test_no_module)
        assert isinstance(fixtures, list)

        # Test circular dependency handling
        seen = {"fixture_a"}
        result = extractor._extract_fixture_chain("fixture_a", test_no_module, {}, seen)
        assert result == []  # Should return empty for already seen

        # Test conftest module import failure
        with patch("importlib.util.spec_from_file_location", return_value=None):
            modules = extractor._get_conftest_modules(test_no_module)
            assert isinstance(modules, list)

    def test_builtin_fixtures_coverage(self):
        """Test builtin fixtures for coverage."""
        extractor = FixtureExtractor()

        # Test each builtin fixture
        for fixture_name in ["request", "tmp_path", "pytestconfig"]:

            def test_with_builtin():
                pass

            # Mock signature to include builtin fixture
            params = [
                inspect.Parameter(fixture_name, inspect.Parameter.POSITIONAL_OR_KEYWORD)
            ]
            test_with_builtin.__signature__ = inspect.Signature(params)

            fixtures = extractor.get_fixture_info(test_with_builtin)

            # Should find the builtin fixture
            found = any(f["name"] == fixture_name for f in fixtures)
            assert found

    def test_fixture_info_extraction_edge_cases(self):
        """Test fixture info extraction edge cases."""
        extractor = FixtureExtractor()

        # Test fixture with all marker attributes
        def complex_fixture():
            pass

        marker = Mock()
        marker.scope = "session"
        marker.params = ["param1", "param2"]
        marker.autouse = True
        marker.ids = ["id1", "id2"]
        marker.name = "custom_name"
        complex_fixture._pytestfixturefunction = marker

        with patch(
            "inspect.getsource", return_value='def complex_fixture(): yield "value"'
        ):
            with patch("inspect.getfile", return_value="/conftest.py"):
                with patch("inspect.getsourcelines", return_value=([], 10)):
                    info = extractor._extract_fixture_info(
                        complex_fixture, "custom_name"
                    )

        assert info["scope"] == "session"
        assert info["params"] == ["param1", "param2"]
        assert info["autouse"] is True
        assert info["ids"] == ["id1", "id2"]
        assert info["is_yield_fixture"] is True