import os
import pytest
from filesweep.cleaner import FileCleaner


def test_cleaner_initialization():
    """Test that cleaner initializes correctly."""
    cleaner = FileCleaner("/test/path")
    assert cleaner.directory == "/test/path"


def test_clean_files(temp_dir, test_files):
    """Test that clean_files method removes files matching the pattern."""
    cleaner = FileCleaner(temp_dir)
    
    # Count initial files
    initial_count = len(os.listdir(temp_dir))
    assert initial_count == 4  # We created 4 files in the test_files fixture
    
    # Clean .log files
    deleted_files = cleaner.clean_files("*.log")
    
    # Check that we deleted 1 file (test2.log)
    assert len(deleted_files) == 1
    assert os.path.basename(deleted_files[0]) == "test2.log"
    
    # Check that the file is really gone
    remaining_files = os.listdir(temp_dir)
    assert len(remaining_files) == initial_count - 1
    assert "test2.log" not in remaining_files
    
    # Check that other files still exist
    assert "test1.txt" in remaining_files
    assert "test3.tmp" in remaining_files
    assert "test4.py" in remaining_files


def test_clean_multiple_patterns(temp_dir, test_files):
    """Test cleaning multiple file patterns."""
    cleaner = FileCleaner(temp_dir)
    
    # First clean .tmp files
    deleted_tmp = cleaner.clean_files("*.tmp")
    assert len(deleted_tmp) == 1
    assert "test3.tmp" not in os.listdir(temp_dir)
    
    # Then clean .py files
    deleted_py = cleaner.clean_files("*.py")
    assert len(deleted_py) == 1
    assert "test4.py" not in os.listdir(temp_dir)
    
    # Check total remaining files
    remaining_files = os.listdir(temp_dir)
    assert len(remaining_files) == 2
    assert set(remaining_files) == {"test1.txt", "test2.log"}


def test_clean_nonexistent_pattern(temp_dir, test_files):
    """Test cleaning with a pattern that doesn't match any files."""
    cleaner = FileCleaner(temp_dir)
    
    # Clean a pattern that doesn't exist
    deleted_files = cleaner.clean_files("*.jpg")
    
    # No files should be deleted
    assert len(deleted_files) == 0
    
    # All test files should still exist
    remaining_files = os.listdir(temp_dir)
    assert len(remaining_files) == 4
