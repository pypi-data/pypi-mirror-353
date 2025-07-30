"""Unit tests for CodeContextExtractor functionality."""

import ast
import inspect
import tempfile
import textwrap
import threading
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from failextract.failextract import CodeContextExtractor


class TestCodeContextExtractor:
    """Test CodeContextExtractor implementation."""

    def test_singleton_pattern(self):
        """Test that CodeContextExtractor implements singleton pattern."""
        # 01 Nominal Behaviors
        extractor1 = CodeContextExtractor()
        extractor2 = CodeContextExtractor()
        
        # Should be the same instance
        assert extractor1 is extractor2
        assert id(extractor1) == id(extractor2)

    def test_thread_safety(self):
        """Test thread-safe singleton implementation."""
        # 05 State Transition Behaviors
        instances = []
        barrier = threading.Barrier(5)
        
        def create_instance():
            barrier.wait()  # Ensure all threads start simultaneously
            instances.append(CodeContextExtractor())
        
        threads = []
        for _ in range(5):
            thread = threading.Thread(target=create_instance)
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join()
        
        # All instances should be the same
        assert len(set(id(instance) for instance in instances)) == 1

    def test_initialization(self):
        """Test CodeContextExtractor initialization."""
        # 01 Nominal Behaviors
        extractor = CodeContextExtractor()
        
        assert hasattr(extractor, '_source_cache')
        assert hasattr(extractor, '_cache_lock')
        assert isinstance(extractor._source_cache, dict)
        assert hasattr(extractor._cache_lock, 'acquire')  # Check if it's a lock-like object

    def test_extract_function_source_with_context_basic(self):
        """Test basic function source extraction with context."""
        # 01 Nominal Behaviors
        extractor = CodeContextExtractor()
        
        # Create a temporary file with test code
        test_code = textwrap.dedent('''
            def helper_function():
                return "helper"
            
            def test_function():
                value = helper_function()
                assert value == "helper"
                return value
            
            def another_function():
                pass
        ''').strip()
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(test_code)
            temp_file = f.name
        
        try:
            # Create a mock frame for test_function
            mock_frame = Mock()
            mock_frame.f_code.co_filename = temp_file
            mock_frame.f_code.co_name = 'test_function'
            mock_frame.f_lineno = 5  # Line where test_function is defined
            
            result = extractor.extract_function_source_with_context(
                mock_frame, context_lines=2, include_line_numbers=True
            )
            
            assert isinstance(result, dict)
            assert 'source' in result
            assert 'start_line' in result
            assert 'end_line' in result
            assert 'failure_line' in result
            
            # Should include context around the function
            source = result['source']
            assert len(source) > 0
            assert 'def test_function():' in source
            
        finally:
            Path(temp_file).unlink()

    def test_extract_function_source_with_context_line_numbers(self):
        """Test line number inclusion in source extraction."""
        # 01 Nominal Behaviors
        extractor = CodeContextExtractor()
        
        test_code = textwrap.dedent('''
            # Line 1
            def simple_test():
                # Line 3
                assert True
                # Line 5
        ''').strip()
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(test_code)
            temp_file = f.name
        
        try:
            mock_frame = Mock()
            mock_frame.f_code.co_filename = temp_file
            mock_frame.f_code.co_name = 'simple_test'
            mock_frame.f_lineno = 2
            
            # Test with line numbers
            result_with_numbers = extractor.extract_function_source_with_context(
                mock_frame, context_lines=1, include_line_numbers=True
            )
            assert result_with_numbers['include_line_numbers'] is True
            assert result_with_numbers['start_line'] >= 1
            
            # Test without line numbers
            result_without_numbers = extractor.extract_function_source_with_context(
                mock_frame, context_lines=1, include_line_numbers=False
            )
            assert result_without_numbers['include_line_numbers'] is False
            
        finally:
            Path(temp_file).unlink()

    def test_extract_function_source_with_context_lines_parameter(self):
        """Test configurable context lines parameter."""
        # 03 Boundary Behaviors
        extractor = CodeContextExtractor()
        
        test_code = textwrap.dedent('''
            # Line 1 - context
            # Line 2 - context
            def target_function():
                # Line 4 - function body
                pass
            # Line 6 - context
            # Line 7 - context
        ''').strip()
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(test_code)
            temp_file = f.name
        
        try:
            mock_frame = Mock()
            mock_frame.f_code.co_filename = temp_file
            mock_frame.f_code.co_name = 'target_function'
            mock_frame.f_lineno = 3
            
            # Test with minimal context (0 lines)
            result_0 = extractor.extract_function_source_with_context(
                mock_frame, context_lines=0, include_line_numbers=True
            )
            
            # Test with moderate context (2 lines)
            result_2 = extractor.extract_function_source_with_context(
                mock_frame, context_lines=2, include_line_numbers=True
            )
            
            # Test with large context (10 lines)
            result_10 = extractor.extract_function_source_with_context(
                mock_frame, context_lines=10, include_line_numbers=True
            )
            
            # More context should include more lines (up to file boundaries)
            assert len(result_0['lines']) <= len(result_2['lines'])
            assert len(result_2['lines']) <= len(result_10['lines'])
            
        finally:
            Path(temp_file).unlink()

    def test_extract_function_source_max_lines_limit(self):
        """Test maximum lines limit enforcement."""
        # 03 Boundary Behaviors
        extractor = CodeContextExtractor()
        
        # Create a large function
        large_function_lines = ['def large_function():'] + [f'    # Line {i}' for i in range(200)]
        test_code = '\n'.join(large_function_lines)
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(test_code)
            temp_file = f.name
        
        try:
            mock_frame = Mock()
            mock_frame.f_code.co_filename = temp_file
            mock_frame.f_code.co_name = 'large_function'
            mock_frame.f_lineno = 1
            
            result = extractor.extract_function_source_with_context(
                mock_frame, max_lines=50, include_line_numbers=True
            )
            
            # Should not exceed max_lines limit
            assert len(result['lines']) <= 50
            
        finally:
            Path(temp_file).unlink()

    def test_extract_function_source_file_not_found(self):
        """Test handling of non-existent files."""
        # 02 Negative Behaviors
        extractor = CodeContextExtractor()
        
        mock_frame = Mock()
        mock_frame.f_code.co_filename = '/nonexistent/file.py'
        mock_frame.f_code.co_name = 'test_function'
        mock_frame.f_lineno = 10
        
        result = extractor.extract_function_source_with_context(mock_frame)
        
        # Should handle gracefully
        assert isinstance(result, dict)
        assert 'lines' in result
        assert 'error' in result
        assert result['lines'] == []

    def test_extract_function_source_invalid_frame(self):
        """Test handling of invalid frame objects."""
        # 02 Negative Behaviors
        extractor = CodeContextExtractor()
        
        # Test with None frame
        result = extractor.extract_function_source_with_context(None)
        assert isinstance(result, dict)
        assert result['lines'] == []
        assert 'error' in result
        
        # Test with invalid frame object
        invalid_frame = Mock()
        invalid_frame.f_code = None
        
        result = extractor.extract_function_source_with_context(invalid_frame)
        assert isinstance(result, dict)
        assert result['lines'] == []
        assert 'error' in result

    def test_source_caching_functionality(self):
        """Test source code caching mechanism."""
        # 05 State Transition Behaviors
        extractor = CodeContextExtractor()
        
        test_code = textwrap.dedent('''
            def cached_function():
                return "cached"
        ''').strip()
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(test_code)
            temp_file = f.name
        
        try:
            mock_frame = Mock()
            mock_frame.f_code.co_filename = temp_file
            mock_frame.f_code.co_name = 'cached_function'
            mock_frame.f_lineno = 1
            
            # First call should cache the source
            result1 = extractor.extract_function_source_with_context(mock_frame)
            
            # Check that file is in cache
            assert temp_file in extractor._source_cache
            
            # Second call should use cached source
            with patch('builtins.open') as mock_open:
                result2 = extractor.extract_function_source_with_context(mock_frame)
                # open should not be called for cached file
                mock_open.assert_not_called()
            
            # Results should be identical
            assert result1['lines'] == result2['lines']
            
        finally:
            Path(temp_file).unlink()

    def test_cache_invalidation_on_file_modification(self):
        """Test cache invalidation when file is modified."""
        # 05 State Transition Behaviors
        extractor = CodeContextExtractor()
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write('def original_function(): pass')
            temp_file = f.name
        
        try:
            mock_frame = Mock()
            mock_frame.f_code.co_filename = temp_file
            mock_frame.f_code.co_name = 'original_function'
            mock_frame.f_lineno = 1
            
            # First call
            result1 = extractor.extract_function_source_with_context(mock_frame)
            
            # Modify the file
            import time
            time.sleep(0.1)  # Ensure different modification time
            with open(temp_file, 'w') as f:
                f.write('def modified_function(): pass')
            
            # Second call should detect modification and reload
            mock_frame.f_code.co_name = 'modified_function'
            result2 = extractor.extract_function_source_with_context(mock_frame)
            
            # Results should be different
            assert result1['lines'] != result2['lines']
            assert 'modified_function' in '\n'.join(result2['lines'])
            
        finally:
            Path(temp_file).unlink()

    def test_ast_parsing_for_function_detection(self):
        """Test AST parsing for intelligent function detection."""
        # 01 Nominal Behaviors
        extractor = CodeContextExtractor()
        
        test_code = textwrap.dedent('''
            def outer_function():
                def inner_function():
                    return "inner"
                
                def another_inner():
                    pass
                
                return inner_function()
            
            class TestClass:
                def method_function(self):
                    return "method"
        ''').strip()
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(test_code)
            temp_file = f.name
        
        try:
            # Test outer function detection
            mock_frame = Mock()
            mock_frame.f_code.co_filename = temp_file
            mock_frame.f_code.co_name = 'outer_function'
            mock_frame.f_lineno = 1
            
            result = extractor.extract_function_source_with_context(mock_frame)
            lines_text = '\n'.join(result['lines'])
            assert 'def outer_function():' in lines_text
            
            # Test method detection
            mock_frame.f_code.co_name = 'method_function'
            mock_frame.f_lineno = 10
            
            result = extractor.extract_function_source_with_context(mock_frame)
            lines_text = '\n'.join(result['lines'])
            assert 'def method_function(self):' in lines_text
            
        finally:
            Path(temp_file).unlink()

    def test_extract_function_source_edge_cases(self):
        """Test edge cases in function source extraction."""
        # 03 Boundary Behaviors
        extractor = CodeContextExtractor()
        
        # Test with empty file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write('')
            empty_file = f.name
        
        try:
            mock_frame = Mock()
            mock_frame.f_code.co_filename = empty_file
            mock_frame.f_code.co_name = 'nonexistent_function'
            mock_frame.f_lineno = 1
            
            result = extractor.extract_function_source_with_context(mock_frame)
            assert result['lines'] == []
            
        finally:
            Path(empty_file).unlink()

    def test_concurrent_access_thread_safety(self):
        """Test thread safety under concurrent access."""
        # 05 State Transition Behaviors
        extractor = CodeContextExtractor()
        
        test_code = textwrap.dedent('''
            def concurrent_function():
                return "thread_safe"
        ''').strip()
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(test_code)
            temp_file = f.name
        
        try:
            results = []
            barrier = threading.Barrier(3)
            
            def extract_source():
                barrier.wait()
                mock_frame = Mock()
                mock_frame.f_code.co_filename = temp_file
                mock_frame.f_code.co_name = 'concurrent_function'
                mock_frame.f_lineno = 1
                
                result = extractor.extract_function_source_with_context(mock_frame)
                results.append(result)
            
            threads = []
            for _ in range(3):
                thread = threading.Thread(target=extract_source)
                threads.append(thread)
                thread.start()
            
            for thread in threads:
                thread.join()
            
            # All results should be identical and valid
            assert len(results) == 3
            for result in results:
                assert 'concurrent_function' in '\n'.join(result['lines'])
                assert result['lines'] == results[0]['lines']
                
        finally:
            Path(temp_file).unlink()

    def test_memory_efficiency_large_files(self):
        """Test memory efficiency with large files."""
        # 04 Error Handling Behaviors
        extractor = CodeContextExtractor()
        
        # Create a large file with many functions
        large_code_lines = []
        for i in range(500):
            large_code_lines.extend([
                f'def function_{i}():',
                f'    """Function number {i}"""',
                f'    return {i}',
                ''
            ])
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write('\n'.join(large_code_lines))
            large_file = f.name
        
        try:
            mock_frame = Mock()
            mock_frame.f_code.co_filename = large_file
            mock_frame.f_code.co_name = 'function_250'
            mock_frame.f_lineno = 1000  # Somewhere in the middle
            
            # Should handle large files without excessive memory usage
            result = extractor.extract_function_source_with_context(
                mock_frame, max_lines=20
            )
            
            # Should return reasonable amount of context
            assert len(result['lines']) <= 20
            assert any('function_250' in line for line in result['lines'])
            
        finally:
            Path(large_file).unlink()

    def test_unicode_and_special_characters(self):
        """Test handling of Unicode and special characters in source code."""
        # 02 Negative Behaviors
        extractor = CodeContextExtractor()
        
        test_code = textwrap.dedent('''
            def unicode_function():
                # Comments with unicode: 你好, мир, 🌍
                text = "Special chars: <>&'\\""
                return text
        ''').strip()
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as f:
            f.write(test_code)
            temp_file = f.name
        
        try:
            mock_frame = Mock()
            mock_frame.f_code.co_filename = temp_file
            mock_frame.f_code.co_name = 'unicode_function'
            mock_frame.f_lineno = 1
            
            result = extractor.extract_function_source_with_context(mock_frame)
            
            lines_text = '\n'.join(result['lines'])
            assert 'unicode_function' in lines_text
            assert '你好' in lines_text
            assert '🌍' in lines_text
            
        finally:
            Path(temp_file).unlink()

    def test_performance_benchmarking(self):
        """Test performance characteristics of extraction."""
        # Performance Testing
        import time
        
        extractor = CodeContextExtractor()
        
        test_code = textwrap.dedent('''
            def performance_test_function():
                for i in range(100):
                    value = i * 2
                return value
        ''').strip()
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(test_code)
            temp_file = f.name
        
        try:
            mock_frame = Mock()
            mock_frame.f_code.co_filename = temp_file
            mock_frame.f_code.co_name = 'performance_test_function'
            mock_frame.f_lineno = 1
            
            # First call (with file I/O)
            start_time = time.time()
            result1 = extractor.extract_function_source_with_context(mock_frame)
            first_call_time = time.time() - start_time
            
            # Second call (cached)
            start_time = time.time()
            result2 = extractor.extract_function_source_with_context(mock_frame)
            cached_call_time = time.time() - start_time
            
            # Cached call should be significantly faster
            assert cached_call_time < first_call_time
            assert result1['lines'] == result2['lines']
            
            # Both calls should complete quickly (< 0.1 seconds)
            assert first_call_time < 0.1
            assert cached_call_time < 0.01
            
        finally:
            Path(temp_file).unlink()