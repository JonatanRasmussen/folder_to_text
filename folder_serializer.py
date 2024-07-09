import os
import json
from typing import Dict, Set, ClassVar
from dataclasses import dataclass

@dataclass
class FolderSerializer:
    """
    A class for serializing any folders content. Supports blacklist/whitelist.
    """

    @staticmethod
    def main(config_name: str) -> None:
        """
        Serialize folder in 'config_name'.json and write output to 'config_name'.txt
        """
        config_path = os.path.join(FolderSerializer._INPUT_FOLDER, f"{config_name}.json")
        serializer = FolderSerializer.create_from_config(config_path)
        serializer.serialize_folder()
        serializer.print_summary()
        output_path = os.path.join(FolderSerializer._OUTPUT_FOLDER, f"{config_name}.txt")
        serializer.write_output(output_path)


    ###########################
    ### PRIVATE CLASS STUFF ###
    ###########################

    # Hardcoded values for input/output folders
    _INPUT_FOLDER = "program_inputs"
    _OUTPUT_FOLDER = "program_outputs"

    # Keys used in config.json
    _FOLDER_TO_SERIALIZE = 'folder_to_serialize'
    _BLACKLIST = 'blacklist'
    _WHITELIST = 'whitelist'
    _CONFIG_EXTENSIONS = 'extensions'
    _CONFIG_FILES = 'files'
    _CONFIG_FOLDERS = 'folders'

    # File extensions that are blacklisted by default
    _BINARY_FILE_EXTENSIONS: ClassVar[Set[str]] = {
        '.png', '.jpg', '.jpeg', '.gif',
        '.bmp', '.exe', '.pdf',  # More can be added
    }

    # Class fields
    folder_to_serialize: str
    _blacklist: Dict[str, Set[str]]
    _whitelist: Dict[str, Set[str]]
    _output_path: str = ""
    _folder_content_as_str: str = ""
    _traversed_files: int = 0
    _skipped_files: int = 0
    _binary_files: int = 0
    _read_errors: int = 0
    _hierarchy: str = ""


    # Some of the following methods are public due to being called
    # from the testing script. Just think of them as private

    @classmethod
    def create_from_config(cls, config_path: str) -> 'FolderSerializer':
        # Load config json
        with open(config_path, 'r') as f:
            config = json.load(f)
        # Convert blacklist / whitelist from list to set
        for list_type in [cls._BLACKLIST, cls._WHITELIST]:
            for key in config[list_type]:
                config[list_type][key] = set(config[list_type][key])
        # Create class instance from config
        return cls(
            folder_to_serialize=config[cls._FOLDER_TO_SERIALIZE],
            _blacklist=config[cls._BLACKLIST],
            _whitelist=config[cls._WHITELIST],
        )

    def print_summary(self) -> None:
        print(self._hierarchy)
        print(f"Success! Length of output: {len(self._folder_content_as_str)} characters")
        print(f"Errors: {self._read_errors}")
        print(f"Binaries: {self._binary_files}")
        print(f"Files Read: {self._traversed_files}")
        print(f"Skipped: {self._skipped_files}")

    def write_output(self, output_path: str) -> None:
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(self._folder_content_as_str)
            print(f"Output successfully written to {output_path}\n")
        except Exception as e:
            print(f"BudoError writing to {output_path} {str(e)}\n")

    def serialize_folder(self) -> None:
        if not self.folder_to_serialize or not os.path.exists(self.folder_to_serialize):
            error_msg = f"The path '{self.folder_to_serialize}' does not exist. Go to your config json file and set a valid path.\n"
            print(error_msg)
            self._folder_content_as_str = error_msg
            return

        hierarchy = self._get_hierarchy()
        hierarchy_with_title = "Folder hierarchy:\n\n" + hierarchy + "\n"
        self._hierarchy = hierarchy_with_title
        self._folder_content_as_str = hierarchy_with_title

        for root, dirs, files in os.walk(self.folder_to_serialize):
            # Filter folders
            dirs[:] = [d for d in dirs if self._should_process_folder(d)]

            for file in files:
                file_path = os.path.join(root, file)
                relative_path = os.path.relpath(file_path, self.folder_to_serialize)

                if not self._should_process_file(file):
                    self._skipped_files += 1
                    continue

                file_extension = os.path.splitext(file)[-1].lower()
                if file_extension in self._BINARY_FILE_EXTENSIONS:
                    self._folder_content_as_str += f"\n\n--- Start of File: {relative_path} ---\n\n"
                    self._folder_content_as_str += "[Binary file - NOT DISPLAYED]"
                    self._folder_content_as_str += f"\n\n--- End of File: {relative_path} ---\n\n"
                    self._binary_files += 1
                else:
                    try:
                        with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                            self._folder_content_as_str += f"\n\n--- Start of File: {relative_path} ---\n\n"
                            self._folder_content_as_str += f.read()
                            self._folder_content_as_str += f"\n\n--- End of File: {relative_path} ---\n\n"
                            self._traversed_files += 1
                    except Exception as e:
                        self._read_errors += 1
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
                    elif file_extension in self._BINARY_FILE_EXTENSIONS:
                        hierarchy += f"{prefix}{item} {file_binary}\n"
                    else:
                        hierarchy += f"{prefix}{item}\n"

        return hierarchy

    def _should_process_folder(self, folder_name: str) -> bool:
        if self._whitelist[self._CONFIG_FOLDERS] and folder_name not in self._whitelist[self._CONFIG_FOLDERS]:
            return False
        return folder_name not in self._blacklist[self._CONFIG_FOLDERS]

    def _should_process_file(self, file_name: str) -> bool:
        # Check file extension
        file_extension = os.path.splitext(file_name)[-1].lower()
        if self._whitelist[self._CONFIG_EXTENSIONS] and file_extension not in self._whitelist[self._CONFIG_EXTENSIONS]:
            return False
        if file_extension in self._blacklist[self._CONFIG_EXTENSIONS]:
            return False
        # Check specific file (e.g. hello_world.py)
        file_name_without_extension = os.path.splitext(file_name)[0]
        if self._whitelist[self._CONFIG_FILES] and file_name not in self._whitelist[self._CONFIG_FILES]:
            # Try without extension (e.g. hello_world)
            if self._whitelist[self._CONFIG_FILES] and file_name_without_extension not in self._whitelist[self._CONFIG_FILES]:
                return False
        if file_name in self._blacklist[self._CONFIG_FILES] or file_name_without_extension in self._blacklist[self._CONFIG_FILES] :
            return False
        return True


#######################
### TESTING SECTION ###
#######################

class FolderSerializerTesting:
    """
    This class is used ONLY for testing of FolderSerializer
    """

    @staticmethod
    def main() -> None:
        """
        Test FolderSerializer with dummy data
        """
        config_path = FolderSerializerTesting._load_testing_config()
        serializer = FolderSerializer.create_from_config(config_path)
        serializer.folder_to_serialize = FolderSerializerTesting._testing_folder_to_serialize()
        serializer.serialize_folder()
        output = FolderSerializerTesting._generate_path_to_test_output()
        serializer.write_output(output)
        FolderSerializerTesting._verify_test_output()


    ###########################
    ### PRIVATE CLASS STUFF ###
    ###########################

    # Folder paths for testing
    _FOLDER_USED_TO_TEST_PROGRAM = "folder_used_to_test_program"
    _FOLDER_TO_SERIALIZE_DURING_TEST = "folder_to_be_serialized"

    # Files used for testing
    _TEST_INPUT_FILE = "test_configs.json"
    _TEST_OUTPUT_FILE = "test_output.txt"
    _EXPECTED_TEST_OUTPUT_FILE = "expected_test_output.txt"

    @staticmethod
    def _load_testing_config() -> str:
        folder = FolderSerializerTesting._FOLDER_USED_TO_TEST_PROGRAM
        file = FolderSerializerTesting._TEST_INPUT_FILE
        local_path = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(local_path, folder, file)

    @staticmethod
    def _generate_path_to_test_output() -> str:
        folder = FolderSerializerTesting._FOLDER_USED_TO_TEST_PROGRAM
        file = FolderSerializerTesting._TEST_OUTPUT_FILE
        local_path = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(local_path, folder, file)

    @staticmethod
    def _testing_folder_to_serialize() -> str:
        test_folder = FolderSerializerTesting._FOLDER_USED_TO_TEST_PROGRAM
        folder_to_serialize = FolderSerializerTesting._FOLDER_TO_SERIALIZE_DURING_TEST
        local_path = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(local_path, test_folder, folder_to_serialize)

    @staticmethod
    def _generate_path_to_expected_test_output() -> str:
        folder = FolderSerializerTesting._FOLDER_USED_TO_TEST_PROGRAM
        file = FolderSerializerTesting._EXPECTED_TEST_OUTPUT_FILE
        local_path = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(local_path, folder, file)

    @staticmethod
    def _verify_test_output() -> None:
        output_path = FolderSerializerTesting._generate_path_to_test_output()
        with open(output_path, 'r') as f:
            output = f.read()

        expected_output_path = FolderSerializerTesting._generate_path_to_expected_test_output()
        with open(expected_output_path, 'r') as f:
            expected_output = f.read()

        msg_output = f"{FolderSerializerTesting._TEST_OUTPUT_FILE} ({len(output)} characters)"
        msg_expected = f"{FolderSerializerTesting._EXPECTED_TEST_OUTPUT_FILE} ({len(expected_output)} characters)"
        if output == expected_output:
            print(f"Test passed! {msg_output} == {msg_expected}...\n")
        else:
            print(f"Test failed! {msg_output} != {msg_expected}")
            print(f"Investigate output at {output_path}")


#%%
if __name__ == "__main__":
    # Test run
    FolderSerializerTesting.main()

    # Actual run
    my_config_name = "self" # Input name of config file that should be loaded
    FolderSerializer.main(my_config_name)