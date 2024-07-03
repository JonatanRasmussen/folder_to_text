import os
from typing import Dict, Set

class FolderSerializer:
    def __init__(self, blacklist: Dict[str, Set[str]], whitelist: Dict[str, Set[str]]):
        self.blacklist = blacklist
        self.whitelist = whitelist
        self.folder_path = ""
        self.output = ""
        self.traversed_files = 0
        self.skipped_files = 0
        self.read_errors = 0

    def execute(self, input_name: str, output_name: str) -> None:
        self._read_input(input_name)
        self._serialize_folder()
        self._write_output(output_name)

    def _read_input(self, file_name: str) -> None:
        try:
            with open(file_name, 'r') as f:
                self.folder_path = f.read().strip()
        except FileNotFoundError:
            print(f"Error: {file_name} file not found.")
        except Exception as e:
            print(f"Error reading {file_name}: {str(e)}")

    def _write_output(self, file_name: str) -> None:
        try:
            with open(file_name, 'w', encoding='utf-8') as f:
                f.write(self.output)
            print(f"Output successfully written to {file_name}\n")
        except Exception as e:
            print(f"Error writing to {file_name} {str(e)}\n")

    def _serialize_folder(self) -> None:
        if not self.folder_path or not os.path.exists(self.folder_path):
            print(f"The path '{self.folder_path}' does not exist.")
            return

        hierarchy = self._get_hierarchy()
        self.output = "Folder hierarchy:\n\n" + hierarchy + "\n\n"

        for root, dirs, files in os.walk(self.folder_path):
            # Filter folders
            dirs[:] = [d for d in dirs if self._should_process_folder(d)]

            for file in files:
                file_path = os.path.join(root, file)
                relative_path = os.path.relpath(file_path, self.folder_path)

                if not self._should_process_file(file):
                    self.skipped_files += 1
                    continue

                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        self.output += f"\n\n--- Start of File: {relative_path} ---\n\n"
                        self.output += f.read()
                        self.output += f"\n\n--- End of File: {relative_path} ---\n\n"
                        self.traversed_files += 1
                except Exception as e:
                    self.read_errors += 1
                    print(f"Error reading file {file_path}: {str(e)}")

        self._print_summary()

    def _print_summary(self) -> None:
        print(f"\nSuccess! Length of output: {len(self.output)} characters")
        print(f"Errors: {self.read_errors}")
        print(f"Files Read: {self.traversed_files}")
        print(f"Skipped: {self.skipped_files}")

    def _get_hierarchy(self, current_path: str = "", prefix: str = "") -> str:
        if not current_path:
            current_path = self.folder_path

        if not os.path.exists(current_path):
            return f"The path {current_path} does not exist."

        hierarchy = ""
        folder_name = os.path.basename(current_path)
        if self._should_process_folder(folder_name):
            hierarchy += f"{prefix}{folder_name}/\n"
            prefix += "  "

            for item in sorted(os.listdir(current_path)):
                item_path = os.path.join(current_path, item)
                if os.path.isdir(item_path):
                    hierarchy += self._get_hierarchy(item_path, prefix)
                else:
                    if self._should_process_file(item):
                        hierarchy += f"{prefix}{item}\n"

        return hierarchy

    def _should_process_folder(self, folder_name: str) -> bool:
        if self.whitelist['folders'] and folder_name not in self.whitelist['folders']:
            return False
        return folder_name not in self.blacklist['folders']

    def _should_process_file(self, file_name: str) -> bool:
        file_extension = os.path.splitext(file_name)[-1].lower()

        # Check file extension
        if self.whitelist['extensions'] and file_extension not in self.whitelist['extensions']:
            return False
        if file_extension in self.blacklist['extensions']:
            return False

        # Check specific file
        if self.whitelist['files'] and file_name not in self.whitelist['files']:
            return False
        if file_name in self.blacklist['files']:
            return False

        return True