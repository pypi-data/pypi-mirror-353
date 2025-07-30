#!/usr/bin/env python3
"""Command-line interface for FailExtract.

This module provides a CLI for the FailExtract library, allowing users to:
- Generate reports from existing failure data  
- Configure output formats and destinations
- Validate and analyze test failure patterns
- Export failure data in various formats
- Check available features and installation status

The CLI is designed to work with both interactive usage and automation/CI/CD
pipelines, providing structured output and exit codes for scripting.

The CLI automatically adapts based on installed optional features:
- Core features (JSON output, basic commands) are always available
- Advanced features require extras (e.g., pip install failextract[formatters])
- Helpful error messages guide users to install missing features

Example:
    Generate a JSON report (always available):

        $ failextract report --format json --output failures.json

    Generate a markdown report:

        $ failextract report --format markdown --output failures.md

    Check which features are available:

        $ failextract features

    Advanced failure analysis (requires analytics extra):

        $ failextract analyze --trends

Author: FailExtract Contributors
License: Apache 2.0
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

from . import FailureExtractor, OutputConfig, __version__, get_available_features, suggest_installation
from .core.registry import get_registry


def create_parser() -> argparse.ArgumentParser:
    """Create and configure the argument parser.

    Returns:
        argparse.ArgumentParser: Configured parser with all commands and options.
    """
    registry = get_registry()
    available_formatters = registry.get_available_formatters()
    
    parser = argparse.ArgumentParser(
        prog="failextract",
        description="FailExtract - Comprehensive test failure extraction and reporting",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"""
Examples:
  failextract report --format json --output failures.json
  failextract list --format table  
  failextract clear
  failextract stats
  failextract features  # Check available features
  failextract analyze   # Requires: pip install failextract[analytics]

Available output formats: {', '.join(available_formatters)}
For more formats, install: pip install failextract[formatters]
        """,
    )

    parser.add_argument(
        "--version", action="version", version=f"FailExtract {__version__}"
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Features command (new)
    features_parser = subparsers.add_parser(
        "features", help="Show available features and installation status"
    )
    features_parser.add_argument(
        "--format",
        "-f", 
        choices=["table", "json"],
        default="table",
        help="Output format (default: table)",
    )

    # Report command
    report_parser = subparsers.add_parser(
        "report", help="Generate failure report in specified format"
    )
    
    # Dynamic format choices based on available formatters
    format_choices = available_formatters.copy()
    # Add aliases for available formats
    if 'yaml' in format_choices:
        format_choices.append('yml')
    if 'markdown' in format_choices:
        format_choices.append('md')
    
    report_parser.add_argument(
        "--format",
        "-f",
        choices=format_choices,
        default="json",
        help=f"Output format (default: json). Available: {', '.join(available_formatters)}",
    )
    report_parser.add_argument(
        "--output", "-o", type=Path, help="Output file path (default: stdout)"
    )
    report_parser.add_argument(
        "--include-source",
        action="store_true",
        default=True,
        help="Include source code in report (default: true)",
    )
    report_parser.add_argument(
        "--include-fixtures",
        action="store_true",
        default=True,
        help="Include fixture information (default: true)",
    )

    # List command
    list_parser = subparsers.add_parser("list", help="List all captured failures")
    list_parser.add_argument(
        "--format",
        "-f",
        choices=["json", "table", "simple"],
        default="table",
        help="Output format (default: table)",
    )
    list_parser.add_argument(
        "--output", "-o", type=Path, help="Output file path (default: stdout)"
    )

    # Clear command
    clear_parser = subparsers.add_parser("clear", help="Clear all stored failure data")
    clear_parser.add_argument(
        "--confirm", action="store_true", help="Skip confirmation prompt"
    )

    # Stats command
    stats_parser = subparsers.add_parser("stats", help="Show failure statistics")
    stats_parser.add_argument(
        "--format",
        "-f",
        choices=["json", "table"],
        default="table",
        help="Output format (default: table)",
    )

    # Analysis command - conditionally available
    if registry.is_feature_available('analytics', 'dependency_graph'):
        analysis_parser = subparsers.add_parser("analyze", help="Perform intelligent failure analysis")
        analysis_parser.add_argument(
            "--output", "-o", type=Path, help="Output file path (default: stdout)"
        )
        analysis_parser.add_argument(
            "--format",
            "-f",
            choices=["json", "markdown", "xml"],
            default="json",
            help="Output format (default: json)",
        )
        analysis_parser.add_argument(
            "--trends",
            action="store_true",
            help="Include trend analysis (requires historical data)",
        )
        analysis_parser.add_argument(
            "--days",
            type=int,
            default=30,
            help="Number of days for trend analysis (default: 30)",
        )
        analysis_parser.add_argument(
            "--storage",
            type=str,
            help="Path to analysis database (default: failextract_analysis.db)",
        )

    return parser


def format_table_output(data: List[Dict[str, Any]], headers: List[str]) -> str:
    """Format data as a simple ASCII table for terminal output.

    Creates a formatted table with aligned columns suitable for display
    in terminals. Automatically calculates column widths based on content
    and provides clean separation between columns.

    Args:
        data: List of dictionaries containing row data where keys match headers
        headers: List of column headers to display

    Returns:
        Formatted ASCII table string with headers and aligned data rows

    Example:
        >>> data = [{'name': 'test1', 'status': 'passed'}, {'name': 'test2', 'status': 'failed'}]
        >>> headers = ['name', 'status']
        >>> table = format_table_output(data, headers)
        >>> print(table)
        name   status
        -----  ------
        test1  passed
        test2  failed
    """
    if not data:
        return "No data to display."

    # Calculate column widths
    widths = {}
    for header in headers:
        widths[header] = len(header)
        for row in data:
            value = str(row.get(header, ""))
            widths[header] = max(widths[header], len(value))

    # Format header
    header_line = " | ".join(h.ljust(widths[h]) for h in headers)
    separator = "-+-".join("-" * widths[h] for h in headers)

    # Format rows
    rows = []
    for row in data:
        row_line = " | ".join(str(row.get(h, "")).ljust(widths[h]) for h in headers)
        rows.append(row_line)

    return "\n".join([header_line, separator] + rows)


def cmd_features(args: argparse.Namespace) -> int:
    """Execute the features command to show available and missing features.

    Displays information about which FailExtract features are currently
    available based on installed optional dependencies, and provides
    installation instructions for missing features.

    Args:
        args: Parsed command line arguments (currently unused for this command)

    Returns:
        Exit code: 0 for success, 1 for error

    Example Output:
        Available Features:
        - json (always available)
        - xml (always available)  
        - csv (always available)
        - markdown (always available)
        
        Missing Features:
        - yaml (install with: pip install failextract[formatters])
        - config (install with: pip install failextract[config])
    """
    try:
        features = get_available_features()
        registry = get_registry()
        
        if args.format == "json":
            output = json.dumps(features, indent=2)
            print(output)
            return 0
        
        # Table format
        print("FailExtract Feature Status")
        print("=" * 50)
        
        # Core features (always available)
        print("\n✅ Core Features (Always Available):")
        for feature in features['core']:
            print(f"  • {feature}")
        
        # Available optional features
        if features['available']:
            print("\n✅ Available Optional Features:")
            for category, feature_list in features['available'].items():
                if category not in ['extraction', 'cli', 'storage']:  # Skip internal categories
                    print(f"  • {category.title()}: {', '.join(feature_list)}")
        
        # Missing optional features  
        if features['missing']:
            print("\n❌ Missing Optional Features:")
            for category, feature_list in features['missing'].items():
                if category not in ['extraction', 'cli', 'storage']:  # Skip internal categories
                    print(f"  • {category.title()}: {', '.join(feature_list)}")
                    suggestion = registry.suggest_installation(category, feature_list[0])
                    if suggestion:
                        print(f"    Install with: {suggestion}")
        
        print("\n" + "=" * 50)
        print("💡 Tip: Install feature sets with 'pip install failextract[<feature>]'")
        print("   Example: pip install failextract[formatters,analytics]")
        
        return 0
        
    except Exception as e:
        print(f"Error checking features: {e}", file=sys.stderr)
        return 1


def cmd_report(args: argparse.Namespace) -> int:
    """Execute the report command.

    Args:
        args: Parsed command line arguments.

    Returns:
        int: Exit code (0 for success, 1 for error).
    """
    try:
        extractor = FailureExtractor()
        registry = get_registry()

        # Map format aliases
        format_map = {"md": "markdown", "yml": "yaml"}
        output_format = format_map.get(args.format, args.format)

        # Check if format is available
        if output_format not in registry.get_available_formatters():
            print(f"❌ Error: Format '{output_format}' is not available.", file=sys.stderr)
            if output_format in ['xml', 'yaml', 'markdown', 'csv']:
                suggestion = suggest_installation('formatters')
                print(f"💡 Install with: {suggestion}", file=sys.stderr)
            return 1

        if args.output:
            # Save to file
            try:
                config = OutputConfig(
                    str(args.output),
                    format=output_format,
                    include_source=args.include_source,
                    include_fixtures=args.include_fixtures,
                )
                extractor.save_report(config)
                print(f"✅ Report saved to {args.output}")
            except Exception as e:
                if "requires additional dependencies" in str(e):
                    print(f"❌ Error: {e}", file=sys.stderr)
                    return 1
                raise e
        else:
            # Output to stdout
            failures = extractor.get_failures()
            if not failures:
                print("No failures found.")
                return 0

            if output_format == "json":
                print(json.dumps(failures, indent=2))
            else:
                try:
                    config = OutputConfig(
                        "stdout",
                        format=output_format,
                        include_source=args.include_source,
                        include_fixtures=args.include_fixtures,
                    )
                    formatted = extractor._format_data(failures, config)
                    print(formatted)
                except Exception as e:
                    if "requires additional dependencies" in str(e):
                        print(f"❌ Error: {e}", file=sys.stderr)
                        return 1
                    raise e

        return 0

    except Exception as e:
        print(f"❌ Error generating report: {e}", file=sys.stderr)
        return 1


def cmd_list(args: argparse.Namespace) -> int:
    """Execute the list command.

    Args:
        args: Parsed command line arguments.

    Returns:
        int: Exit code (0 for success, 1 for error).
    """
    try:
        extractor = FailureExtractor()
        failures = extractor.failures

        if not failures:
            print("No failures found.")
            return 0

        if args.format == "json":
            output = json.dumps(failures, indent=2)
        elif args.format == "simple":
            output = "\n".join(
                f"- {f['test_name']}: {f['error_message']}" for f in failures
            )
        else:  # table format
            table_data = []
            for f in failures:
                table_data.append(
                    {
                        "Test": f.get("test_name", "Unknown"),
                        "Error": f.get("error_message", "")[:50] + "..."
                        if len(f.get("error_message", "")) > 50
                        else f.get("error_message", ""),
                        "File": f.get("test_file", "Unknown"),
                        "Timestamp": f.get("timestamp", "Unknown"),
                    }
                )
            output = format_table_output(
                table_data, ["Test", "Error", "File", "Timestamp"]
            )

        if args.output:
            args.output.write_text(output)
            print(f"✅ Output saved to {args.output}")
        else:
            print(output)

        return 0

    except Exception as e:
        print(f"❌ Error listing failures: {e}", file=sys.stderr)
        return 1


def cmd_clear(args: argparse.Namespace) -> int:
    """Execute the clear command.

    Args:
        args: Parsed command line arguments.

    Returns:
        int: Exit code (0 for success, 1 for error).
    """
    try:
        if not args.confirm:
            response = input("Are you sure you want to clear all failure data? (y/N): ")
            if response.lower() not in ["y", "yes"]:
                print("Operation cancelled.")
                return 0

        extractor = FailureExtractor()
        count = len(extractor.get_failures())
        extractor.clear()

        print(f"✅ Cleared {count} failure record(s).")
        return 0

    except Exception as e:
        print(f"❌ Error clearing failures: {e}", file=sys.stderr)
        return 1


def cmd_stats(args: argparse.Namespace) -> int:
    """Execute the stats command.

    Args:
        args: Parsed command line arguments.

    Returns:
        int: Exit code (0 for success, 1 for error).
    """
    try:
        extractor = FailureExtractor()
        failures = extractor.failures

        # Calculate statistics
        total_failures = len(failures)
        if total_failures == 0:
            print("No failure data available.")
            return 0

        # Group by test file
        files = {}
        error_types = {}

        for failure in failures:
            test_file = failure.get("test_file", "Unknown")
            files[test_file] = files.get(test_file, 0) + 1

            error_msg = failure.get("error_message", "")
            # Simple error type classification
            if "AssertionError" in error_msg:
                error_type = "AssertionError"
            elif "AttributeError" in error_msg:
                error_type = "AttributeError"
            elif "TypeError" in error_msg:
                error_type = "TypeError"
            elif "ValueError" in error_msg:
                error_type = "ValueError"
            else:
                error_type = "Other"

            error_types[error_type] = error_types.get(error_type, 0) + 1

        stats = {
            "total_failures": total_failures,
            "files_affected": len(files),
            "top_files": dict(
                sorted(files.items(), key=lambda x: x[1], reverse=True)[:5]
            ),
            "error_types": error_types,
        }

        if args.format == "json":
            print(json.dumps(stats, indent=2))
        else:  # table format
            print(f"📊 Failure Statistics")
            print("=" * 40)
            print(f"Total Failures: {stats['total_failures']}")
            print(f"Files Affected: {stats['files_affected']}")
            print("\nTop Files by Failure Count:")
            for file, count in stats["top_files"].items():
                print(f"  • {file}: {count}")
            print("\nError Types:")
            for error_type, count in stats["error_types"].items():
                print(f"  • {error_type}: {count}")

        return 0

    except Exception as e:
        print(f"❌ Error generating stats: {e}", file=sys.stderr)
        return 1


def cmd_analyze(args: argparse.Namespace) -> int:
    """Execute the analyze command.

    Args:
        args: Parsed command line arguments.

    Returns:
        int: Exit code (0 for success, 1 for error).
    """
    try:
        # Check if analytics features are available
        registry = get_registry()
        if not registry.is_feature_available('analytics', 'dependency_graph'):
            print("❌ Error: Advanced analysis features are not available.", file=sys.stderr)
            suggestion = suggest_installation('analytics')
            print(f"💡 Install with: {suggestion}", file=sys.stderr)
            return 1

        # Get failure data
        extractor = FailureExtractor()
        failures = extractor.get_failures()
        
        if not failures:
            print("No failure data available for analysis.")
            return 0
        
        # Try to import and use analyzer
        try:
            from .failextract import FailureAnalyzer
            
            # Initialize analyzer
            analyzer = FailureAnalyzer(storage_path=args.storage)
            
            # Perform analysis
            analysis_results = analyzer.analyze_failures(failures)
            
            # Add trend analysis if requested
            if args.trends:
                trend_analysis = analyzer.trend_analyzer.analyze_trends(days_back=args.days)
                analysis_results['trend_analysis'] = trend_analysis
            
            # Format and output results
            if args.format == "json":
                output = json.dumps(analysis_results, indent=2)
            elif args.format == "markdown":
                output = _format_analysis_markdown(analysis_results)
            elif args.format == "markdown":
                output = _format_analysis_markdown(analysis_results)
            else:
                output = json.dumps(analysis_results, indent=2)
            
            if args.output:
                with open(args.output, 'w') as f:
                    f.write(output)
                print(f"✅ Analysis report saved to {args.output}")
            else:
                print(output)
            
            return 0
            
        except ImportError:
            print("❌ Error: FailureAnalyzer not available.", file=sys.stderr)
            suggestion = suggest_installation('analytics')
            print(f"💡 Install with: {suggestion}", file=sys.stderr)
            return 1
        
    except Exception as e:
        print(f"❌ Error performing analysis: {e}", file=sys.stderr)
        return 1


def _format_analysis_markdown(analysis: Dict[str, Any]) -> str:
    """Format analysis results as Markdown."""
    md = []
    
    # Header
    md.append("# 📊 Failure Analysis Report")
    md.append(f"\n🕒 Generated: {analysis['summary']['analysis_timestamp']}")
    md.append("")
    
    # Summary
    summary = analysis['summary']
    md.append("## 📈 Summary")
    md.append(f"- **Total Failures**: {summary['total_failures']}")
    md.append(f"- **Patterns Detected**: {summary['patterns_detected']}")
    md.append(f"- **Insights Generated**: {summary['insights_generated']}")
    md.append(f"- **Critical Failures**: {summary['critical_failures']}")
    if summary.get('highest_priority_failure'):
        md.append(f"- **Highest Priority**: {summary['highest_priority_failure']}")
    md.append("")
    
    # Top Priority Failures
    if analysis.get('priority_ranking'):
        md.append("## 🔥 Priority Ranking")
        for i, failure in enumerate(analysis['priority_ranking'][:5], 1):
            md.append(f"{i}. **{failure['failure_id']}** (Priority: {failure['priority_score']:.1f})")
            md.append(f"   - Criticality: {failure['criticality']}")
            md.append(f"   - Blast Radius: {failure['blast_radius']}")
            if failure['affected_components']:
                md.append(f"   - Components: {', '.join(failure['affected_components'])}")
        md.append("")
    
    # Key Insights
    if analysis.get('insights'):
        md.append("## 💡 Key Insights")
        for insight in analysis['insights'][:5]:  # Top 5 insights
            md.append(f"### {insight['title']}")
            md.append(f"**Confidence**: {insight['confidence']:.1%} | **Priority**: {insight['priority']}/5")
            md.append(f"\n{insight['description']}")
            if insight.get('recommended_actions'):
                md.append("\n**Recommended Actions**:")
                for action in insight['recommended_actions']:
                    md.append(f"- {action}")
            md.append("")
    
    md.append("\n---")
    md.append("*Generated by FailExtract Intelligent Analysis*")
    
    return "\n".join(md)


def _format_analysis_markdown(analysis: Dict[str, Any]) -> str:
    """Format analysis results as Markdown."""
    # Simplified Markdown output for core functionality
    md = []
    md.append("# Failure Analysis Report")
    md.append(f"*Generated: {analysis['summary']['analysis_timestamp']}*")
    md.append(f"**Total Failures:** {analysis['summary']['total_failures']}")
    return '\n\n'.join(md)


def main() -> int:
    """Main CLI entry point.

    Returns:
        int: Exit code (0 for success, non-zero for error).
    """
    try:
        parser = create_parser()
        args = parser.parse_args()

        if not args.command:
            # Show help with feature status
            parser.print_help()
            print("\n" + "=" * 50)
            print("💡 Quick Start:")
            print("  failextract features    # Check available features")
            print("  failextract report      # Generate JSON report")
            print("  failextract list        # List captured failures")
            print("\n🚀 For more features, install extras:")
            print("  pip install failextract[formatters]  # XML, YAML output")
            print("  pip install failextract[analytics]   # Advanced analysis") 
            print("  pip install failextract[all]         # Everything")
            return 1

        # Execute command
        if args.command == "features":
            return cmd_features(args)
        elif args.command == "report":
            return cmd_report(args)
        elif args.command == "list":
            return cmd_list(args)
        elif args.command == "clear":
            return cmd_clear(args)
        elif args.command == "stats":
            return cmd_stats(args)
        elif args.command == "analyze":
            return cmd_analyze(args)
        else:
            print(f"❌ Unknown command: {args.command}", file=sys.stderr)
            return 1

    except KeyboardInterrupt:
        print("\n⏹️  Operation cancelled by user.")
        return 1
    except Exception as e:
        print(f"❌ Unexpected error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())