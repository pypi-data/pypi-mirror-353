import os
import sys
import json
import pytest
from unittest.mock import patch
from io import StringIO
from filesweep import main


def test_main_scan_command(temp_dir, test_files):
    """Test the main scan command functionality."""
    output_file = os.path.join(temp_dir, "output.json")
    
    # Mock sys.argv
    test_args = ["filesweep", "scan", temp_dir, "--output", output_file]
    with patch.object(sys, "argv", test_args):
        # Capture stdout
        captured_stdout = StringIO()
        with patch("sys.stdout", captured_stdout):
            main()
    
    # Check that the output file was created
    assert os.path.exists(output_file)
    
    # Load the JSON to verify contents
    with open(output_file, 'r') as f:
        data = json.load(f)
    
    # Check that we have the right number of files
    assert len(data) == len(test_files)


def test_main_clean_command(temp_dir, test_files):
    """Test the main clean command functionality."""
    # Assert that test3.tmp exists before cleaning
    assert os.path.exists(test_files["test3.tmp"])
    
    # Mock sys.argv
    test_args = ["filesweep", "clean", temp_dir, "*.tmp"]
    with patch.object(sys, "argv", test_args):
        # Capture stdout
        captured_stdout = StringIO()
        with patch("sys.stdout", captured_stdout):
            main()
    
    # Check that the tmp file was deleted
    assert not os.path.exists(test_files["test3.tmp"])
    
    # Other files should still exist
    assert os.path.exists(test_files["test1.txt"])
    assert os.path.exists(test_files["test2.log"])
    assert os.path.exists(test_files["test4.py"])


def test_main_no_args():
    """Test main function with no arguments (should show help)."""
    # Mock empty sys.argv
    test_args = ["filesweep"]
    with patch.object(sys, "argv", test_args):
        # Capture stdout
        captured_stdout = StringIO()
        with patch("sys.stdout", captured_stdout):
            main()
    
    # Should contain help message
    output = captured_stdout.getvalue()
    assert "usage:" in output.lower()
    assert "filesweep" in output
