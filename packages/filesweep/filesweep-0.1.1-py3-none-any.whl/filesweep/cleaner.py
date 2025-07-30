import os
import fnmatch


class FileCleaner:
    def __init__(self, directory):
        self.directory = directory

    def clean_files(self, pattern):
        """Removes files matching the specified pattern."""
        deleted_files = []
        for root, _, files in os.walk(self.directory):
            for file in files:
                if fnmatch.fnmatch(file, pattern):
                    file_path = os.path.join(root, file)
                    try:
                        os.remove(file_path)
                        deleted_files.append(file_path)
                        print(f"Removed {file} -> {file_path}")
                    except Exception as e:
                        print(f"Error removing {file} -> {file_path}: {e}")

        print(f"Deleted {len(deleted_files)} files matching '{pattern}'")
        return deleted_files


# Usage Example:
if __name__ == "__main__":
    cleaner = FileCleaner(r"C:\Users\raksh\Music\Projects\PyPi Projects\FileSweep")
    cleaner.clean_files("file_data*.*")  # Example: Deletes all '.log' files
