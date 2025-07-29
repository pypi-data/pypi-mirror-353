#!/usr/bin/env python3
"""
Simple test for fast-glob prefilter search functionality
"""
import asyncio
import sys
import os
import tempfile
from pathlib import Path
import pytest

# Add src to path so we can import tunacode modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_fast_glob_import():
    """Test that fast_glob function can be imported"""
    from tunacode.tools.grep import fast_glob
    assert fast_glob is not None

def test_fast_glob_basic_functionality():
    """Test basic fast_glob functionality with real files"""
    from tunacode.tools.grep import fast_glob
    
    # Use current directory which has Python files
    root = Path(".")
    
    # Test finding Python files
    python_files = fast_glob(root, "*.py")
    
    assert len(python_files) > 0, "Should find at least some Python files"
    assert all(str(f).endswith('.py') for f in python_files), "All results should be .py files"
    
    # Test specific pattern
    test_files = fast_glob(root, "test_*.py")
    assert len(test_files) >= 2, "Should find our test files"  # At least test_react_thoughts.py and this file

def test_fast_glob_multiple_extensions():
    """Test fast_glob with multiple extensions pattern"""
    from tunacode.tools.grep import fast_glob
    
    root = Path(".")
    
    # Test multiple extensions pattern
    code_files = fast_glob(root, "*.{py,md}")
    
    assert len(code_files) > 0, "Should find Python and Markdown files"
    
    py_files = [f for f in code_files if str(f).endswith('.py')]
    md_files = [f for f in code_files if str(f).endswith('.md')]
    
    assert len(py_files) > 0, "Should find some Python files"
    assert len(md_files) > 0, "Should find some Markdown files"

def test_parallel_grep_import():
    """Test that ParallelGrep class can be imported"""
    from tunacode.tools.grep import ParallelGrep, grep
    assert ParallelGrep is not None
    assert grep is not None

@pytest.mark.asyncio
async def test_grep_search_integration():
    """Test that grep function works with fast-glob prefilter"""
    from tunacode.tools.grep import grep
    
    # Test searching for a pattern we know exists
    result = await grep("import", ".", include_files="*.py", max_results=5)
    
    assert isinstance(result, str), "grep should return a string"
    assert "Found" in result or "No matches" in result, "Result should indicate search status"
    
    # If we found matches, check they contain our search pattern
    if "Found" in result:
        assert "Strategy:" in result, "Result should show which strategy was used"
        assert "Candidates:" in result, "Result should show candidate count"

@pytest.mark.asyncio
async def test_smart_strategy_selection():
    """Test that smart strategy selection works based on candidate count"""
    from tunacode.tools.grep import ParallelGrep
    
    # Create grep tool instance
    grep_tool = ParallelGrep()
    
    # Test with very specific pattern (should find few files)
    result_few = await grep_tool._execute(
        "test_", ".", include_files="test_*.py", search_type="smart", max_results=10
    )
    
    # Should use python strategy for small sets
    assert "Strategy: python" in result_few, "Should use python strategy for small candidate sets"
    
    # Test with broader pattern (more files)
    result_many = await grep_tool._execute(
        "import", ".", include_files="*.py", search_type="smart", max_results=10
    )
    
    # Should show some strategy was selected
    assert "Strategy:" in result_many, "Should show strategy selection"

def test_bounded_results():
    """Test that results are properly bounded by MAX_GLOB"""
    from tunacode.tools.grep import fast_glob, MAX_GLOB
    
    root = Path(".")
    
    # Test that we don't exceed MAX_GLOB even with broad pattern
    all_files = fast_glob(root, "*")
    
    assert len(all_files) <= MAX_GLOB, f"Results should be bounded by MAX_GLOB ({MAX_GLOB})"

# Remove the main() function and if __name__ block since pytest will handle test discovery and execution