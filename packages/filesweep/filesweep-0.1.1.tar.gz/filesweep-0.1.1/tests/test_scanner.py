import os
import json
import csv
import xml.etree.ElementTree as ET
import pytest
from filesweep.scanner import FileScanner


def test_scanner_initialization():
    """Test that scanner initializes correctly."""
    scanner = FileScanner("/test/path")
    assert scanner.directory == "/test/path"


def test_scan(temp_dir, test_files):
    """Test that scan method collects file details correctly."""
    scanner = FileScanner(temp_dir)
    file_data = scanner.scan()
    
    # Check we have the correct number of files
    assert len(file_data) == len(test_files)
    
    # Check that each file in our test_files is in the scan results
    for filename in test_files:
        file_path = test_files[filename]
        matching_files = [file for file in file_data if file["path"] == file_path]
        assert len(matching_files) == 1
        
        file_info = matching_files[0]
        assert file_info["name"] == filename
        assert file_info["path"] == file_path
        assert isinstance(file_info["size"], int)
        assert isinstance(file_info["modified_time"], float)


def test_export_to_json(temp_dir, test_files):
    """Test JSON export functionality."""
    scanner = FileScanner(temp_dir)
    output_file = os.path.join(temp_dir, "test_output.json")
    
    scanner.export_to_json(output_file)
    
    # Check that file was created
    assert os.path.exists(output_file)
    
    # Check that the content is valid JSON and has the right structure
    with open(output_file, "r") as f:
        data = json.load(f)
        
    assert isinstance(data, list)
    assert len(data) == len(test_files)
    
    # Check that each exported file has the required fields
    for file_info in data:
        assert "name" in file_info
        assert "path" in file_info
        assert "size" in file_info
        assert "modified_time" in file_info


def test_export_to_csv(temp_dir, test_files):
    """Test CSV export functionality."""
    scanner = FileScanner(temp_dir)
    output_file = os.path.join(temp_dir, "test_output.csv")
    
    scanner.export_to_csv(output_file)
    
    # Check that file was created
    assert os.path.exists(output_file)
    
    # Check that the content is valid CSV and has the right structure
    with open(output_file, "r", newline="") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        
    assert len(rows) == len(test_files)
    
    # Check that each exported file has the required fields
    for row in rows:
        assert "name" in row
        assert "path" in row
        assert "size" in row
        assert "modified_time" in row


def test_export_to_xml(temp_dir, test_files):
    """Test XML export functionality."""
    scanner = FileScanner(temp_dir)
    output_file = os.path.join(temp_dir, "test_output.xml")
    
    scanner.export_to_xml(output_file)
    
    # Check that file was created
    assert os.path.exists(output_file)
    
    # Check that the content is valid XML and has the right structure
    tree = ET.parse(output_file)
    root = tree.getroot()
    
    assert root.tag == "files"
    file_elements = root.findall("file")
    assert len(file_elements) == len(test_files)
    
    # Check that each exported file has the required fields
    for file_element in file_elements:
        assert file_element.find("name") is not None
        assert file_element.find("path") is not None
        assert file_element.find("size") is not None
        assert file_element.find("modified_time") is not None
