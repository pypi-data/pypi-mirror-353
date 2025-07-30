import os
import json
import csv
import xml.etree.ElementTree as ET
import xml.dom.minidom


class FileScanner:
    def __init__(self, directory):
        self.directory = directory

    def scan(self):
        """Scan directory and collect file details."""
        file_data = []
        for root, _, files in os.walk(self.directory):
            for file in files:
                file_path = os.path.join(root, file)
                file_info = {
                    "name": file,
                    "path": file_path,
                    "size": os.path.getsize(file_path),
                    "modified_time": os.path.getmtime(file_path)
                }
                file_data.append(file_info)
        return file_data

    def export_to_json(self, output_file="file_data.json"):
        """Export file details to JSON."""
        data = self.scan()
        with open(output_file, "w") as f:
            json.dump(data, f, indent=4)
        print(f"File data exported to {output_file}")

    def export_to_csv(self, output_file="file_data.csv"):
        """Export file details to CSV."""
        data = self.scan()
        with open(output_file, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=["name", "path", "size", "modified_time"])
            writer.writeheader()
            writer.writerows(data)
        print(f"File data exported to {output_file}")

    def export_to_xml(self, output_file="file_data.xml"):
        """Export file details to a well-formatted XML."""
        data = self.scan()
        root = ET.Element("files")

        for file_info in data:
            file_element = ET.SubElement(root, "file")
            for key, value in file_info.items():
                ET.SubElement(file_element, key).text = str(value)

        # Format XML with indentation
        rough_string = ET.tostring(root, 'utf-8')
        pretty_xml = xml.dom.minidom.parseString(rough_string).toprettyxml(indent="    ")

        with open(output_file, "w", encoding="utf-8") as f:
            f.write(pretty_xml)

        print(f"File data exported to {output_file}")


# Usage Example:
if __name__ == "__main__":
    scanner = FileScanner(r"C:\Users\raksh\Music\Projects\PyPi Projects\FileSweep")
    scanner.export_to_json()
    scanner.export_to_csv()
    scanner.export_to_xml()
