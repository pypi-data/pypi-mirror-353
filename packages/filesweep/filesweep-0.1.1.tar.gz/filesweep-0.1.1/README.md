# FileSweep

![PyPI Version](https://img.shields.io/pypi/v/filesweep)
![Python Version](https://img.shields.io/pypi/pyversions/filesweep)
![License](https://img.shields.io/pypi/l/filesweep)

FileSweep is a powerful tool for managing, scanning, and organizing files in directories. It offers both file scanning with multiple export formats and pattern-based file cleaning capabilities.

## Installation

```bash
pip install filesweep
```

## Features

- **File Scanning**: Scan directories to collect detailed file information
- **Multiple Export Formats**: Export file data in JSON, CSV, or XML format
- **Pattern-Based Cleaning**: Remove files matching specific patterns
- **Command Line Interface**: Easy-to-use CLI for all operations
- **Python API**: Can be used as a library in your Python projects

## Usage

### Command Line Interface

#### Scanning files and exporting data

```bash
# Export file data to JSON (default)
filesweep scan /path/to/directory

# Export to CSV
filesweep scan /path/to/directory --format csv

# Export to XML with custom output path
filesweep scan /path/to/directory --format xml --output my_files.xml
```

#### Cleaning files by pattern

```bash
# Remove all temporary files
filesweep clean /path/to/directory "*.tmp"

# Remove all log files
filesweep clean /path/to/directory "*.log"
```

### Python API

```python
from filesweep.scanner import FileScanner
from filesweep.cleaner import FileCleaner

# Scan files and export data
scanner = FileScanner("/path/to/directory")
scanner.export_to_json("file_data.json")  # or export_to_csv, export_to_xml

# Clean files matching a pattern
cleaner = FileCleaner("/path/to/directory")
deleted_files = cleaner.clean_files("*.tmp")
print(f"Cleaned {len(deleted_files)} files")
```

## Documentation

For more detailed documentation, see the [docs](docs/) directory.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Author

- Rakshith Kalmadi - [GitHub](https://github.com/rakshithkalmadi)

