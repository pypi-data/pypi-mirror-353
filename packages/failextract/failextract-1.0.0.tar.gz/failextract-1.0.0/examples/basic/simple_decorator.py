#!/usr/bin/env python3
"""
Basic example: Simple decorator usage

This example demonstrates the most basic usage of FailExtract
with the @extract_on_failure decorator.
"""

from failextract import extract_on_failure, FailureExtractor, OutputConfig


@extract_on_failure
def test_basic_assertion():
    """A simple test that will fail and be captured."""
    x = 10
    y = 20
    assert x > y, f"Expected {x} to be greater than {y}"


@extract_on_failure
def test_with_setup():
    """Test with some setup that will fail."""
    # Setup some data
    user_data = {
        'name': 'John Doe',
        'email': 'john@example.com',
        'age': 25
    }
    
    # This will fail and capture the context
    assert user_data['age'] > 30, "User must be over 30"


@extract_on_failure
def test_list_operations():
    """Test with list operations that will fail."""
    numbers = [1, 2, 3, 4, 5]
    filtered = [n for n in numbers if n > 10]
    
    assert len(filtered) > 0, "Should have found numbers greater than 10"


def test_success_example():
    """This test will pass - not decorated so won't be captured."""
    assert 1 + 1 == 2


if __name__ == "__main__":
    print("Running basic decorator examples...")
    
    # Run the failing tests
    try:
        test_basic_assertion()
    except AssertionError:
        pass
    
    try:
        test_with_setup()
    except AssertionError:
        pass
    
    try:
        test_list_operations()
    except AssertionError:
        pass
    
    # Run successful test
    test_success_example()
    
    # Generate report
    extractor = FailureExtractor()
    print(f"Captured {len(extractor.failures)} failures")
    
    if extractor.failures:
        # Generate JSON report
        config = OutputConfig("basic_failures.json", format="json")
        extractor.save_report(config)
        print("Generated basic_failures.json")
        
        # Generate Markdown report
        config = OutputConfig("basic_failures.md", format="markdown")
        extractor.save_report(config)
        print("Generated basic_failures.md")
        
        print("\nFailure summary:")
        for i, failure in enumerate(extractor.failures, 1):
            print(f"{i}. {failure['test_name']}: {failure['exception_message']}")
    else:
        print("No failures captured")