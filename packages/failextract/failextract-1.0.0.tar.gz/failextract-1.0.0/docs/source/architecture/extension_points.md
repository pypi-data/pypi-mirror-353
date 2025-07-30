# Extension Points in FailExtract

FailExtract is designed for extensibility at multiple integration points. This document provides comprehensive guidance for extending and customizing functionality to meet specific requirements.

## Extension Philosophy

FailExtract follows the **Open/Closed Principle**: open for extension, closed for modification. You can extend functionality without modifying core library code, ensuring upgrade compatibility and maintainability.

### Core Extension Points

1. **Custom Output Formatters** - Add new output formats
2. **Custom Extraction Logic** - Modify failure data collection
3. **Configuration Extensions** - Add custom configuration options
4. **Hook System Integration** - Custom processing pipelines

## Custom Output Formatters

### OutputFormatter Interface

All formatters implement the `OutputFormatter` abstract base class:

```python
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional

class OutputFormatter(ABC):
    """Abstract base class for output formatters."""
    
    @abstractmethod
    def format(self, failures: List[Dict[str, Any]], 
               passed: Optional[List[Dict[str, Any]]] = None,
               metadata: Optional[Dict[str, Any]] = None) -> str:
        """Format failure data into specific output format.
        
        Args:
            failures: List of failure dictionaries
            passed: Optional list of passed test dictionaries
            metadata: Optional metadata about the test session
            
        Returns:
            Formatted string representation
        """
        pass
```

### Creating Custom Formatters

#### Example: Slack Notification Formatter

```python
import json
from datetime import datetime
from failextract import OutputFormatter

class SlackFormatter(OutputFormatter):
    """Custom formatter for Slack notifications."""
    
    def format(self, failures, passed=None, metadata=None):
        """Format failures as Slack message blocks."""
        
        if not failures:
            return self._create_success_message(passed, metadata)
        
        # Create header block
        total_tests = len(failures) + (len(passed) if passed else 0)
        header_text = f"🚨 Test Failures Report - {len(failures)} failures"
        
        blocks = [
            {
                "type": "header",
                "text": {"type": "plain_text", "text": header_text}
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*{len(failures)} failures* out of {total_tests} tests"
                }
            }
        ]
        
        # Add failure details (limit to prevent message size issues)
        for failure in failures[:5]:
            test_name = failure.get('test_name', 'Unknown test')
            error_msg = failure.get('exception_message', 'No error message')
            
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn", 
                    "text": f"*{test_name}*\nError: {error_msg[:100]}..."
                }
            })
        
        return json.dumps({"blocks": blocks}, indent=2)
    
    def _create_success_message(self, passed, metadata):
        """Create success message when no failures."""
        return json.dumps({
            "blocks": [{
                "type": "header",
                "text": {"type": "plain_text", "text": "✅ All Tests Passed!"}
            }]
        })
```

#### Example: JUnit XML Formatter

```python
from failextract import OutputFormatter

class JunitXMLFormatter(OutputFormatter):
    """Custom formatter for JUnit XML format."""
    
    def format(self, failures, passed=None, metadata=None):
        """Format failures as JUnit XML."""
        
        total_tests = len(failures) + (len(passed) if passed else 0)
        
        xml_lines = [
            '<?xml version="1.0" encoding="UTF-8"?>',
            f'<testsuite name="FailExtract" tests="{total_tests}" '
            f'failures="{len(failures)}" errors="0" time="0">'
        ]
        
        # Add failure test cases
        for failure in failures:
            test_name = failure.get('test_name', 'unknown_test')
            classname = failure.get('test_module', 'unknown_module')
            error_type = failure.get('exception_type', 'AssertionError')
            error_msg = failure.get('exception_message', 'No message')
            traceback = failure.get('exception_traceback', 'No traceback')
            
            xml_lines.extend([
                f'  <testcase classname="{classname}" name="{test_name}" time="0">',
                f'    <failure type="{error_type}" message="{self._escape_xml(error_msg)}">',
                f'      <![CDATA[{traceback}]]>',
                '    </failure>',
                '  </testcase>'
            ])
        
        # Add passed test cases
        if passed:
            for test in passed:
                test_name = test.get('test_name', 'unknown_test')
                classname = test.get('test_module', 'unknown_module')
                xml_lines.append(
                    f'  <testcase classname="{classname}" name="{test_name}" time="0"/>'
                )
        
        xml_lines.append('</testsuite>')
        return '\n'.join(xml_lines)
    
    def _escape_xml(self, text: str) -> str:
        """Escape XML special characters."""
        return (text.replace('&', '&amp;')
                   .replace('<', '&lt;')
                   .replace('>', '&gt;')
                   .replace('"', '&quot;')
                   .replace("'", '&#39;'))
```

### Formatter Registration

#### Dynamic Registration

```python
from failextract import FormatterRegistry, OutputFormat

# Register custom formatter
custom_formatter = SlackFormatter()
FormatterRegistry.register_formatter('slack', custom_formatter)

# Use registered formatter
extractor = FailureExtractor()
config = OutputConfig("failures.slack", format="slack")
extractor.save_report(config)
```

#### Extending OutputFormat Enum

For permanent format additions, extend the OutputFormat enum:

```python
from enum import Enum
from failextract import OutputFormat

class ExtendedOutputFormat(OutputFormat):
    """Extended output formats including custom formats."""
    SLACK = "slack"
    JUNIT = "junit"
    PROMETHEUS = "prometheus"
    TELEGRAM = "telegram"
```

### Advanced Formatter Features

#### Template-Based Formatters

```python
from string import Template
from failextract import OutputFormatter

class TemplateFormatter(OutputFormatter):
    """Formatter using customizable templates."""
    
    def __init__(self, template_string: str):
        self.template = Template(template_string)
    
    def format(self, failures, passed=None, metadata=None):
        """Format using template substitution."""
        
        context = {
            'failure_count': len(failures),
            'passed_count': len(passed) if passed else 0,
            'total_count': len(failures) + (len(passed) if passed else 0),
            'timestamp': datetime.now().isoformat(),
            'failures_summary': self._create_failures_summary(failures)
        }
        
        return self.template.substitute(context)
    
    def _create_failures_summary(self, failures):
        """Create formatted summary of failures."""
        summary_lines = []
        for i, failure in enumerate(failures, 1):
            test_name = failure.get('test_name', 'Unknown')
            error_msg = failure.get('exception_message', 'No message')
            summary_lines.append(f"{i}. {test_name}: {error_msg}")
        return '\n'.join(summary_lines)

# Usage
email_template = """
Test Results Summary
===================

Tests: $total_count
Passed: $passed_count  
Failed: $failure_count
Timestamp: $timestamp

Failures:
$failures_summary
"""

email_formatter = TemplateFormatter(email_template)
FormatterRegistry.register_formatter('email', email_formatter)
```

#### Multi-Format Composers

```python
from failextract import OutputFormatter

class MultiFormatComposer(OutputFormatter):
    """Composer that generates multiple formats simultaneously."""
    
    def __init__(self, formatters: Dict[str, OutputFormatter]):
        self.formatters = formatters
    
    def format(self, failures, passed=None, metadata=None):
        """Generate multiple formats and return as structured data."""
        
        results = {}
        for format_name, formatter in self.formatters.items():
            try:
                results[format_name] = formatter.format(failures, passed, metadata)
            except Exception as e:
                results[format_name] = f"Error generating {format_name}: {e}"
        
        return json.dumps(results, indent=2)

# Usage
composer = MultiFormatComposer({
    'slack': SlackFormatter(),
    'junit': JunitXMLFormatter(),
    'email': TemplateFormatter(email_template)
})
```

## Custom Extraction Logic

### FixtureExtractor Extension

The `FixtureExtractor` class can be extended to customize how test fixtures and context are extracted:

```python
from failextract import FixtureExtractor

class CustomFixtureExtractor(FixtureExtractor):
    """Custom fixture extractor with additional context."""
    
    def extract_fixture_info(self, test_func, test_locals):
        """Extract fixture information with custom logic."""
        
        # Call parent implementation
        base_info = super().extract_fixture_info(test_func, test_locals)
        
        # Add custom extraction logic
        custom_info = self._extract_custom_context(test_func, test_locals)
        
        # Merge results
        return {**base_info, **custom_info}
    
    def _extract_custom_context(self, test_func, test_locals):
        """Extract custom context information."""
        context = {}
        
        # Extract database connection info
        if 'db_session' in test_locals:
            context['database'] = {
                'url': str(test_locals['db_session'].bind.url),
                'transaction_active': test_locals['db_session'].in_transaction()
            }
        
        # Extract HTTP client info
        if 'client' in test_locals:
            context['http_client'] = {
                'base_url': getattr(test_locals['client'], 'base_url', None),
                'timeout': getattr(test_locals['client'], 'timeout', None)
            }
        
        # Extract environment variables
        context['environment'] = {
            'test_env': os.getenv('TEST_ENVIRONMENT', 'unknown'),
            'debug_mode': os.getenv('DEBUG', 'false').lower() == 'true'
        }
        
        return context
    
    def _extract_fixture_chain(self, name, func, locals_dict, seen):
        """Override fixture chain extraction with custom logic."""
        
        # Custom fixture detection
        if self._is_custom_fixture(name, locals_dict):
            return self._extract_custom_fixture(name, locals_dict)
        
        # Fall back to parent implementation
        return super()._extract_fixture_chain(name, func, locals_dict, seen)
    
    def _is_custom_fixture(self, name, locals_dict):
        """Detect if this is a custom fixture type."""
        value = locals_dict.get(name)
        return (hasattr(value, '__fixture_type__') or 
                isinstance(value, (DatabaseSession, HTTPClient)))
    
    def _extract_custom_fixture(self, name, locals_dict):
        """Extract custom fixture information."""
        value = locals_dict[name]
        
        if hasattr(value, '__fixture_type__'):
            return {
                'type': value.__fixture_type__,
                'value': str(value),
                'custom': True
            }
        
        return {'value': str(value), 'custom': True}
```

### AST Parsing Customization

Extend AST parsing for specialized source code analysis:

```python
import ast
from failextract import FailureExtractor

class AdvancedFailureExtractor(FailureExtractor):
    """Extended failure extractor with advanced AST analysis."""
    
    def _extract_source_context(self, traceback_obj):
        """Extract source code context with AST analysis."""
        
        base_context = super()._extract_source_context(traceback_obj)
        
        # Add AST-based analysis
        if base_context and 'source_code' in base_context:
            ast_analysis = self._analyze_source_ast(base_context['source_code'])
            base_context['ast_analysis'] = ast_analysis
        
        return base_context
    
    def _analyze_source_ast(self, source_code):
        """Perform AST analysis on source code."""
        try:
            tree = ast.parse(source_code)
            analyzer = SourceAnalyzer()
            analyzer.visit(tree)
            
            return {
                'function_calls': analyzer.function_calls,
                'variable_assignments': analyzer.assignments,
                'control_structures': analyzer.control_structures,
                'complexity_score': analyzer.complexity_score
            }
        except SyntaxError:
            return {'error': 'Could not parse source code'}

class SourceAnalyzer(ast.NodeVisitor):
    """AST visitor for source code analysis."""
    
    def __init__(self):
        self.function_calls = []
        self.assignments = []
        self.control_structures = []
        self.complexity_score = 0
    
    def visit_Call(self, node):
        """Visit function call nodes."""
        if isinstance(node.func, ast.Name):
            self.function_calls.append(node.func.id)
        elif isinstance(node.func, ast.Attribute):
            self.function_calls.append(f"{ast.unparse(node.func.value)}.{node.func.attr}")
        
        self.generic_visit(node)
    
    def visit_Assign(self, node):
        """Visit assignment nodes."""
        for target in node.targets:
            if isinstance(target, ast.Name):
                self.assignments.append(target.id)
        
        self.generic_visit(node)
    
    def visit_If(self, node):
        """Visit if statement nodes."""
        self.control_structures.append('if')
        self.complexity_score += 1
        self.generic_visit(node)
    
    def visit_For(self, node):
        """Visit for loop nodes."""
        self.control_structures.append('for')
        self.complexity_score += 1
        self.generic_visit(node)
    
    def visit_While(self, node):
        """Visit while loop nodes."""
        self.control_structures.append('while')
        self.complexity_score += 1
        self.generic_visit(node)
```

## Configuration Extensions

### Custom OutputConfig

Extend OutputConfig for specialized configuration needs:

```python
from failextract import OutputConfig

class AdvancedOutputConfig(OutputConfig):
    """Extended output configuration with advanced options."""
    
    def __init__(self, filename, format="json", **kwargs):
        super().__init__(filename, format)
        
        # Extended configuration options
        self.encryption_key = kwargs.get('encryption_key')
        self.compression_level = kwargs.get('compression_level', 6)
        self.include_source_code = kwargs.get('include_source_code', True)
        self.max_failure_details = kwargs.get('max_failure_details', 100)
        self.custom_metadata = kwargs.get('custom_metadata', {})
        
        # Validation
        self._validate_extended_config()
    
    def _validate_extended_config(self):
        """Validate extended configuration options."""
        if self.compression_level not in range(1, 10):
            raise ValueError("Compression level must be between 1 and 9")
        
        if self.max_failure_details < 1:
            raise ValueError("max_failure_details must be positive")
    
    def to_dict(self):
        """Convert configuration to dictionary including extensions."""
        base_dict = super().to_dict()
        base_dict.update({
            'compression_level': self.compression_level,
            'include_source_code': self.include_source_code,
            'max_failure_details': self.max_failure_details,
            'custom_metadata': self.custom_metadata
        })
        return base_dict
```

### Configuration Providers

Create custom configuration sources:

```python
import os
import json
from pathlib import Path
from failextract import OutputConfig

class ConfigurationProvider:
    """Base class for configuration providers."""
    
    def load_config(self, config_path: str) -> Dict[str, Any]:
        """Load configuration from source."""
        raise NotImplementedError

class FileConfigProvider(ConfigurationProvider):
    """Load configuration from JSON files."""
    
    def load_config(self, config_path: str) -> Dict[str, Any]:
        """Load configuration from JSON file."""
        path = Path(config_path)
        if not path.exists():
            raise FileNotFoundError(f"Config file not found: {config_path}")
        
        with open(path) as f:
            return json.load(f)

class EnvironmentConfigProvider(ConfigurationProvider):
    """Load configuration from environment variables."""
    
    def load_config(self, prefix: str = "FAILEXTRACT_") -> Dict[str, Any]:
        """Load configuration from environment variables."""
        config = {}
        
        for key, value in os.environ.items():
            if key.startswith(prefix):
                config_key = key[len(prefix):].lower()
                config[config_key] = self._parse_value(value)
        
        return config
    
    def _parse_value(self, value: str):
        """Parse string value to appropriate type."""
        # Try boolean
        if value.lower() in ('true', 'false'):
            return value.lower() == 'true'
        
        # Try integer
        try:
            return int(value)
        except ValueError:
            pass
        
        # Try float
        try:
            return float(value)
        except ValueError:
            pass
        
        # Return as string
        return value

class ConfigurationManager:
    """Manage configuration from multiple sources."""
    
    def __init__(self):
        self.providers = {}
    
    def register_provider(self, name: str, provider: ConfigurationProvider):
        """Register a configuration provider."""
        self.providers[name] = provider
    
    def load_configuration(self, sources: List[str]) -> OutputConfig:
        """Load and merge configuration from multiple sources."""
        merged_config = {}
        
        for source in sources:
            if source in self.providers:
                config = self.providers[source].load_config()
                merged_config.update(config)
        
        # Create OutputConfig with merged settings
        return AdvancedOutputConfig(**merged_config)

# Usage
config_manager = ConfigurationManager()
config_manager.register_provider('file', FileConfigProvider())
config_manager.register_provider('env', EnvironmentConfigProvider())

config = config_manager.load_configuration(['file:config.json', 'env'])
```

## Hook System Integration

### Custom Processing Hooks

FailExtract supports hooks for custom processing pipelines:

```python
from failextract import FailureExtractor

class ProcessingHooks:
    """Custom processing hooks for failure extraction."""
    
    @staticmethod
    def pre_extraction_hook(test_func, exception, locals_dict):
        """Called before failure extraction."""
        print(f"Processing failure in {test_func.__name__}")
        
        # Custom pre-processing
        if hasattr(test_func, '__test_category__'):
            locals_dict['_test_category'] = test_func.__test_category__
        
        return locals_dict
    
    @staticmethod
    def post_extraction_hook(failure_data):
        """Called after failure extraction."""
        
        # Add custom metadata
        failure_data['processing_timestamp'] = datetime.now().isoformat()
        failure_data['hostname'] = socket.gethostname()
        
        # Custom enrichment
        if 'test_category' in failure_data:
            failure_data['category_metadata'] = {
                'critical': failure_data['test_category'] in ['security', 'data_integrity'],
                'notification_level': 'urgent' if failure_data['test_category'] == 'security' else 'normal'
            }
        
        return failure_data
    
    @staticmethod
    def filtering_hook(failure_data):
        """Filter failures based on custom criteria."""
        
        # Skip certain types of failures
        if failure_data.get('exception_type') == 'SkipTest':
            return False
        
        # Skip non-critical test categories in development
        if os.getenv('ENVIRONMENT') == 'development':
            if failure_data.get('test_category') == 'integration':
                return False
        
        return True
    
    @staticmethod
    def aggregation_hook(all_failures):
        """Process all failures after collection."""
        
        # Group failures by category
        categorized = {}
        for failure in all_failures:
            category = failure.get('test_category', 'unknown')
            if category not in categorized:
                categorized[category] = []
            categorized[category].append(failure)
        
        # Add summary metadata
        summary = {
            'total_failures': len(all_failures),
            'categories': {cat: len(failures) for cat, failures in categorized.items()},
            'critical_count': len([f for f in all_failures if f.get('category_metadata', {}).get('critical')])
        }
        
        return all_failures, summary

# Register hooks with extractor
extractor = FailureExtractor()
extractor.register_hook('pre_extraction', ProcessingHooks.pre_extraction_hook)
extractor.register_hook('post_extraction', ProcessingHooks.post_extraction_hook)
extractor.register_hook('filtering', ProcessingHooks.filtering_hook)
extractor.register_hook('aggregation', ProcessingHooks.aggregation_hook)
```

### Integration with External Systems

#### Slack Integration Hook

```python
import requests
from failextract import FailureExtractor

class SlackIntegration:
    """Integration hooks for Slack notifications."""
    
    def __init__(self, webhook_url: str, channel: str = "#test-failures"):
        self.webhook_url = webhook_url
        self.channel = channel
    
    def failure_notification_hook(self, failure_data):
        """Send immediate notification for critical failures."""
        
        if failure_data.get('category_metadata', {}).get('critical'):
            self._send_slack_message(
                f"🚨 Critical test failure in {failure_data['test_name']}: "
                f"{failure_data['exception_message']}"
            )
        
        return failure_data
    
    def session_summary_hook(self, all_failures, summary):
        """Send session summary to Slack."""
        
        if all_failures:
            message = (f"Test session completed with {summary['total_failures']} failures:\n"
                      f"Critical: {summary['critical_count']}\n"
                      f"Categories: {', '.join(f'{cat}: {count}' for cat, count in summary['categories'].items())}")
            
            self._send_slack_message(message)
        
        return all_failures, summary
    
    def _send_slack_message(self, message: str):
        """Send message to Slack."""
        payload = {
            "channel": self.channel,
            "text": message,
            "username": "FailExtract Bot"
        }
        
        try:
            response = requests.post(self.webhook_url, json=payload)
            response.raise_for_status()
        except requests.RequestException as e:
            print(f"Failed to send Slack notification: {e}")

# Usage
slack = SlackIntegration("https://hooks.slack.com/services/YOUR/WEBHOOK/URL")
extractor = FailureExtractor()
extractor.register_hook('post_extraction', slack.failure_notification_hook)
extractor.register_hook('session_end', slack.session_summary_hook)
```

## Testing Extensions

### Testing Custom Formatters

```python
import pytest
from failextract import OutputFormatter

class TestCustomFormatter:
    """Test suite for custom formatters."""
    
    @pytest.fixture
    def sample_failure_data(self):
        """Sample failure data for testing."""
        return [{
            'test_name': 'test_example',
            'test_module': 'test_module',
            'exception_type': 'AssertionError',
            'exception_message': 'Test assertion failed',
            'exception_traceback': 'Traceback line 1\nTraceback line 2'
        }]
    
    @pytest.fixture
    def sample_passed_data(self):
        """Sample passed test data."""
        return [{
            'test_name': 'test_passing',
            'test_module': 'test_module'
        }]
    
    def test_slack_formatter_with_failures(self, sample_failure_data, sample_passed_data):
        """Test Slack formatter with failure data."""
        formatter = SlackFormatter()
        result = formatter.format(sample_failure_data, sample_passed_data)
        
        # Verify result structure
        assert isinstance(result, str)
        
        # Parse JSON result
        import json
        data = json.loads(result)
        assert 'blocks' in data
        assert len(data['blocks']) >= 2  # Header + summary at minimum
        
        # Verify content
        header_block = data['blocks'][0]
        assert header_block['type'] == 'header'
        assert '🚨' in header_block['text']['text']
    
    def test_junit_formatter_structure(self, sample_failure_data, sample_passed_data):
        """Test JUnit XML formatter structure."""
        formatter = JunitXMLFormatter()
        result = formatter.format(sample_failure_data, sample_passed_data)
        
        # Verify XML structure
        assert result.startswith('<?xml version="1.0"')
        assert '<testsuite' in result
        assert '<testcase' in result
        assert '<failure' in result
        assert '</testsuite>' in result
    
    def test_template_formatter_substitution(self):
        """Test template-based formatter."""
        template = "Failures: $failure_count, Passed: $passed_count"
        formatter = TemplateFormatter(template)
        
        result = formatter.format([{'test': 'data'}], [{'test': 'passed'}])
        assert "Failures: 1, Passed: 1" in result
```

### Performance Testing Extensions

```python
import time
import pytest
from failextract import FailureExtractor

class TestExtensionPerformance:
    """Performance tests for extensions."""
    
    def test_custom_extractor_performance(self):
        """Test custom extractor performance."""
        extractor = CustomFixtureExtractor()
        
        start_time = time.time()
        
        # Simulate large number of extractions
        for i in range(1000):
            extractor.extract_fixture_info(lambda: None, {'test_data': f'data_{i}'})
        
        duration = time.time() - start_time
        
        # Performance assertion (adjust threshold as needed)
        assert duration < 1.0, f"Custom extraction too slow: {duration:.3f}s"
    
    def test_custom_formatter_memory_usage(self, sample_large_dataset):
        """Test memory usage of custom formatters."""
        import tracemalloc
        
        formatter = SlackFormatter()
        
        tracemalloc.start()
        result = formatter.format(sample_large_dataset)
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        
        # Memory usage assertion (adjust threshold as needed)
        assert peak < 10 * 1024 * 1024, f"Formatter used too much memory: {peak} bytes"
```

## Best Practices for Extensions

### Design Guidelines

1. **Interface Compliance**: Always implement complete interfaces
2. **Error Handling**: Gracefully handle edge cases and invalid inputs
3. **Performance**: Consider memory usage and execution time
4. **Documentation**: Provide comprehensive docstrings and examples
5. **Testing**: Include unit tests and integration tests
6. **Backward Compatibility**: Maintain compatibility with existing APIs

### Common Pitfalls

1. **Incomplete Interface Implementation**: Failing to implement all abstract methods
2. **State Mutation**: Modifying shared state without proper synchronization
3. **Resource Leaks**: Not properly cleaning up resources (files, connections)
4. **Exception Suppression**: Catching and ignoring exceptions without logging
5. **Circular Dependencies**: Creating circular imports between modules

### Extension Checklist

- [ ] Interface fully implemented
- [ ] Error handling for edge cases
- [ ] Unit tests with >90% coverage
- [ ] Performance benchmarks
- [ ] Documentation with examples
- [ ] Integration tests
- [ ] Memory usage validated
- [ ] Thread safety considered
- [ ] Backward compatibility maintained
- [ ] Code review completed

## Advanced Extension Patterns

### Plugin Architecture

```python
import importlib
from typing import Dict, Type

class PluginManager:
    """Manage dynamic plugin loading and registration."""
    
    def __init__(self):
        self.formatters: Dict[str, Type[OutputFormatter]] = {}
        self.extractors: Dict[str, Type[FixtureExtractor]] = {}
    
    def register_formatter_plugin(self, name: str, formatter_class: Type[OutputFormatter]):
        """Register a formatter plugin."""
        if not issubclass(formatter_class, OutputFormatter):
            raise TypeError(f"{formatter_class} must inherit from OutputFormatter")
        
        self.formatters[name] = formatter_class
    
    def register_extractor_plugin(self, name: str, extractor_class: Type[FixtureExtractor]):
        """Register an extractor plugin."""
        if not issubclass(extractor_class, FixtureExtractor):
            raise TypeError(f"{extractor_class} must inherit from FixtureExtractor")
        
        self.extractors[name] = extractor_class
    
    def load_plugins_from_directory(self, plugin_dir: str):
        """Load plugins from a directory."""
        import sys
        from pathlib import Path
        
        plugin_path = Path(plugin_dir)
        if not plugin_path.exists():
            return
        
        sys.path.insert(0, str(plugin_path))
        
        for plugin_file in plugin_path.glob("*.py"):
            if plugin_file.name.startswith("_"):
                continue
            
            module_name = plugin_file.stem
            try:
                module = importlib.import_module(module_name)
                
                # Auto-discover and register plugins
                self._discover_plugins(module)
                
            except ImportError as e:
                print(f"Failed to load plugin {module_name}: {e}")
        
        sys.path.pop(0)
    
    def _discover_plugins(self, module):
        """Discover plugins in a module."""
        for name in dir(module):
            obj = getattr(module, name)
            
            if (isinstance(obj, type) and 
                issubclass(obj, OutputFormatter) and 
                obj != OutputFormatter):
                
                plugin_name = name.lower().replace('formatter', '')
                self.register_formatter_plugin(plugin_name, obj)
            
            elif (isinstance(obj, type) and 
                  issubclass(obj, FixtureExtractor) and 
                  obj != FixtureExtractor):
                
                plugin_name = name.lower().replace('extractor', '')
                self.register_extractor_plugin(plugin_name, obj)

# Global plugin manager instance
plugin_manager = PluginManager()

# Usage
plugin_manager.load_plugins_from_directory("./plugins")
slack_formatter = plugin_manager.formatters['slack']()
```

This extension architecture provides powerful customization capabilities while maintaining clean separation of concerns and ensuring maintainability. Extensions can be developed independently and integrated seamlessly with the core FailExtract functionality.