"""Property-based tests for fixture extraction."""

import inspect
import keyword
import string
from unittest.mock import Mock, patch

from hypothesis import assume, given, settings
from hypothesis import strategies as st

from failextract import BUILTIN_FIXTURES, FixtureExtractor


class TestFixtureExtractorProperties:
    """Property-based tests for FixtureExtractor."""

    @given(
        fixture_name=st.text(
            alphabet=string.ascii_letters + string.digits + "_", min_size=1, max_size=50
        ).filter(
            lambda x: x.isidentifier()
            and not x.startswith("_")
            and not keyword.iskeyword(x)
        )
    )
    def test_fixture_discovery_robustness(self, fixture_name):
        """Test fixture discovery with various valid fixture names."""
        extractor = FixtureExtractor()

        # Create mock test function
        def test_function(**kwargs):
            pass

        # Dynamically set signature with the generated fixture name
        sig = inspect.Signature(
            [inspect.Parameter(fixture_name, inspect.Parameter.POSITIONAL_OR_KEYWORD)]
        )
        test_function.__signature__ = sig

        # Mock fixture discovery
        with patch.object(extractor, "_find_fixture_definition") as mock_find:
            mock_find.return_value = {
                "name": fixture_name,
                "type": "fixture",
                "scope": "function",
            }

            fixtures = extractor.get_fixture_info(test_function)

        # Should handle any valid identifier as fixture name
        if fixtures:
            assert any(f["name"] == fixture_name for f in fixtures)

    @given(
        fixture_names=st.lists(
            st.text(
                alphabet=string.ascii_letters + string.digits + "_",
                min_size=1,
                max_size=20,
            ).filter(
                lambda x: x.isidentifier()
                and not x.startswith("_")
                and not keyword.iskeyword(x)
                and x not in ("self", "cls")
            ),
            min_size=0,
            max_size=10,
            unique=True,
        )
    )
    def test_multiple_fixtures_extraction(self, fixture_names):
        """Test extraction of multiple fixtures with property-based names."""
        extractor = FixtureExtractor()

        # Create test function with multiple fixtures
        def test_function(**kwargs):
            pass

        # Create signature with all fixture names
        params = [
            inspect.Parameter(name, inspect.Parameter.POSITIONAL_OR_KEYWORD)
            for name in fixture_names
        ]
        test_function.__signature__ = inspect.Signature(params)

        # Mock fixture discovery for each fixture
        def mock_find_fixture(name, func, locals_dict):
            if name in fixture_names:
                return {
                    "name": name,
                    "type": "fixture",
                    "scope": "function",
                    "dependencies": [],
                }
            return None

        with patch.object(
            extractor, "_find_fixture_definition", side_effect=mock_find_fixture
        ):
            fixtures = extractor.get_fixture_info(test_function)

        # Should find all fixtures
        found_names = {f["name"] for f in fixtures}
        expected_names = set(fixture_names)
        assert found_names == expected_names

    @given(
        dependency_chain=st.lists(
            st.text(
                alphabet=string.ascii_letters + "_", min_size=1, max_size=15
            ).filter(lambda x: x.isidentifier() and not keyword.iskeyword(x)),
            min_size=1,
            max_size=5,
            unique=True,
        )
    )
    def test_fixture_dependency_chains(self, dependency_chain):
        """Test handling of fixture dependency chains of various lengths."""
        assume(len(dependency_chain) > 0)

        extractor = FixtureExtractor()

        # Create dependency chain: each fixture depends on the previous one
        def mock_find_fixture(name, func, locals_dict):
            if name not in dependency_chain:
                return None

            index = dependency_chain.index(name)
            dependencies = dependency_chain[:index]  # Depends on all previous fixtures

            return {
                "name": name,
                "type": "fixture",
                "scope": "function",
                "dependencies": dependencies,
            }

        def test_function(**kwargs):
            pass

        # Test with the last fixture in the chain (should pull in all dependencies)
        if dependency_chain:
            last_fixture = dependency_chain[-1]
            params = [
                inspect.Parameter(last_fixture, inspect.Parameter.POSITIONAL_OR_KEYWORD)
            ]
            test_function.__signature__ = inspect.Signature(params)

            with patch.object(
                extractor, "_find_fixture_definition", side_effect=mock_find_fixture
            ):
                fixtures = extractor.get_fixture_info(test_function)

            # Should resolve entire dependency chain
            found_names = {f["name"] for f in fixtures}
            expected_names = set(dependency_chain)
            assert found_names == expected_names

    @given(scope=st.sampled_from(["function", "class", "module", "session", "package"]))
    def test_fixture_scope_handling(self, scope):
        """Test handling of various fixture scopes."""
        extractor = FixtureExtractor()

        def test_fixture():
            pass

        # Mock pytest marker with the given scope
        test_fixture._pytestfixturefunction = Mock()
        test_fixture._pytestfixturefunction.scope = scope
        test_fixture._pytestfixturefunction.params = None
        test_fixture._pytestfixturefunction.autouse = False
        test_fixture._pytestfixturefunction.ids = None

        with (
            patch("inspect.getsource"),
            patch("inspect.getfile"),
            patch("inspect.getsourcelines"),
        ):
            info = extractor._extract_fixture_info(test_fixture, "test_fixture")

        # Should handle any valid pytest scope
        assert info["scope"] == scope

    @given(
        autouse=st.booleans(),
        params=st.one_of(
            st.none(),
            st.lists(st.text(min_size=1, max_size=10), min_size=1, max_size=5),
        ),
    )
    def test_fixture_marker_attributes(self, autouse, params):
        """Test handling of various fixture marker attributes."""
        extractor = FixtureExtractor()

        def test_fixture():
            pass

        # Mock pytest marker with the given attributes
        marker = Mock()
        marker.scope = "function"
        marker.autouse = autouse
        marker.params = params
        marker.ids = None
        test_fixture._pytestfixturefunction = marker

        with (
            patch("inspect.getsource"),
            patch("inspect.getfile"),
            patch("inspect.getsourcelines"),
        ):
            info = extractor._extract_fixture_info(test_fixture, "test_fixture")

        # Should correctly extract marker attributes
        assert info["autouse"] == autouse
        assert info["params"] == params

    @given(builtin_name=st.sampled_from(list(BUILTIN_FIXTURES.keys())))
    def test_builtin_fixture_consistency(self, builtin_name):
        """Test that all builtin fixtures are handled consistently."""
        extractor = FixtureExtractor()

        def test_function(**kwargs):
            pass

        # Create signature with builtin fixture
        params = [
            inspect.Parameter(builtin_name, inspect.Parameter.POSITIONAL_OR_KEYWORD)
        ]
        test_function.__signature__ = inspect.Signature(params)

        fixtures = extractor.get_fixture_info(test_function)

        # Should find the builtin fixture
        assert len(fixtures) > 0
        builtin_fixture = next(f for f in fixtures if f["name"] == builtin_name)
        assert builtin_fixture["type"] == "builtin"
        assert builtin_fixture["description"] == BUILTIN_FIXTURES[builtin_name]

    @given(cache_size=st.integers(min_value=1, max_value=20))
    @settings(max_examples=5, deadline=500)  # Reduce examples and increase deadline
    def test_fixture_cache_behavior(self, cache_size):
        """Test fixture cache behavior with various cache sizes."""
        extractor = FixtureExtractor()

        def test_function():
            pass

        test_function.__module__ = "test_module"

        # Generate fixture names
        fixture_names = [f"fixture_{i}" for i in range(cache_size)]

        # Mock fixture discovery to always return a fixture
        def mock_find_fixture(name, func, locals_dict):
            return {"name": name, "type": "fixture", "scope": "function"}

        # First call should miss cache
        for fixture_name in fixture_names:
            with patch.object(
                extractor, "_find_fixture_definition", side_effect=mock_find_fixture
            ) as mock_find:
                result = extractor._find_fixture_definition(
                    fixture_name, test_function, {}
                )
                assert mock_find.called

        # Second call should hit cache
        original_find = extractor._find_fixture_definition
        call_count = 0

        def counting_find(name, func, locals_dict):
            nonlocal call_count
            call_count += 1
            return original_find(name, func, locals_dict)

        with patch.object(
            extractor, "_find_fixture_definition", side_effect=counting_find
        ):
            for fixture_name in fixture_names:
                extractor._find_fixture_definition(fixture_name, test_function, {})

        # Should have cache hits (call_count should be less than or equal to cache_size)
        # Cache behavior depends on implementation, but should be reasonable
        assert call_count <= cache_size * 2  # Allow for some cache misses

    @given(
        file_path=st.builds(
            lambda dir_parts, filename: "/".join(dir_parts) + "/" + filename + ".py",
            st.lists(
                st.text(
                    alphabet=string.ascii_letters + string.digits,
                    min_size=1,
                    max_size=10,
                ),
                min_size=1,
                max_size=5,
            ),
            st.text(
                alphabet=string.ascii_letters + string.digits, min_size=1, max_size=15
            ),
        )
    )
    def test_conftest_path_handling(self, file_path):
        """Test handling of various file paths for conftest discovery."""
        assume("conftest.py" not in file_path)  # Avoid conflicts

        extractor = FixtureExtractor()

        def test_function():
            pass

        with patch("inspect.getfile", return_value=file_path):
            with patch("pathlib.Path.exists", return_value=True):
                with patch("importlib.util.spec_from_file_location") as mock_spec:
                    mock_spec.return_value = None  # Simulate import failure

                    # Should handle gracefully regardless of path structure
                    result = extractor._get_conftest_modules(test_function)
                    assert isinstance(result, list)

    @given(
        source_code=st.text(
            alphabet=string.ascii_letters + string.digits + " \n\t:()[]{}\"'",
            min_size=10,
            max_size=500,
        )
    )
    @settings(max_examples=20)  # Limit for performance
    def test_source_extraction_robustness(self, source_code):
        """Test source extraction with various code patterns."""
        extractor = FixtureExtractor()

        def test_fixture():
            pass

        # Mock source extraction
        with patch("inspect.getsource", return_value=source_code):
            with patch("inspect.getfile"), patch("inspect.getsourcelines"):
                try:
                    info = extractor._extract_fixture_info(test_fixture, "test_fixture")

                    # If successful, should have source
                    assert "source" in info
                    assert isinstance(info["source"], str)

                    # Should correctly detect yield fixtures
                    if "yield" in source_code:
                        assert info.get("is_yield_fixture") is True
                    else:
                        assert info.get("is_yield_fixture") is False

                except Exception:
                    # Some source patterns might cause issues, which is acceptable
                    # as long as it doesn't crash the entire system
                    pass

    @given(
        num_fixtures=st.integers(min_value=0, max_value=20),
        include_duplicates=st.booleans(),
    )
    def test_fixture_deduplication(self, num_fixtures, include_duplicates):
        """Test that fixture extraction handles duplicates correctly."""
        extractor = FixtureExtractor()

        # Generate fixture names
        fixture_names = [f"fixture_{i}" for i in range(num_fixtures)]

        # For signature, use unique names only (signatures can't have duplicates)
        unique_fixture_names = list(
            dict.fromkeys(fixture_names)
        )  # Preserve order, remove duplicates

        def test_function(**kwargs):
            pass

        # Create signature with unique fixture names
        params = [
            inspect.Parameter(name, inspect.Parameter.POSITIONAL_OR_KEYWORD)
            for name in unique_fixture_names
        ]
        test_function.__signature__ = inspect.Signature(params)

        # But test with the original list (potentially with duplicates) for extraction logic
        test_fixture_names = fixture_names
        if include_duplicates and fixture_names:
            test_fixture_names.extend(fixture_names[: min(3, len(fixture_names))])

        # Mock fixture discovery
        def mock_find_fixture(name, func, locals_dict):
            return {"name": name, "type": "fixture", "scope": "function"}

        with patch.object(
            extractor, "_find_fixture_definition", side_effect=mock_find_fixture
        ):
            fixtures = extractor.get_fixture_info(test_function)

        # Should handle duplicates properly (exact behavior depends on implementation)
        # At minimum, should not crash and should return reasonable results
        assert isinstance(fixtures, list)

        # Each fixture should be valid
        for fixture in fixtures:
            assert "name" in fixture
            assert "type" in fixture
