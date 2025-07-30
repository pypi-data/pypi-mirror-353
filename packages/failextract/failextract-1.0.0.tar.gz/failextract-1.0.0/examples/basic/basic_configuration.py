#!/usr/bin/env python3
"""
Basic Configuration Examples for FailExtract

This example demonstrates various configuration options for FailExtract
including output formats, memory management, and decorator options.
"""

import tempfile
from pathlib import Path

from failextract import (
    FailureExtractor,
    OutputConfig,
    OutputFormat,
    extract_on_failure,
    generate_session_report,
)


def example_decorator_configurations():
    """Demonstrate different decorator configuration options."""
    print("=== Decorator Configuration Examples ===\n")

    # 1. Basic decorator with default settings
    @extract_on_failure
    def test_basic():
        """Basic failure capture with defaults."""
        assert 1 == 2, "Basic assertion failure"

    # 2. Decorator with HTML output
    @extract_on_failure("failures.html")
    def test_html_output():
        """Capture failures to HTML file."""
        assert "hello" == "world", "String comparison failure"

    # 3. Decorator with detailed context
    @extract_on_failure(
        output="detailed_failures.json",
        include_locals=True,
        include_fixtures=True,
        max_depth=15,
    )
    def test_detailed_capture():
        """Capture with maximum context information."""
        local_var = {"user": "john", "active": True}
        assert local_var["active"] == False, "User should be inactive"

    # 4. Decorator with custom options
    @extract_on_failure(
        output="minimal_failures.json",
        include_locals=False,
        skip_stdlib=True,
        extract_classes=False,
    )
    def test_minimal_capture():
        """Minimal failure capture for performance."""
        data = [1, 2, 3, 4, 5]
        assert len(data) == 10, "Data length mismatch"

    # Run examples
    examples = [
        ("Basic Decorator", test_basic),
        ("HTML Output", test_html_output),
        ("Detailed Capture", test_detailed_capture),
        ("Minimal Capture", test_minimal_capture),
    ]

    for name, test_func in examples:
        print(f"Running {name}...")
        try:
            test_func()
        except AssertionError:
            print(f"  ✓ {name} failure captured")
        except Exception as e:
            print(f"  ✗ Unexpected error in {name}: {e}")


def example_output_configurations():
    """Demonstrate various output configuration options."""
    print("\n=== Output Configuration Examples ===\n")

    # Get the extractor instance
    extractor = FailureExtractor()

    # Add some sample failure data for demonstration
    sample_failure = {
        "timestamp": "2024-01-01T12:00:00",
        "test_name": "test_sample",
        "test_module": "example_module",
        "test_file": "/path/to/test.py",
        "exception_type": "AssertionError",
        "exception_message": "Sample failure for demonstration",
        "test_source": "def test_sample():\n    assert False, 'Sample failure'",
    }
    extractor.add_failure(sample_failure)

    # 1. Basic JSON output
    json_config = OutputConfig("output_basic.json")
    print("1. Basic JSON configuration:")
    print(f"   File: {json_config.filename}")
    print(f"   Format: {json_config.format}")
    print(f"   Append: {json_config.append}")

    # 2. HTML output with explicit format
    html_config = OutputConfig("report.html", format="html")
    print("\n2. HTML configuration:")
    print(f"   File: {html_config.filename}")
    print(f"   Format: {html_config.format}")

    # 3. Markdown output with append mode
    md_config = OutputConfig("failures.md", format="markdown", append=True)
    print("\n3. Markdown with append:")
    print(f"   File: {md_config.filename}")
    print(f"   Format: {md_config.format}")
    print(f"   Append: {md_config.append}")

    # 4. YAML output with limits
    yaml_config = OutputConfig(
        "limited_failures.yaml", format="yaml", max_failures=50
    )
    print("\n4. YAML with limits:")
    print(f"   File: {yaml_config.filename}")
    print(f"   Format: {yaml_config.format}")
    print(f"   Max failures: {yaml_config.max_failures}")

    # 5. CSV output for analysis
    csv_config = OutputConfig("analysis.csv", format="csv")
    print("\n5. CSV for data analysis:")
    print(f"   File: {csv_config.filename}")
    print(f"   Format: {csv_config.format}")

    # 6. XML output for tool integration
    xml_config = OutputConfig("integration.xml", format="xml")
    print("\n6. XML for tool integration:")
    print(f"   File: {xml_config.filename}")
    print(f"   Format: {xml_config.format}")

    # Generate all reports
    configs = [json_config, html_config, md_config, yaml_config, csv_config, xml_config]

    print("\nGenerating all configured reports...")
    for config in configs:
        try:
            extractor.save_report(config)
            print(f"  ✓ Generated {config.filename}")
        except Exception as e:
            print(f"  ✗ Failed to generate {config.filename}: {e}")


def example_memory_management():
    """Demonstrate memory management configuration."""
    print("\n=== Memory Management Examples ===\n")

    extractor = FailureExtractor()

    # Check initial state
    print("1. Initial memory state:")
    stats = extractor.get_stats()
    limits = extractor.get_memory_limits()
    print(f"   Failures: {stats['failures_count']}")
    print(f"   Passed: {stats['passed_count']}")
    print(f"   Max failures limit: {limits['max_failures']}")
    print(f"   Max passed limit: {limits['max_passed']}")

    # Set memory limits
    print("\n2. Setting memory limits (max 100 failures, 50 passed):")
    extractor.set_memory_limits(max_failures=100, max_passed=50)
    limits = extractor.get_memory_limits()
    print(f"   Max failures limit: {limits['max_failures']}")
    print(f"   Max passed limit: {limits['max_passed']}")

    # Add some data to demonstrate limits
    print("\n3. Adding test data...")
    for i in range(5):
        failure = {
            "timestamp": f"2024-01-01T12:0{i}:00",
            "test_name": f"test_failure_{i}",
            "test_module": "demo_module",
            "test_file": "/demo/test.py",
            "exception_type": "AssertionError",
            "exception_message": f"Demo failure {i}",
        }
        extractor.add_failure(failure)

        passed = {
            "timestamp": f"2024-01-01T12:0{i}:30",
            "test_name": f"test_passed_{i}",
            "test_module": "demo_module",
            "test_file": "/demo/test.py",
        }
        extractor.add_passed(passed)

    # Check final state
    print("\n4. Final memory state after adding data:")
    stats = extractor.get_stats()
    print(f"   Failures: {stats['failures_count']}")
    print(f"   Passed: {stats['passed_count']}")
    print(f"   Total: {stats['total_count']}")
    print(f"   At failure limit: {stats['failures_at_limit']}")
    print(f"   At passed limit: {stats['passed_at_limit']}")


def example_format_detection():
    """Demonstrate automatic format detection from file extensions."""
    print("\n=== Format Detection Examples ===\n")

    # Test various file extensions
    test_files = [
        "report.json",
        "failures.html",
        "summary.md",
        "data.csv",
        "config.yaml",
        "integration.xml",
        "unknown.txt",  # Should default to JSON
    ]

    for filename in test_files:
        try:
            config = OutputConfig(filename)
            print(f"{filename:15} -> {config.format.value}")
        except Exception as e:
            print(f"{filename:15} -> Error: {e}")


def example_session_reporting():
    """Demonstrate session-level reporting."""
    print("\n=== Session Reporting Examples ===\n")

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        # 1. Generate session report with defaults
        print("1. Generating default session report...")
        default_report = temp_path / "session_default.md"
        try:
            generate_session_report(str(default_report))
            if default_report.exists():
                print(f"   ✓ Generated: {default_report}")
                print(f"   Size: {default_report.stat().st_size} bytes")
            else:
                print("   ⚠ No failures to report")
        except Exception as e:
            print(f"   ✗ Error: {e}")

        # 2. Generate HTML session report
        print("\n2. Generating HTML session report...")
        html_report = temp_path / "session_report.html"
        try:
            generate_session_report(str(html_report), format="html")
            if html_report.exists():
                print(f"   ✓ Generated: {html_report}")
                print(f"   Size: {html_report.stat().st_size} bytes")
            else:
                print("   ⚠ No failures to report")
        except Exception as e:
            print(f"   ✗ Error: {e}")

        # 3. Generate JSON session report without clearing
        print("\n3. Generating JSON session report (no clear)...")
        json_report = temp_path / "session_data.json"
        try:
            generate_session_report(str(json_report), format="json", clear=False)
            if json_report.exists():
                print(f"   ✓ Generated: {json_report}")
                print(f"   Size: {json_report.stat().st_size} bytes")
            else:
                print("   ⚠ No failures to report")
        except Exception as e:
            print(f"   ✗ Error: {e}")


def example_error_handling():
    """Demonstrate configuration error handling."""
    print("\n=== Error Handling Examples ===\n")

    print("1. Testing invalid configurations:")

    # Test invalid format
    try:
        config = OutputConfig("test.txt", format="invalid")
        print("   ✗ Should have failed with invalid format")
    except ValueError as e:
        print(f"   ✓ Caught invalid format error: {e}")

    # Test invalid max_failures
    try:
        config = OutputConfig("test.json", max_failures=-1)
        print("   ✗ Should have failed with negative max_failures")
    except ValueError as e:
        print(f"   ✓ Caught negative max_failures error: {e}")

    # Test type errors
    try:
        config = OutputConfig("test.json", append="not_a_bool")
        print("   ✗ Should have failed with wrong append type")
    except TypeError as e:
        print(f"   ✓ Caught type error: {e}")

    print("\n2. Testing format mismatch warnings:")
    try:
        # This should generate a warning
        config = OutputConfig("data.json", format="yaml")
        print(f"   ✓ Created config with format override: {config.format}")
    except Exception as e:
        print(f"   ✗ Unexpected error: {e}")


def main():
    """Run all configuration examples."""
    print("FailExtract Configuration Examples")
    print("=" * 40)

    # Run all example categories
    example_decorator_configurations()
    example_output_configurations()
    example_memory_management()
    example_format_detection()
    example_session_reporting()
    example_error_handling()

    print("\n" + "=" * 40)
    print("Configuration examples completed!")
    print("\nGenerated files:")
    for file in Path(".").glob("*.json"):
        print(f"  - {file}")
    for file in Path(".").glob("*.html"):
        print(f"  - {file}")
    for file in Path(".").glob("*.md"):
        print(f"  - {file}")
    for file in Path(".").glob("*.csv"):
        print(f"  - {file}")
    for file in Path(".").glob("*.yaml"):
        print(f"  - {file}")
    for file in Path(".").glob("*.xml"):
        print(f"  - {file}")


if __name__ == "__main__":
    main()