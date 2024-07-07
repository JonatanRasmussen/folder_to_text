import os
from typing import Dict, Set, Any
from global_configs import GlobalConfigs

class FolderSerializer:

    BINARY_FILE_EXTENSIONS = {
        '.png', '.jpg', '.jpeg', '.gif',
        '.bmp', '.exe', '.pdf',
    }

    def __init__(self, folder_to_serialize: str, where_to_write_output: str, blacklist: Dict[str, Set[str]], whitelist: Dict[str, Set[str]]):
        self.blacklist = blacklist
        self.whitelist = whitelist
        self.folder_to_serialize = folder_to_serialize
        self.where_to_write_output = where_to_write_output
        self.folder_content_as_str = ""
        self.traversed_files = 0
        self.skipped_files = 0
        self.binary_files = 0
        self.read_errors = 0
        self.hierarchy = ""
        self.running_special_testing_config = False

    @classmethod
    def create_from_config(cls, config_name: str):
        config = GlobalConfigs.load_config(config_name)
        folder_to_serialize = config[GlobalConfigs.FOLDER_TO_SERIALIZE]
        where_to_write_output = GlobalConfigs.generate_output_path(config_name)
        blacklist = config[GlobalConfigs.BLACKLIST]
        whitelist = config[GlobalConfigs.WHITELIST]
        serializer = FolderSerializer(folder_to_serialize, where_to_write_output, blacklist, whitelist)
        if GlobalConfigs.is_test_run(config_name):
            serializer.running_special_testing_config = True
            serializer.folder_to_serialize = GlobalConfigs.locate_testing_folder_to_serialize()
        return serializer

    @staticmethod
    def create_and_execute_test_run() -> None:
        config_name = GlobalConfigs.PROGRAM_INPUT_TO_RUN_TEST
        serializer = FolderSerializer.create_from_config(config_name)
        serializer.serialize_folder()
        serializer.write_output()
        GlobalConfigs.verify_test_output()

    @staticmethod
    def create_and_execute_from_config(config_name: str) -> None:
        serializer = FolderSerializer.create_from_config(config_name)
        serializer.serialize_folder()
        serializer.print_summary()
        serializer.write_output()


    def _read_input(self, file_name: str) -> None:
        try:
            with open(file_name, 'r') as f:
                self.folder_to_serialize = f.read().strip()
        except FileNotFoundError:
            print(f"Error: {file_name} file not found.")
        except Exception as e:
            print(f"Error reading {file_name}: {str(e)}")

    def write_output(self) -> None:
        file_name = self.where_to_write_output
        try:
            with open(file_name, 'w', encoding='utf-8') as f:
                f.write(self.folder_content_as_str)
            print(f"Output successfully written to {file_name}\n")
        except Exception as e:
            print(f"Error writing to {file_name} {str(e)}\n")

    def serialize_folder(self) -> None:
        if not self.folder_to_serialize or not os.path.exists(self.folder_to_serialize):
            error_msg = f"The path '{self.folder_to_serialize}' does not exist. Go to your config json file and set a valid path.\n"
            print(error_msg)
            self.folder_content_as_str = error_msg
            return

        hierarchy = self._get_hierarchy()
        hierarchy_with_title = "Folder hierarchy:\n\n" + hierarchy + "\n"
        self.hierarchy = hierarchy_with_title
        self.folder_content_as_str = hierarchy_with_title

        for root, dirs, files in os.walk(self.folder_to_serialize):
            # Filter folders
            dirs[:] = [d for d in dirs if self._should_process_folder(d)]

            for file in files:
                file_path = os.path.join(root, file)
                relative_path = os.path.relpath(file_path, self.folder_to_serialize)

                if not self._should_process_file(file):
                    self.skipped_files += 1
                    continue

                file_extension = os.path.splitext(file)[-1].lower()
                if file_extension in self.BINARY_FILE_EXTENSIONS:
                    self.folder_content_as_str += f"\n\n--- Start of File: {relative_path} ---\n\n"
                    self.folder_content_as_str += "[Binary file - NOT DISPLAYED]"
                    self.folder_content_as_str += f"\n\n--- End of File: {relative_path} ---\n\n"
                    self.binary_files += 1
                else:
                    try:
                        with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                            self.folder_content_as_str += f"\n\n--- Start of File: {relative_path} ---\n\n"
                            self.folder_content_as_str += f.read()
                            self.folder_content_as_str += f"\n\n--- End of File: {relative_path} ---\n\n"
                            self.traversed_files += 1
                    except Exception as e:
                        self.read_errors += 1
                        print(f"Error reading file {file_path}: {str(e)}")

    def print_summary(self) -> None:
        print(self.hierarchy)
        print(f"Success! Length of output: {len(self.folder_content_as_str)} characters")
        print(f"Errors: {self.read_errors}")
        print(f"Binaries: {self.binary_files}")
        print(f"Files Read: {self.traversed_files}")
        print(f"Skipped: {self.skipped_files}")

    def _get_hierarchy(self, current_path: str = "", prefix: str = "") -> str:
        file_skipped = "(NOT FEATURED)"
        file_binary = "(BINARY FILE)"
        if not current_path:
            current_path = self.folder_to_serialize

        if not os.path.exists(current_path):
            return f"The path {current_path} does not exist."

        hierarchy = ""
        folder_name = os.path.basename(current_path)
        if not self._should_process_folder(folder_name):
            hierarchy += f"{prefix}{folder_name}/ {file_skipped}\n"
        else:
            hierarchy += f"{prefix}{folder_name}/\n"
            prefix += "  "

            for item in sorted(os.listdir(current_path)):
                item_path = os.path.join(current_path, item)
                if os.path.isdir(item_path):
                    hierarchy += self._get_hierarchy(item_path, prefix)
                else:
                    file_extension = os.path.splitext(item)[-1].lower()
                    if not self._should_process_file(item):
                        hierarchy += f"{prefix}{item} {file_skipped}\n"
                    elif file_extension in self.BINARY_FILE_EXTENSIONS:
                        hierarchy += f"{prefix}{item} {file_binary}\n"
                    else:
                        hierarchy += f"{prefix}{item}\n"

        return hierarchy

    def _should_process_folder(self, folder_name: str) -> bool:
        if self.whitelist['folders'] and folder_name not in self.whitelist['folders']:
            return False
        return folder_name not in self.blacklist['folders']

    def _should_process_file(self, file_name: str) -> bool:

        # Check file extension
        file_extension = os.path.splitext(file_name)[-1].lower()
        if self.whitelist['extensions'] and file_extension not in self.whitelist['extensions']:
            return False
        if file_extension in self.blacklist['extensions']:
            return False

        # Check specific file (e.g. hello_world.py)
        file_name_without_extension = os.path.splitext(file_name)[0]
        if self.whitelist['files'] and file_name not in self.whitelist['files']:
            # Try without extension (e.g. hello_world)
            if self.whitelist['files'] and file_name_without_extension not in self.whitelist['files']:
                return False
        if (file_name or file_name_without_extension) in self.blacklist['files']:
            return False

        return True