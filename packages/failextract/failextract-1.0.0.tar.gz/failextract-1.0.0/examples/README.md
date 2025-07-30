# FailExtract Examples

This directory contains working examples demonstrating various usage patterns for FailExtract. All examples are tested and functional with the current codebase.

## 📁 Available Examples

### Basic Examples
- **[simple_decorator.py](basic/simple_decorator.py)** - Basic `@extract_on_failure` decorator usage
- **[multiple_formats.py](basic/multiple_formats.py)** - Generate reports in all supported formats
- **[basic_configuration.py](basic/basic_configuration.py)** - Configuration and setup examples

### Advanced Examples  
- **[custom_formatter.py](advanced/custom_formatter.py)** - Create custom output formatters

### Integration Examples
- **[pytest_conftest.py](integration/pytest_conftest.py)** - pytest integration setup

## 🚀 Quick Start

### 1. Basic Usage
Start with the simple decorator example:
```bash
cd examples/basic/
python simple_decorator.py
```

This will generate:
- `basic_failures.json` - JSON report
- `basic_failures.md` - Markdown report

### 2. Multiple Formats
See all supported output formats:
```bash
cd examples/basic/
python multiple_formats.py
```

Generates reports in JSON, Markdown, XML, CSV, and YAML formats.

### 3. Custom Formatters
Explore creating custom formatters:
```bash
cd examples/advanced/
python custom_formatter.py
```

## 📚 Example Details

### `simple_decorator.py`
**What it demonstrates:**
- Basic `@extract_on_failure` decorator usage
- Automatic failure context capture
- Report generation in JSON and Markdown formats

**Key concepts:**
- Decorator application
- Failure data structure
- Basic report generation

### `multiple_formats.py`  
**What it demonstrates:**
- All supported output formats (JSON, XML, CSV, YAML, Markdown)
- Format-specific configuration
- Batch report generation
- Error handling for format generation

**Output formats:**
- **JSON** - Machine-readable, always available (built-in)
- **XML** - Structured data format (built-in)
- **CSV** - Spreadsheet analysis (built-in)
- **Markdown** - Documentation-friendly format (built-in)
- **YAML** - Configuration-like format (requires `pip install failextract[formatters]`)

### `basic_configuration.py`
**What it demonstrates:**
- Configuration file usage
- Output customization
- Setting up workspace configurations

### `custom_formatter.py`
**What it demonstrates:**
- Creating custom output formatters
- Implementing the OutputFormatter interface
- Registering custom formatters
- Domain-specific output generation

### `pytest_conftest.py`
**What it demonstrates:**
- pytest integration setup
- Automatic failure capture in test suites
- Session-level reporting
- Hook-based integration

## 🔧 Running Examples

### Prerequisites
```bash
# Install FailExtract (Python 3.11+ required)
pip install failextract

# For YAML output support (optional)
pip install failextract[formatters]

# For all features (recommended for examples)
pip install failextract[all]
```

### Running Individual Examples
```bash
# Run a specific example
python examples/basic/simple_decorator.py

# Run from the example directory
cd examples/basic/
python multiple_formats.py
```

### pytest Integration
```bash
# Copy the conftest example to your project
cp examples/integration/pytest_conftest.py conftest.py

# Run tests with FailExtract integration
pytest --tb=short
```

## 📖 Learning Path

### Beginner (Start Here)
1. **[simple_decorator.py](basic/simple_decorator.py)** - Basic decorator usage
2. **[multiple_formats.py](basic/multiple_formats.py)** - Explore output formats  
3. **[basic_configuration.py](basic/basic_configuration.py)** - Configuration basics

### Intermediate
1. **[pytest_conftest.py](integration/pytest_conftest.py)** - pytest integration
2. **[custom_formatter.py](advanced/custom_formatter.py)** - Custom formatters

### Use Case Examples

#### Development Workflow
```python
# Add to individual tests during development
@extract_on_failure
def test_new_feature():
    # Your test code
    pass
```

#### CI/CD Pipeline  
```bash
# Generate reports after test runs
failextract report --format json --output ci-failures.json
failextract report --format markdown --output ci-failures.md
```

#### Documentation Generation
```python
# Generate failure documentation
from failextract import FailureExtractor, OutputConfig

extractor = FailureExtractor()
config = OutputConfig("test-failures.md", format="markdown")
extractor.save_report(config)
```

## 🔍 Expected Output

### After running simple_decorator.py:
```
Running basic decorator examples...
Captured 3 failures
Generated basic_failures.json  
Generated basic_failures.md

Failure summary:
1. test_basic_assertion: Expected 10 to be greater than 20
2. test_with_setup: User must be over 30
3. test_list_operations: Should have found numbers greater than 10
```

### After running multiple_formats.py:
```
Running multiple format example...
Generating reports for 3 failures...

✓ Generated failures.json - Machine-readable JSON format
✓ Generated failures.markdown - Markdown format for documentation  
✓ Generated failures.xml - XML format for structured data
✓ Generated failures.csv - CSV format for spreadsheet analysis
✓ Generated failures.yaml - YAML format for configuration-like output

Files created:
  - failures.json
  - failures.markdown
  - failures.xml
  - failures.csv
  - failures.yaml
```

## 🛠️ Supported Output Formats

| Format | Extension | Description | Availability |
|--------|-----------|-------------|--------------|
| JSON | `.json` | Machine-readable format | ✅ Built-in |
| XML | `.xml` | Structured data format | ✅ Built-in |
| CSV | `.csv` | Spreadsheet analysis | ✅ Built-in |
| Markdown | `.md` | Documentation format | ✅ Built-in |
| YAML | `.yaml` | Configuration-like format | 📦 `pip install failextract[formatters]` |

### Format Details

- **JSON**: Always available, perfect for API integration and machine processing
- **XML**: Structured format, great for enterprise systems and data exchange
- **CSV**: Tabular format, ideal for spreadsheet analysis and data visualization
- **Markdown**: Human-readable format, perfect for documentation and GitHub issues
- **YAML**: Clean, human-readable structured format, requires optional dependency

## 🤝 Contributing Examples

Want to add an example? Please:

1. **Test your example** - Ensure it runs without errors
2. **Follow naming conventions** - Use descriptive filenames
3. **Include docstrings** - Explain what the example demonstrates
4. **Update this README** - Add your example to the appropriate section
5. **Use working features** - Only use features that are implemented

### Example Template
```python
#!/usr/bin/env python3
"""
[Category] example: [Title]

Brief description of what this example demonstrates.
"""

from failextract import extract_on_failure, FailureExtractor, OutputConfig

# Your example code here

if __name__ == "__main__":
    print("[Example name] example")
    # Demonstration code
```

## 📞 Support

- **Documentation:** See main [README.md](../README.md) and `docs/` directory
- **Issues:** GitHub issues for bugs and questions
- **Examples Questions:** Tag with `examples` label
- **Python Version:** Requires Python 3.11 or later

## 🏆 Best Practices

### For Production Use
```python
# Use specific format configurations
config = OutputConfig(
    "production-failures.json",
    format="json",
    include_source=True,
    include_fixtures=True
)
```

### For Development
```python
# Quick debugging with markdown
@extract_on_failure
def test_debugging():
    # Your test code here
    pass
```

### For CI/CD
```bash
# Generate both machine-readable and human-readable reports
failextract report --format json --output ci-failures.json
failextract report --format markdown --output ci-failures.md
```

Happy testing with FailExtract! 🎉