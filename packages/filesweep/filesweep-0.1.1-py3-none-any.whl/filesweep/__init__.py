"""
FileSweep - A tool for managing and organizing files in a directory.
"""

import argparse
from filesweep.cleaner import FileCleaner
from filesweep.scanner import FileScanner

def main():
    """Entry point for the FileSweep package when used as a command-line tool."""
    parser = argparse.ArgumentParser(description="FileSweep: File management and organization tool")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Clean command
    clean_parser = subparsers.add_parser("clean", help="Clean files matching a pattern")
    clean_parser.add_argument("directory", help="Directory to clean")
    clean_parser.add_argument("pattern", help="File pattern to match (e.g., '*.tmp')")
    
    # Scan command
    scan_parser = subparsers.add_parser("scan", help="Scan directory and export file information")
    scan_parser.add_argument("directory", help="Directory to scan")
    scan_parser.add_argument("--format", choices=["json", "csv", "xml"], default="json", help="Export format")
    scan_parser.add_argument("--output", help="Output file path")
    
    args = parser.parse_args()
    
    if args.command == "clean":
        cleaner = FileCleaner(args.directory)
        cleaner.clean_files(args.pattern)
    elif args.command == "scan":
        scanner = FileScanner(args.directory)
        output_file = args.output or f"file_data.{args.format}"
        
        if args.format == "json":
            scanner.export_to_json(output_file)
        elif args.format == "csv":
            scanner.export_to_csv(output_file)
        elif args.format == "xml":
            scanner.export_to_xml(output_file)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()