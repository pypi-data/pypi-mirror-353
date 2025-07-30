"""Configuration management system for FailExtract.

This module implements a comprehensive configuration system supporting:
- Project-level configuration files (TOML, YAML)
- Workspace detection (git, Python packages, explicit markers)
- Settings inheritance hierarchy (global → user → workspace → CLI → env)
- Schema validation and error handling
- Integration with existing OutputConfig system

The system follows modern Python configuration patterns and provides
backward compatibility with existing FailExtract functionality.
"""

import os
import warnings
from pathlib import Path
from typing import Dict, Any, Optional, List, Union, NamedTuple
from dataclasses import dataclass, field, asdict
from enum import Enum

try:
    import tomllib  # Python 3.11+
except ImportError:
    try:
        import tomli as tomllib  # Fallback for older Python
    except ImportError:
        tomllib = None

import yaml


class ConfigurationError(Exception):
    """Raised when configuration is invalid or cannot be loaded."""
    pass


class ValidationResult(NamedTuple):
    """Result of configuration validation."""
    is_valid: bool
    errors: List[str]
    warnings: List[str]


@dataclass
class FieldSchema:
    """Schema definition for a configuration field."""
    name: str
    type: type
    default: Any = None
    required: bool = False
    validator: Optional[callable] = None
    description: str = ""


@dataclass
class SectionSchema:
    """Schema definition for a configuration section."""
    name: str
    fields: Dict[str, FieldSchema] = field(default_factory=dict)
    description: str = ""
    
    def add_field(self, field_schema: FieldSchema) -> None:
        """Add a field to this section."""
        self.fields[field_schema.name] = field_schema


class ConfigurationSchema:
    """Defines and validates the configuration schema for FailExtract."""
    
    def __init__(self):
        """Initialize the configuration schema with all sections and fields."""
        self.sections: Dict[str, SectionSchema] = {}
        self._define_schema()
    
    def _define_schema(self) -> None:
        """Define the complete configuration schema."""
        # Output configuration section
        output_section = SectionSchema(
            name="output",
            description="Output formatting and file configuration"
        )
        output_section.add_field(FieldSchema(
            name="default_format",
            type=str,
            default="json",
            validator=self._validate_output_format,
            description="Default output format for reports"
        ))
        output_section.add_field(FieldSchema(
            name="default_filename",
            type=str,
            default=None,
            description="Default filename for reports"
        ))
        output_section.add_field(FieldSchema(
            name="append",
            type=bool,
            default=False,
            description="Whether to append to existing files"
        ))
        output_section.add_field(FieldSchema(
            name="include_passed",
            type=bool,
            default=False,
            description="Whether to include passed tests in reports"
        ))
        output_section.add_field(FieldSchema(
            name="max_failures",
            type=int,
            default=None,
            validator=self._validate_positive_int,
            description="Maximum number of failures to capture"
        ))
        self.sections["output"] = output_section
        
        # Workspace configuration section
        workspace_section = SectionSchema(
            name="workspace",
            description="Workspace detection and management"
        )
        workspace_section.add_field(FieldSchema(
            name="root_path",
            type=str,
            default=None,
            description="Explicit workspace root path"
        ))
        workspace_section.add_field(FieldSchema(
            name="detection_strategy",
            type=str,
            default="auto",
            validator=self._validate_detection_strategy,
            description="Workspace detection strategy"
        ))
        workspace_section.add_field(FieldSchema(
            name="ignore_patterns",
            type=list,
            default=lambda: ["__pycache__", "*.pyc", ".pytest_cache"],
            description="Patterns to ignore in workspace"
        ))
        workspace_section.add_field(FieldSchema(
            name="include_patterns",
            type=list,
            default=lambda: ["*.py"],
            description="Patterns to include in workspace analysis"
        ))
        workspace_section.add_field(FieldSchema(
            name="max_depth",
            type=int,
            default=10,
            validator=self._validate_positive_int,
            description="Maximum depth for workspace traversal"
        ))
        self.sections["workspace"] = workspace_section
        
        # Extraction configuration section
        extraction_section = SectionSchema(
            name="extraction",
            description="Test failure extraction behavior"
        )
        extraction_section.add_field(FieldSchema(
            name="include_locals",
            type=bool,
            default=True,
            description="Whether to include local variables"
        ))
        extraction_section.add_field(FieldSchema(
            name="include_fixtures",
            type=bool,
            default=True,
            description="Whether to include fixture information"
        ))
        extraction_section.add_field(FieldSchema(
            name="max_depth",
            type=int,
            default=10,
            validator=self._validate_positive_int,
            description="Maximum depth for extraction"
        ))
        extraction_section.add_field(FieldSchema(
            name="skip_stdlib",
            type=bool,
            default=True,
            description="Whether to skip standard library code"
        ))
        extraction_section.add_field(FieldSchema(
            name="extract_classes",
            type=bool,
            default=True,
            description="Whether to extract class information"
        ))
        extraction_section.add_field(FieldSchema(
            name="context_lines",
            type=int,
            default=5,
            validator=self._validate_non_negative_int,
            description="Number of context lines around failure"
        ))
        self.sections["extraction"] = extraction_section
        
        # Formatting configuration section
        formatting_section = SectionSchema(
            name="formatting",
            description="Output formatting configuration"
        )
        formatting_section.add_field(FieldSchema(
            name="indent_size",
            type=int,
            default=2,
            validator=self._validate_positive_int,
            description="Indentation size for formatted output"
        ))
        formatting_section.add_field(FieldSchema(
            name="max_line_length",
            type=int,
            default=88,
            validator=self._validate_positive_int,
            description="Maximum line length for formatted output"
        ))
        formatting_section.add_field(FieldSchema(
            name="sort_keys",
            type=bool,
            default=True,
            description="Whether to sort keys in output"
        ))
        self.sections["formatting"] = formatting_section
        
        # Memory configuration section
        memory_section = SectionSchema(
            name="memory",
            description="Memory management configuration"
        )
        memory_section.add_field(FieldSchema(
            name="max_failures",
            type=int,
            default=1000,
            validator=self._validate_positive_int,
            description="Maximum failures to keep in memory"
        ))
        memory_section.add_field(FieldSchema(
            name="max_passed",
            type=int,
            default=1000,
            validator=self._validate_positive_int,
            description="Maximum passed tests to keep in memory"
        ))
        memory_section.add_field(FieldSchema(
            name="cleanup_threshold",
            type=float,
            default=0.8,
            validator=self._validate_percentage,
            description="Memory cleanup threshold (0.0-1.0)"
        ))
        self.sections["memory"] = memory_section
    
    def get_section(self, name: str) -> SectionSchema:
        """Get a section schema by name."""
        if name not in self.sections:
            raise ConfigurationError(f"Unknown configuration section: {name}")
        return self.sections[name]
    
    def validate(self, config: Dict[str, Any]) -> ValidationResult:
        """Validate a configuration dictionary against the schema."""
        errors = []
        warnings = []
        
        # Validate each section
        for section_name, section_data in config.items():
            if section_name not in self.sections:
                warnings.append(f"Unknown configuration section: {section_name}")
                continue
                
            section_schema = self.sections[section_name]
            section_errors = self._validate_section(section_schema, section_data)
            errors.extend(section_errors)
        
        # Check for unknown fields within known sections
        for section_name in config:
            if section_name in self.sections:
                section_data = config[section_name]
                section_schema = self.sections[section_name]
                for field_name in section_data:
                    if field_name not in section_schema.fields:
                        warnings.append(
                            f"Unknown field '{field_name}' in section '{section_name}'"
                        )
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings
        )
    
    def _validate_section(self, section_schema: SectionSchema, section_data: Dict[str, Any]) -> List[str]:
        """Validate a single section against its schema."""
        errors = []
        
        if not isinstance(section_data, dict):
            errors.append(f"Section '{section_schema.name}' must be a dictionary")
            return errors
        
        # Validate each field
        for field_name, field_schema in section_schema.fields.items():
            if field_name in section_data:
                value = section_data[field_name]
                field_errors = self._validate_field(field_schema, value)
                errors.extend(field_errors)
            elif field_schema.required:
                errors.append(
                    f"Required field '{field_name}' missing from section '{section_schema.name}'"
                )
        
        return errors
    
    def _validate_field(self, field_schema: FieldSchema, value: Any) -> List[str]:
        """Validate a single field against its schema."""
        errors = []
        
        # Type validation
        if field_schema.type is not type(None) and value is not None:
            if not isinstance(value, field_schema.type):
                errors.append(
                    f"Field '{field_schema.name}' must be of type {field_schema.type.__name__}, "
                    f"got {type(value).__name__}"
                )
                return errors  # Don't continue if type is wrong
        
        # Custom validator
        if field_schema.validator and value is not None:
            try:
                field_schema.validator(value)
            except ValueError as e:
                errors.append(f"Field '{field_schema.name}': {str(e)}")
        
        return errors
    
    # Validation helper methods
    def _validate_output_format(self, value: str) -> None:
        """Validate output format value."""
        valid_formats = ["json", "yaml", "markdown", "xml", "csv"]
        if value not in valid_formats:
            raise ValueError(f"Invalid format '{value}'. Valid formats: {valid_formats}")
    
    def _validate_detection_strategy(self, value: str) -> None:
        """Validate workspace detection strategy."""
        valid_strategies = ["auto", "git", "python_package", "explicit_marker", "custom"]
        if value not in valid_strategies:
            raise ValueError(f"Invalid detection strategy '{value}'. Valid strategies: {valid_strategies}")
    
    def _validate_positive_int(self, value: int) -> None:
        """Validate that integer is positive."""
        if value <= 0:
            raise ValueError("Value must be positive")
    
    def _validate_non_negative_int(self, value: int) -> None:
        """Validate that integer is non-negative."""
        if value < 0:
            raise ValueError("Value must be non-negative")
    
    def _validate_percentage(self, value: float) -> None:
        """Validate that float is between 0.0 and 1.0."""
        if not 0.0 <= value <= 1.0:
            raise ValueError("Value must be between 0.0 and 1.0")


@dataclass
class OutputSection:
    """Output configuration section."""
    default_format: str = "json"
    default_filename: Optional[str] = None
    append: bool = False
    include_passed: bool = False
    max_failures: Optional[int] = None


@dataclass
class WorkspaceSection:
    """Workspace configuration section."""
    root_path: Optional[str] = None
    detection_strategy: str = "auto"
    ignore_patterns: List[str] = field(default_factory=lambda: ["__pycache__", "*.pyc", ".pytest_cache"])
    include_patterns: List[str] = field(default_factory=lambda: ["*.py"])
    max_depth: int = 10


@dataclass
class ExtractionSection:
    """Extraction configuration section."""
    include_locals: bool = True
    include_fixtures: bool = True
    max_depth: int = 10
    skip_stdlib: bool = True
    extract_classes: bool = True
    context_lines: int = 5


@dataclass
class FormattingSection:
    """Formatting configuration section."""
    indent_size: int = 2
    max_line_length: int = 88
    sort_keys: bool = True


@dataclass
class MemorySection:
    """Memory configuration section."""
    max_failures: int = 1000
    max_passed: int = 1000
    cleanup_threshold: float = 0.8


class ProjectConfig:
    """Main project configuration class containing all sections."""
    
    def __init__(self, config_data: Optional[Dict[str, Any]] = None):
        """Initialize project configuration.
        
        Args:
            config_data: Dictionary containing configuration data
            
        Raises:
            ConfigurationError: If configuration is invalid
        """
        self.schema = ConfigurationSchema()
        
        # Initialize sections with defaults
        self.output = OutputSection()
        self.workspace = WorkspaceSection()
        self.extraction = ExtractionSection()
        self.formatting = FormattingSection()
        self.memory = MemorySection()
        
        # Load provided configuration
        if config_data:
            self._load_from_dict(config_data)
    
    def _load_from_dict(self, config_data: Dict[str, Any]) -> None:
        """Load configuration from dictionary."""
        # Validate configuration
        validation_result = self.schema.validate(config_data)
        if not validation_result.is_valid:
            error_msg = "Configuration validation failed:\n" + "\n".join(validation_result.errors)
            raise ConfigurationError(error_msg)
        
        # Show warnings
        for warning in validation_result.warnings:
            warnings.warn(f"Configuration warning: {warning}", UserWarning)
        
        # Load sections
        for section_name, section_data in config_data.items():
            if section_name == "output":
                self.output = self._load_section(OutputSection, section_data)
            elif section_name == "workspace":
                self.workspace = self._load_section(WorkspaceSection, section_data)
            elif section_name == "extraction":
                self.extraction = self._load_section(ExtractionSection, section_data)
            elif section_name == "formatting":
                self.formatting = self._load_section(FormattingSection, section_data)
            elif section_name == "memory":
                self.memory = self._load_section(MemorySection, section_data)
    
    def _load_section(self, section_class, section_data: Dict[str, Any]):
        """Load a specific section from data."""
        # Get current section instance
        current_section = getattr(self, section_class.__name__.lower().replace('section', ''))
        
        # Update with new data
        section_dict = asdict(current_section)
        section_dict.update(section_data)
        
        return section_class(**section_dict)
    
    def merge(self, other_config: Dict[str, Any]) -> None:
        """Merge another configuration into this one.
        
        Args:
            other_config: Configuration data to merge in
        """
        # Validate the other configuration
        validation_result = self.schema.validate(other_config)
        if not validation_result.is_valid:
            error_msg = "Cannot merge invalid configuration:\n" + "\n".join(validation_result.errors)
            raise ConfigurationError(error_msg)
        
        # Merge each section
        for section_name, section_data in other_config.items():
            if hasattr(self, section_name):
                current_section = getattr(self, section_name)
                section_dict = asdict(current_section)
                
                # Only update with valid fields for the section
                if section_name in self.schema.sections:
                    section_schema = self.schema.sections[section_name]
                    valid_fields = {k: v for k, v in section_data.items() 
                                  if k in section_schema.fields}
                    section_dict.update(valid_fields)
                else:
                    section_dict.update(section_data)
                
                # Get the appropriate section class
                section_class = type(current_section)
                setattr(self, section_name, section_class(**section_dict))
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return {
            "output": asdict(self.output),
            "workspace": asdict(self.workspace),
            "extraction": asdict(self.extraction),
            "formatting": asdict(self.formatting),
            "memory": asdict(self.memory),
        }
    
    def get_output_config(self, filename: Optional[str] = None, **kwargs) -> 'OutputConfig':
        """Create an OutputConfig instance with project defaults.
        
        Args:
            filename: Output filename (overrides project default)
            **kwargs: Additional OutputConfig parameters
            
        Returns:
            OutputConfig instance with project defaults applied
        """
        # Import here to avoid circular imports
        from .failextract import OutputConfig, OutputFormat
        
        # Use project defaults as base
        config_kwargs = {
            'append': self.output.append,
            'include_passed': self.output.include_passed,
            'max_failures': self.output.max_failures,
        }
        
        # Override with explicit kwargs
        config_kwargs.update(kwargs)
        
        # Determine output parameter
        output_param = filename or self.output.default_filename
        if output_param is None and 'output' not in config_kwargs:
            # Use default format if no filename specified
            format_str = config_kwargs.get('format', self.output.default_format)
            if isinstance(format_str, str):
                # Convert string to OutputFormat for default filename
                try:
                    output_format = OutputFormat(format_str)
                    output_param = output_format
                except ValueError:
                    # Fallback to JSON if invalid format
                    output_param = OutputFormat.JSON
        
        if output_param is not None:
            config_kwargs['output'] = output_param
        
        # Set default format only if not specified and no filename to detect from
        if 'format' not in config_kwargs and output_param is None:
            config_kwargs['format'] = self.output.default_format
        
        return OutputConfig(**config_kwargs)


class WorkspaceDetector:
    """Detects workspace root directories using various strategies."""
    
    def __init__(self, max_depth: int = 10, custom_markers: Optional[List[str]] = None,
                 custom_patterns: Optional[List[str]] = None):
        """Initialize workspace detector.
        
        Args:
            max_depth: Maximum depth to search upward
            custom_markers: Custom marker files to look for
            custom_patterns: Custom patterns to match
        """
        self.max_depth = max_depth
        self.custom_markers = custom_markers or []
        self.custom_patterns = custom_patterns or []
        self.detection_method: Optional[str] = None
    
    def detect_workspace(self, start_path: Union[str, Path]) -> Optional[Path]:
        """Detect workspace root starting from given path.
        
        Args:
            start_path: Path to start detection from
            
        Returns:
            Path to workspace root, or None if not found
        """
        start_path = Path(start_path).resolve()
        
        # Try different detection strategies in priority order
        strategies = [
            ('explicit_marker', self._detect_explicit_marker),
            ('custom_pattern', self._detect_custom_pattern),
            ('git', self._detect_git_repository),
            ('python_package', self._detect_python_package),
        ]
        
        for strategy_name, strategy_func in strategies:
            workspace_root = strategy_func(start_path)
            if workspace_root:
                self.detection_method = strategy_name
                return workspace_root
        
        self.detection_method = None
        return None
    
    def _detect_explicit_marker(self, start_path: Path) -> Optional[Path]:
        """Detect workspace using explicit marker file."""
        marker_files = ['.failextract-workspace', '.failextract']
        
        current = start_path
        for _ in range(self.max_depth):
            for marker in marker_files:
                if (current / marker).exists():
                    return current
            
            parent = current.parent
            if parent == current:  # Reached root
                break
            current = parent
        
        return None
    
    def _detect_custom_pattern(self, start_path: Path) -> Optional[Path]:
        """Detect workspace using custom patterns."""
        if not self.custom_markers and not self.custom_patterns:
            return None
        
        current = start_path
        for _ in range(self.max_depth):
            # Check custom marker files
            for marker in self.custom_markers:
                if (current / marker).exists():
                    return current
            
            # Check custom patterns
            for pattern in self.custom_patterns:
                if list(current.glob(pattern)):
                    return current
            
            parent = current.parent
            if parent == current:
                break
            current = parent
        
        return None
    
    def _detect_git_repository(self, start_path: Path) -> Optional[Path]:
        """Detect workspace using git repository."""
        current = start_path
        for _ in range(self.max_depth):
            git_dir = current / '.git'
            if git_dir.exists() and (git_dir.is_dir() or git_dir.is_file()):
                return current
            
            parent = current.parent
            if parent == current:
                break
            current = parent
        
        return None
    
    def _detect_python_package(self, start_path: Path) -> Optional[Path]:
        """Detect workspace using Python package indicators."""
        package_indicators = [
            'pyproject.toml',
            'setup.py',
            'setup.cfg',
            'requirements.txt',
            'Pipfile',
            'poetry.lock',
        ]
        
        current = start_path
        for _ in range(self.max_depth):
            for indicator in package_indicators:
                if (current / indicator).exists():
                    return current
            
            parent = current.parent
            if parent == current:
                break
            current = parent
        
        return None


class ConfigurationManager:
    """Main configuration manager that handles loading and merging configurations."""
    
    def __init__(self):
        """Initialize configuration manager with default configuration."""
        self.config = ProjectConfig()
        self.workspace_root: Optional[Path] = None
        self._config_sources: List[str] = []
    
    def load_from_file(self, file_path: Union[str, Path]) -> None:
        """Load configuration from a file.
        
        Args:
            file_path: Path to configuration file
            
        Raises:
            ConfigurationError: If file cannot be parsed
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            return  # Silently ignore missing files
        
        try:
            if file_path.suffix.lower() in ['.toml']:
                config_data = self._load_toml_file(file_path)
            elif file_path.suffix.lower() in ['.yaml', '.yml']:
                config_data = self._load_yaml_file(file_path)
            else:
                raise ConfigurationError(f"Unsupported configuration file format: {file_path.suffix}")
            
            if config_data:
                self.merge_configuration(config_data)
                self._config_sources.append(str(file_path))
                
        except Exception as e:
            if isinstance(e, ConfigurationError):
                raise
            raise ConfigurationError(f"Failed to parse configuration file {file_path}: {e}")
    
    def load_from_pyproject_toml(self, file_path: Union[str, Path]) -> None:
        """Load configuration from pyproject.toml file.
        
        Args:
            file_path: Path to pyproject.toml file
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            return
        
        try:
            # Load the raw TOML data without extracting sections
            if tomllib is None:
                raise ConfigurationError("TOML support not available. Install tomli for Python < 3.11")
            
            with open(file_path, 'rb') as f:
                data = tomllib.load(f)
            
            # Extract failextract configuration from tool section
            if 'tool' in data and 'failextract' in data['tool']:
                failextract_config = data['tool']['failextract']
                self.merge_configuration(failextract_config)
                self._config_sources.append(f"{file_path}[tool.failextract]")
                
        except Exception as e:
            raise ConfigurationError(f"Failed to parse pyproject.toml {file_path}: {e}")
    
    def load_from_environment(self) -> None:
        """Load configuration from environment variables.
        
        Environment variables should be prefixed with FAILEXTRACT_ and use
        underscore notation for nested sections: FAILEXTRACT_OUTPUT_DEFAULT_FORMAT
        """
        env_config = {}
        
        for key, value in os.environ.items():
            if key.startswith('FAILEXTRACT_'):
                # Remove prefix and convert to nested dict
                config_key = key[12:]  # Remove 'FAILEXTRACT_'
                parts = config_key.lower().split('_')
                
                if len(parts) >= 2:
                    section = parts[0]
                    field = '_'.join(parts[1:])
                    
                    if section not in env_config:
                        env_config[section] = {}
                    
                    # Convert string values to appropriate types
                    converted_value = self._convert_env_value(value)
                    env_config[section][field] = converted_value
        
        if env_config:
            self.merge_configuration(env_config)
            self._config_sources.append("environment variables")
    
    def load_from_workspace(self, start_path: Union[str, Path]) -> None:
        """Load configuration from workspace.
        
        Args:
            start_path: Path to start workspace detection from
        """
        detector = WorkspaceDetector()
        workspace_root = detector.detect_workspace(start_path)
        
        if workspace_root:
            self.workspace_root = workspace_root
            
            # Try to load configuration files from workspace root
            config_files = [
                'failextract.toml',
                '.failextract.toml',
                'failextract.yaml',
                '.failextract.yaml',
                'failextract.yml',
                '.failextract.yml',
                'pyproject.toml',
            ]
            
            for config_file in config_files:
                config_path = workspace_root / config_file
                if config_path.exists():
                    if config_file == 'pyproject.toml':
                        self.load_from_pyproject_toml(config_path)
                    else:
                        self.load_from_file(config_path)
    
    def merge_configuration(self, config_data: Dict[str, Any]) -> None:
        """Merge configuration data into current configuration.
        
        Args:
            config_data: Configuration data to merge
        """
        self.config.merge(config_data)
    
    def get_effective_config(self) -> ProjectConfig:
        """Get the effective configuration after all merging.
        
        Returns:
            Current effective configuration
        """
        return self.config
    
    def create_output_config(self, filename: Optional[str] = None, **kwargs) -> 'OutputConfig':
        """Create OutputConfig with project defaults.
        
        Args:
            filename: Output filename
            **kwargs: Additional OutputConfig parameters
            
        Returns:
            OutputConfig instance
        """
        return self.config.get_output_config(filename, **kwargs)
    
    def get_extraction_config(self) -> ExtractionSection:
        """Get extraction configuration.
        
        Returns:
            Extraction configuration section
        """
        return self.config.extraction
    
    def _load_toml_file(self, file_path: Path) -> Dict[str, Any]:
        """Load TOML file."""
        if tomllib is None:
            raise ConfigurationError("TOML support not available. Install tomli for Python < 3.11")
        
        with open(file_path, 'rb') as f:
            data = tomllib.load(f)
        
        # Handle TOML files with 'tool.failextract' section (like pyproject.toml style)
        if 'tool' in data and 'failextract' in data['tool']:
            return data['tool']['failextract']
        
        # Handle direct failextract configuration
        if 'failextract' in data:
            return data['failextract']
        
        # Return the whole data if no specific section found
        return data
    
    def _load_yaml_file(self, file_path: Path) -> Dict[str, Any]:
        """Load YAML file."""
        with open(file_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
            
        # Handle YAML file with 'failextract' root key
        if isinstance(data, dict) and 'failextract' in data:
            return data['failextract']
        
        return data or {}
    
    def _convert_env_value(self, value: str) -> Union[str, int, float, bool]:
        """Convert environment variable string to appropriate type."""
        # Boolean conversion
        if value.lower() in ('true', 'yes', '1', 'on'):
            return True
        elif value.lower() in ('false', 'no', '0', 'off'):
            return False
        
        # Numeric conversion
        try:
            if '.' in value:
                return float(value)
            else:
                return int(value)
        except ValueError:
            pass
        
        # String (default)
        return value
    
    @property
    def config_sources(self) -> List[str]:
        """Get list of configuration sources that were loaded."""
        return self._config_sources.copy()