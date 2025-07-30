# Design Patterns in FailExtract

FailExtract employs several well-established design patterns to provide a robust, extensible, and maintainable architecture. This document explains the architectural decisions and their rationale.

## Pattern Overview

FailExtract uses four primary design patterns:

1. **Singleton Pattern** - For centralized failure collection
2. **Registry Pattern** - For formatter management and discovery
3. **Abstract Factory Pattern** - For output format creation
4. **Decorator Pattern** - For non-intrusive test instrumentation

## Singleton Pattern

### Usage: FailureExtractor Class

The `FailureExtractor` class implements the Singleton pattern to ensure a single, globally accessible instance for collecting test failures across the entire test session.

```python
class FailureExtractor:
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    # Initialize instance data
        return cls._instance
```

### Why Singleton?

**Benefits:**
- **Global State Management**: All test failures collected in one place
- **Memory Efficiency**: Single instance prevents memory fragmentation
- **Session Coordination**: Enables session-level reporting and statistics
- **Thread Safety**: Controlled access in concurrent environments

**Thread Safety Implementation:**
- **Double-Checked Locking**: Prevents race conditions during initialization
- **Data Locks**: Separate locks for data operations (`self._data_lock`)
- **Atomic Operations**: Thread-safe failure collection and reporting

```python
def add_failure(self, failure_data: Dict[str, Any]):
    with self._data_lock:  # Thread-safe data access
        self.failures.append(failure_data)
        # Memory limit enforcement
        if self._max_failures and len(self.failures) > self._max_failures:
            self.failures = self.failures[-self._max_failures:]
```

### Memory Management

The singleton includes built-in memory management to handle large test suites:

```python
def set_memory_limits(self, max_failures: Optional[int] = None, 
                     max_passed: Optional[int] = None):
    """Configure memory limits for failure collection."""
    with self._data_lock:
        self._max_failures = max_failures
        self._max_passed = max_passed
```

**FIFO Eviction**: When limits are exceeded, oldest entries are removed first, ensuring recent failures are always available.

## Registry Pattern

### Usage: FormatterRegistry Class

The `FormatterRegistry` implements the Registry pattern to manage output formatters and provide format discovery capabilities.

```python
class FormatterRegistry:
    _formatters: Dict[OutputFormat, OutputFormatter] = {
        OutputFormat.JSON: JSONFormatter(),
        OutputFormat.MARKDOWN: MarkdownFormatter(),
        # OutputFormat.HTML: HTMLFormatter(),  # Removed
        OutputFormat.XML: XMLFormatter(),
        OutputFormat.CSV: CSVFormatter(),
    }
    
    @classmethod
    def get_formatter(cls, format_type: OutputFormat) -> OutputFormatter:
        """Get formatter instance for specified format."""
        if format_type not in cls._formatters:
            raise ValueError(f"Unsupported format: {format_type}")
        return cls._formatters[format_type]
```

### Why Registry?

**Benefits:**
- **Extensibility**: Easy addition of new formatters
- **Loose Coupling**: Output logic separated from core functionality
- **Plugin Architecture**: Supports custom formatter registration
- **Format Discovery**: Automatic format detection and validation

**Extension Example:**
```python
# Custom formatter registration
class CustomFormatter(OutputFormatter):
    def format(self, failures, passed=None, metadata=None):
        return "Custom output format"

# Register new formatter
FormatterRegistry.register_formatter(OutputFormat.CUSTOM, CustomFormatter())
```

### Format Detection

The registry includes intelligent format detection:

```python
@classmethod
def detect_format_from_extension(cls, filename: str) -> OutputFormat:
    """Detect output format from file extension."""
    ext = Path(filename).suffix.lower()
    ext_map = {
        '.json': OutputFormat.JSON,
        # '.html': OutputFormat.HTML,  # Removed
        '.md': OutputFormat.MARKDOWN,
        '.xml': OutputFormat.XML,
        '.csv': OutputFormat.CSV,
    }
    return ext_map.get(ext, OutputFormat.JSON)
```

## Abstract Factory Pattern

### Usage: OutputFormatter Hierarchy

The `OutputFormatter` abstract base class defines the interface for all output formatters, implementing the Abstract Factory pattern.

```python
class OutputFormatter(ABC):
    """Abstract base class for output formatters."""
    
    @abstractmethod
    def format(self, failures: List[Dict[str, Any]], 
               passed: Optional[List[Dict[str, Any]]] = None,
               metadata: Optional[Dict[str, Any]] = None) -> str:
        """Format failure data into specific output format."""
        pass
```

### Concrete Implementations

Each output format implements the abstract interface:

```python
class JSONFormatter(OutputFormatter):
    def format(self, failures, passed=None, metadata=None):
        # JSON-specific formatting logic
        return json.dumps(data, indent=2)

# HTMLFormatter removed - use external tools like pandoc for HTML conversion
# class HTMLFormatter(OutputFormatter):
#     def format(self, failures, passed=None, metadata=None):
#         # HTML-specific formatting with templates
#         return self._generate_html(data)
```

### Why Abstract Factory?

**Benefits:**
- **Consistent Interface**: All formatters follow same contract
- **Polymorphism**: Format selection at runtime
- **Testability**: Easy mocking and testing of formatters
- **Maintainability**: Changes to one format don't affect others

**Factory Method Pattern:**
```python
def create_formatter(format_type: OutputFormat) -> OutputFormatter:
    """Factory method for creating formatters."""
    return FormatterRegistry.get_formatter(format_type)
```

## Decorator Pattern

### Usage: @extract_on_failure

The `extract_on_failure` decorator implements the Decorator pattern to add failure extraction capabilities to test functions without modifying their code.

```python
def extract_on_failure(func: Callable) -> Callable:
    """Decorator to extract failure information on test failure."""
    
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            result = func(*args, **kwargs)
            # Handle passed test if configured
            _handle_passed_test(func, args, kwargs)
            return result
        except Exception as e:
            # Extract failure information
            failure_info = extract_failure_info(func, e, args, kwargs)
            
            # Store in global extractor
            extractor = FailureExtractor()
            extractor.add_failure(failure_info)
            
            # Re-raise original exception
            raise
    
    return wrapper
```

### Why Decorator?

**Benefits:**
- **Non-Intrusive**: No modification of existing test code
- **Composable**: Can be combined with other decorators
- **Transparent**: Preserves original function behavior
- **Selective**: Apply only to tests that need instrumentation

**Composition Example:**
```python
@pytest.mark.parametrize("value", [1, 2, 3])
@extract_on_failure
def test_with_multiple_decorators(value):
    assert value > 0
```

### Function Preservation

The decorator preserves function metadata using `functools.wraps`:

```python
@functools.wraps(func)  # Preserves __name__, __doc__, etc.
def wrapper(*args, **kwargs):
    # Wrapper implementation
```

## Architectural Benefits

### Modularity

Each pattern addresses a specific concern:
- **Singleton**: Global state management
- **Registry**: Component discovery and management
- **Abstract Factory**: Output format abstraction
- **Decorator**: Non-intrusive instrumentation

### Extensibility

The architecture supports extension at multiple points:

```python
# 1. Custom formatters
class SlackFormatter(OutputFormatter):
    def format(self, failures, passed=None, metadata=None):
        return self._create_slack_blocks(failures)

# 2. Custom extractors
class CustomFixtureExtractor(FixtureExtractor):
    def _extract_fixture_chain(self, name, func, locals_dict, seen):
        # Custom extraction logic
        return super()._extract_fixture_chain(name, func, locals_dict, seen)

# 3. Configuration extensions
class CustomOutputConfig(OutputConfig):
    def __init__(self, *args, custom_option=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.custom_option = custom_option
```

### Performance Optimization

Design patterns enable performance optimizations:

**Singleton Benefits:**
- Single instance reduces memory overhead
- Shared cache across all operations
- Batch processing capabilities

**Registry Benefits:**
- Formatter instance reuse
- Lazy initialization of formatters
- Efficient format lookup

**Decorator Benefits:**
- Minimal overhead for successful tests
- Lazy failure extraction
- Selective instrumentation

### Testing and Maintenance

Patterns improve testability:

```python
# Mock formatters for testing
mock_formatter = Mock(spec=OutputFormatter)
FormatterRegistry._formatters[OutputFormat.JSON] = mock_formatter

# Test singleton behavior
extractor1 = FailureExtractor()
extractor2 = FailureExtractor()
assert extractor1 is extractor2

# Test decorator composition
@extract_on_failure
def test_function():
    pass
assert hasattr(test_function, '__wrapped__')
```

## Best Practices

### Using the Patterns

**Singleton Usage:**
- Always use `FailureExtractor()` constructor
- Don't directly access `_instance`
- Configure memory limits for large test suites

**Registry Usage:**
- Use `get_formatter()` method for format access
- Register custom formatters before first use
- Handle unsupported format exceptions

**Factory Usage:**
- Implement complete `OutputFormatter` interface
- Handle all parameter combinations
- Provide meaningful error messages

**Decorator Usage:**
- Apply to test functions, not helper functions
- Combine with other pytest decorators as needed
- Consider performance impact for large test suites

### Common Pitfalls

**Singleton Pitfalls:**
- Don't assume single-threaded access
- Always reset state between test sessions
- Handle memory limits appropriately

**Registry Pitfalls:**
- Register formatters before configuration
- Handle missing formatter exceptions
- Don't modify registry during iteration

**Factory Pitfalls:**
- Implement complete interface contract
- Handle edge cases (empty data, None values)
- Validate input parameters

**Decorator Pitfalls:**
- Don't suppress original exceptions
- Preserve function metadata with `functools.wraps`
- Handle both success and failure cases

This architecture provides a solid foundation for test failure analysis while maintaining flexibility for extension and customization.