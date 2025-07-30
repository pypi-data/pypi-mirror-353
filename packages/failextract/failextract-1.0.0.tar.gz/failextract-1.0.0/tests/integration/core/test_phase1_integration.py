"""Integration tests for Phase 1 enhanced code context functionality."""

import tempfile
import textwrap
from pathlib import Path
from unittest.mock import Mock

import pytest

from failextract.failextract import (
    CodeContextExtractor,
    MarkdownFormatter,
    OutputConfig,
    extract_failure_info,
    extract_on_failure,
)
# HTMLFormatter has been removed from the codebase


class TestPhase1Integration:
    """Integration tests for Phase 1 enhanced functionality."""

    def test_end_to_end_enhanced_context_extraction(self):
        """Test complete enhanced context extraction flow."""
        # Create test code
        test_code = textwrap.dedent('''
            def helper_function():
                return "helper result"
            
            def test_enhanced_feature():
                """Test the enhanced code context feature."""
                result = helper_function()
                assert result == "expected result", "Values should match"
                return result
        ''').strip()
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(test_code)
            temp_file = f.name
        
        try:
            # Create mock frame
            mock_frame = Mock()
            mock_frame.f_code.co_filename = temp_file
            mock_frame.f_code.co_name = 'test_enhanced_feature'
            mock_frame.f_lineno = 6  # Line with the function definition
            mock_frame.f_globals = {'__file__': temp_file}
            
            # Create exception
            exception = AssertionError("Values should match")
            
            # Use enhanced configuration
            config = OutputConfig(
                enhanced_context=True,
                code_context_lines=3,
                include_line_numbers=True
            )
            
            # Extract failure info
            result = extract_failure_info(exception, mock_frame, config=config)
            
            # Verify enhanced context is included
            assert result['enhanced_context'] is True
            assert 'test_source_with_context' in result
            
            context = result['test_source_with_context']
            assert isinstance(context, dict)
            assert 'lines' in context
            assert 'start_line' in context
            assert 'include_line_numbers' in context
            
            # Verify content includes the test function
            lines_text = '\n'.join(context['lines'])
            assert 'test_enhanced_feature' in lines_text
            
        finally:
            Path(temp_file).unlink()

    # HTMLFormatter has been removed from the codebase
    # def test_html_formatter_with_enhanced_context(self):
    #     """Test HTML formatter with enhanced context data."""
    #     formatter = HTMLFormatter()
    #     
    #     failure_data = {
    #         "test_name": "test_html_integration",
    #         "test_module": "test_module",
    #         "test_file": "/path/to/test.py",
    #         "timestamp": "2024-01-01T12:00:00",
    #         "exception_type": "AssertionError",
    #         "exception_message": "Integration test failure",
    #         "test_source": "def test_html_integration(): pass",
    #         "enhanced_context": True,
    #         "test_source_with_context": {
    #             "lines": [
    #                 "# Comment before function",
    #                 "def test_html_integration():",
    #                 "    assert False, 'Integration test failure'",
    #                 "    return None"
    #             ],
    #             "start_line": 5,
    #             "include_line_numbers": True
    #         }
    #     }
    #     
    #     result = formatter.format([failure_data])
    #     
    #     # Verify enhanced HTML formatting (modern CSS classes)
    #     assert "language-python" in result or "code-block" in result
    #     assert "test_html_integration" in result
    #     assert "Integration test failure" in result
    #     
    #     # Verify that enhanced context content is included
    #     assert "Comment before function" in result
    #     assert "def test_html_integration" in result

    def test_markdown_formatter_with_enhanced_context(self):
        """Test Markdown formatter with enhanced context data."""
        formatter = MarkdownFormatter()
        
        failure_data = {
            "test_name": "test_markdown_integration",
            "test_module": "test_module", 
            "test_file": "/path/to/test.py",
            "timestamp": "2024-01-01T12:00:00",
            "exception_type": "ValueError",
            "exception_message": "Markdown test failure",
            "test_source": "def test_markdown_integration(): pass",
            "enhanced_context": True,
            "test_source_with_context": {
                "lines": [
                    "def test_markdown_integration():",
                    "    value = calculate_result()",
                    "    raise ValueError('Markdown test failure')"
                ],
                "start_line": 10,
                "include_line_numbers": True
            }
        }
        
        result = formatter.format([failure_data])
        
        # Verify enhanced Markdown formatting
        assert "```python" in result
        assert "# Line 10" in result
        assert "# Line 11" in result
        assert "# Line 12" in result
        assert "test_markdown_integration" in result

    def test_code_context_extractor_singleton(self):
        """Test CodeContextExtractor singleton behavior."""
        extractor1 = CodeContextExtractor()
        extractor2 = CodeContextExtractor()
        
        # Should be the same instance
        assert extractor1 is extractor2
        assert id(extractor1) == id(extractor2)

    def test_output_config_enhanced_parameters(self):
        """Test OutputConfig with enhanced parameters."""
        config = OutputConfig(
            enhanced_context=True,
            include_source=True,
            include_fixtures=True,
            code_context_lines=10,
            max_code_lines=200,
            include_line_numbers=True
        )
        
        # Verify all enhanced parameters are set
        assert config.enhanced_context is True
        assert config.include_source is True
        assert config.include_fixtures is True
        assert config.code_context_lines == 10
        assert config.max_code_lines == 200
        assert config.include_line_numbers is True

    def test_extract_on_failure_decorator_integration(self):
        """Test extract_on_failure decorator with enhanced context."""
        test_code = textwrap.dedent('''
            def decorated_test_function():
                """A test function with decorator."""
                value = 42
                assert value == 100, "Expected 100"
                return value
        ''').strip()
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(test_code)
            temp_file = f.name
        
        try:
            # Create mock frame for decorator test
            mock_frame = Mock()
            mock_frame.f_code.co_filename = temp_file
            mock_frame.f_code.co_name = 'decorated_test_function'
            mock_frame.f_lineno = 4  # Line with assert
            mock_frame.f_globals = {'__file__': temp_file}
            
            exception = AssertionError("Expected 100")
            
            # Test decorator with enhanced context
            config = OutputConfig(enhanced_context=True)
            result = extract_failure_info(exception, mock_frame, config=config)
            
            # Should have enhanced context
            assert result['enhanced_context'] is True
            if 'test_source_with_context' in result:
                context = result['test_source_with_context']
                lines_text = '\n'.join(context['lines'])
                assert 'decorated_test_function' in lines_text
                
        finally:
            Path(temp_file).unlink()

    def test_formatter_fallback_behavior(self):
        """Test formatter fallback when enhanced context is disabled."""
        # Use MarkdownFormatter instead of HTMLFormatter
        formatter = MarkdownFormatter()
        
        failure_data = {
            "test_name": "test_fallback",
            "test_module": "test_module",
            "test_file": "/path/to/test.py", 
            "timestamp": "2024-01-01T12:00:00",
            "exception_type": "RuntimeError",
            "exception_message": "Fallback test",
            "test_source": "def test_fallback(): pass",
            "enhanced_context": False  # Disabled
        }
        
        result = formatter.format([failure_data])
        
        # Should include basic content regardless of enhanced context setting
        assert "test_fallback" in result
        assert "Fallback test" in result
        assert "def test_fallback(): pass" in result

    def test_performance_integration(self):
        """Test performance of complete enhanced context flow."""
        import time
        
        test_code = textwrap.dedent('''
            def performance_integration_test():
                for i in range(50):
                    value = i * 2
                assert value == 100, "Performance test"
        ''').strip()
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(test_code)
            temp_file = f.name
        
        try:
            mock_frame = Mock()
            mock_frame.f_code.co_filename = temp_file
            mock_frame.f_code.co_name = 'performance_integration_test'
            mock_frame.f_lineno = 1
            mock_frame.f_globals = {'__file__': temp_file}
            
            exception = AssertionError("Performance test")
            config = OutputConfig(enhanced_context=True)
            
            # Measure performance
            start_time = time.time()
            result = extract_failure_info(exception, mock_frame, config=config)
            extraction_time = time.time() - start_time
            
            # Should complete quickly
            assert extraction_time < 0.1  # Less than 100ms
            assert result['enhanced_context'] is True
            
            # Test formatter performance (using MarkdownFormatter instead of HTMLFormatter)
            formatter = MarkdownFormatter()
            start_time = time.time()
            formatted = formatter.format([result])
            format_time = time.time() - start_time
            
            # Should format quickly
            assert format_time < 0.1
            assert len(formatted) > 100  # Should have substantial output
            
        finally:
            Path(temp_file).unlink()

    def test_unicode_integration(self):
        """Test Unicode handling in complete flow."""
        unicode_code = textwrap.dedent('''
            def test_unicode_интеграция():
                """Test with Unicode: 🐍 Python"""
                текст = "Тестовая строка"
                assert текст == "Expected", "Unicode test"
        ''').strip()
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as f:
            f.write(unicode_code)
            temp_file = f.name
        
        try:
            mock_frame = Mock()
            mock_frame.f_code.co_filename = temp_file
            mock_frame.f_code.co_name = 'test_unicode_интеграция'
            mock_frame.f_lineno = 1
            mock_frame.f_globals = {'__file__': temp_file}
            
            exception = AssertionError("Unicode test")
            config = OutputConfig(enhanced_context=True)
            
            # Extract with Unicode content
            result = extract_failure_info(exception, mock_frame, config=config)
            assert result['enhanced_context'] is True
            
            # HTMLFormatter has been removed from the codebase
            # Format with HTML (test escaping)
            # html_formatter = HTMLFormatter()
            # html_result = html_formatter.format([result])
            # 
            # # Should handle Unicode properly
            # assert 'test_unicode_' in html_result  # Function name (may be escaped)
            # assert '🐍' in html_result or '&#' in html_result  # Emoji (escaped or not)
            
            # Format with Markdown
            md_formatter = MarkdownFormatter()
            md_result = md_formatter.format([result])
            
            # Markdown should preserve Unicode
            assert 'test_unicode_интеграция' in md_result
            assert '🐍' in md_result
            
        finally:
            Path(temp_file).unlink()

    def test_backward_compatibility_integration(self):
        """Test that enhanced features don't break existing functionality."""
        test_code = "def legacy_test(): pass"
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(test_code)
            temp_file = f.name
        
        try:
            mock_frame = Mock()
            mock_frame.f_code.co_filename = temp_file
            mock_frame.f_code.co_name = 'legacy_test'
            mock_frame.f_lineno = 1
            mock_frame.f_globals = {'__file__': temp_file}
            
            exception = RuntimeError("Legacy test")
            
            # Test without explicit config (should use defaults)
            result = extract_failure_info(exception, mock_frame)
            
            # Should have standard fields for backward compatibility
            assert 'test_name' in result
            assert 'exception_type' in result
            assert 'exception_message' in result
            assert 'test_source' in result
            
            # Should also have enhanced context by default
            assert 'enhanced_context' in result
            
            # Test with existing formatters (HTMLFormatter removed)
            for FormatterClass in [MarkdownFormatter]:
                formatter = FormatterClass()
                formatted = formatter.format([result])
                
                # Should produce valid output
                assert len(formatted) > 0
                assert 'legacy_test' in formatted
                assert 'RuntimeError' in formatted
                
        finally:
            Path(temp_file).unlink()