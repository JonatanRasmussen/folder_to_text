import os
from typing import Dict, Set, ClassVar
from persistence import Persistence
from dataclasses import dataclass

@dataclass
class FolderSerializer:
    """ A class for serializing folder contents with customizable filters. """

    BINARY_FILE_EXTENSIONS: ClassVar[Set[str]] = {
        '.png', '.jpg', '.jpeg', '.gif',
        '.bmp', '.exe', '.pdf',  # More can be added
    }

    folder_to_serialize: str
    blacklist: Dict[str, Set[str]]
    whitelist: Dict[str, Set[str]]
    output_path: str = ""
    folder_content_as_str: str = ""
    traversed_files: int = 0
    skipped_files: int = 0
    binary_files: int = 0
    read_errors: int = 0
    hierarchy: str = ""

    @staticmethod
    def main(config_name: str) -> None:
        """
        Serialize the content of the folder specified in 'config_name'.json
        Write output to 'config_name'.txt
        """
        config_path = Persistence.generate_path_to_config(config_name)
        serializer = FolderSerializer.create_from_config(config_path)
        serializer.serialize_folder()
        serializer.print_summary()
        output_path = Persistence.generate_path_to_output(config_name)
        serializer.write_output(output_path)

    @classmethod
    def create_from_config(cls, config_path: str) -> 'FolderSerializer':
        config = Persistence.load_config(config_path)
        return cls(
            folder_to_serialize=config[Persistence.FOLDER_TO_SERIALIZE],
            blacklist=config[Persistence.BLACKLIST],
            whitelist=config[Persistence.WHITELIST],
        )

    def print_summary(self) -> None:
        print(self.hierarchy)
        print(f"Success! Length of output: {len(self.folder_content_as_str)} characters")
        print(f"Errors: {self.read_errors}")
        print(f"Binaries: {self.binary_files}")
        print(f"Files Read: {self.traversed_files}")
        print(f"Skipped: {self.skipped_files}")

    def write_output(self, output_path: str) -> None:
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(self.folder_content_as_str)
            print(f"Output successfully written to {output_path}\n")
        except Exception as e:
            print(f"BudoError writing to {output_path} {str(e)}\n")

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
        if self.whitelist[Persistence.CONFIG_FOLDERS] and folder_name not in self.whitelist[Persistence.CONFIG_FOLDERS]:
            return False
        return folder_name not in self.blacklist[Persistence.CONFIG_FOLDERS]

    def _should_process_file(self, file_name: str) -> bool:

        # Check file extension
        file_extension = os.path.splitext(file_name)[-1].lower()
        if self.whitelist[Persistence.CONFIG_EXTENSIONS] and file_extension not in self.whitelist[Persistence.CONFIG_EXTENSIONS]:
            return False
        if file_extension in self.blacklist[Persistence.CONFIG_EXTENSIONS]:
            return False

        # Check specific file (e.g. hello_world.py)
        file_name_without_extension = os.path.splitext(file_name)[0]
        if self.whitelist[Persistence.CONFIG_FILES] and file_name not in self.whitelist[Persistence.CONFIG_FILES]:
            # Try without extension (e.g. hello_world)
            if self.whitelist[Persistence.CONFIG_FILES] and file_name_without_extension not in self.whitelist[Persistence.CONFIG_FILES]:
                return False
        if file_name in self.blacklist[Persistence.CONFIG_FILES] or file_name_without_extension in self.blacklist[Persistence.CONFIG_FILES] :
            return False

        return True

if __name__ == "__main__":
    my_config_name = "self" # Input name of config file that should be loaded
    FolderSerializer.main(my_config_name)