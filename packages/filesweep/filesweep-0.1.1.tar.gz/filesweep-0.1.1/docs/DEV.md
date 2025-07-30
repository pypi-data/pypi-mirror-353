## Planning
### File structure

```
FileSweep/
│── filesweep/               # Main package directory
│   │── __init__.py          # Init file for package
│   │── cleaner.py           # Handles file deletion
│   │── scanner.py           # Exports file details
│   │── utils.py             # Helper functions
│── tests/                   # Unit tests for modules
│   │── test_cleaner.py      # Tests for file cleanup
│   │── test_scanner.py      # Tests for scanning/exporting
│── setup.py                 # Package setup script
│── README.md                # Documentation
│── requirements.txt         # Dependencies list
```