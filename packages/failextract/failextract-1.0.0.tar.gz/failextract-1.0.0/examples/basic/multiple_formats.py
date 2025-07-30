#!/usr/bin/env python3
"""
Basic example: Multiple output formats

This example demonstrates generating reports in all supported formats.
"""

from failextract import extract_on_failure, FailureExtractor, OutputConfig, OutputFormat


@extract_on_failure
def test_database_connection():
    """Simulate a database connection test failure."""
    connection_string = "postgresql://user:pass@localhost:5432/testdb"
    connected = False  # Simulate connection failure
    
    assert connected, f"Failed to connect to database: {connection_string}"


@extract_on_failure
def test_api_response():
    """Simulate an API response validation failure."""
    api_response = {
        'status': 'error',
        'code': 500,
        'message': 'Internal server error',
        'data': None
    }
    
    assert api_response['status'] == 'success', f"API returned error: {api_response}"


@extract_on_failure
def test_file_processing():
    """Simulate a file processing failure."""
    file_path = "/data/important_file.csv"
    file_exists = False  # Simulate missing file
    
    assert file_exists, f"Required file not found: {file_path}"


def generate_all_formats():
    """Generate reports in all supported formats."""
    extractor = FailureExtractor()
    
    if not extractor.failures:
        print("No failures to report")
        return
    
    # All supported formats
    formats = [
        ("json", "Machine-readable JSON format"),
        ("markdown", "Markdown format for documentation"),
        ("xml", "XML format for structured data"),
        ("csv", "CSV format for spreadsheet analysis"),
        ("yaml", "YAML format for configuration-like output")
    ]
    
    print(f"Generating reports for {len(extractor.failures)} failures...\n")
    
    for format_name, description in formats:
        try:
            config = OutputConfig(f"failures.{format_name}", format=format_name)
            extractor.save_report(config)
            print(f"✓ Generated failures.{format_name} - {description}")
        except Exception as e:
            print(f"✗ Failed to generate {format_name}: {e}")
    
    print(f"\nGenerated {len(formats)} report files")
    print("\nFiles created:")
    for format_name, _ in formats:
        print(f"  - failures.{format_name}")


if __name__ == "__main__":
    print("Running multiple format example...")
    
    # Run the failing tests to generate some failures
    tests = [test_database_connection, test_api_response, test_file_processing]
    
    for test_func in tests:
        try:
            test_func()
        except AssertionError:
            pass  # Expected to fail
    
    # Generate reports in all formats
    generate_all_formats()
    
    # Show some statistics
    extractor = FailureExtractor()
    print(f"\nCaptured failures:")
    for i, failure in enumerate(extractor.failures, 1):
        print(f"  {i}. {failure['test_name']}")
        print(f"     Error: {failure['exception_message']}")
        print(f"     Module: {failure['test_module']}")
        print()