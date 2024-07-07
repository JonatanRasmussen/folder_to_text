import os
import json
from typing import Dict, Any

class GlobalConfigs:

    # folder paths
    INPUT_FOLDER = "program_inputs"
    OUTPUT_FOLDER = "program_outputs"

    # names used in config.json
    FOLDER_TO_SERIALIZE = 'folder_to_serialize'
    BLACKLIST = 'blacklist'
    WHITELIST = 'whitelist'

    # testing
    TEST_INPUT_FILE_NAME = "test_configs"
    TEST_OUTPUT_FILE_NAME = "test_output"
    EXPECTED_TEST_OUTPUT_FILE_NAME = "expected_test_output"
    PROGRAM_INPUT_TO_RUN_TEST = ""
    FOLDER_USED_TO_TEST_PROGRAM = "folder_used_to_test_program"
    FOLDER_TO_SERIALIZE_DURING_TEST = "folder_to_be_serialized"

    @staticmethod
    def load_config(config_name_file: str) -> Dict[str, Any]:
        input_path = GlobalConfigs.generate_input_path(config_name_file)
        with open(input_path, 'r') as f:
            config = json.load(f)
        for list_type in [GlobalConfigs.BLACKLIST, GlobalConfigs.WHITELIST]:
            for key in config[list_type]:
                # Convert lists to sets for blacklist and whitelist
                config[list_type][key] = set(config[list_type][key])
        return config

    @staticmethod
    def generate_input_path(config_name: str) -> str:
        if GlobalConfigs.is_test_run(config_name):
            return GlobalConfigs.load_testing_config()
        # Use config file specified by user
        folder = GlobalConfigs.INPUT_FOLDER
        extension = ".json"
        return os.path.join(folder, config_name + extension)

    @staticmethod
    def generate_output_path(config_name: str) -> str:
        if GlobalConfigs.is_test_run(config_name):
            return GlobalConfigs.generate_path_to_test_output()
        folder = GlobalConfigs.OUTPUT_FOLDER
        extension = '.txt'
        return os.path.join(folder, config_name + extension)

    # TESTING
    @staticmethod
    def is_test_run(config_name: str) -> bool:
        return len(config_name) == 0

    @staticmethod
    def load_testing_config() -> str:
        # Load special config used for testing the program
        folder = GlobalConfigs.FOLDER_USED_TO_TEST_PROGRAM
        extension = '.json'
        file = GlobalConfigs.TEST_INPUT_FILE_NAME
        dir_containing_script = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(dir_containing_script, folder, file + extension)

    @staticmethod
    def generate_path_to_test_output() -> str:
        # Get special output path used when testing the program
        folder = GlobalConfigs.FOLDER_USED_TO_TEST_PROGRAM
        extension = '.txt'
        file = GlobalConfigs.TEST_OUTPUT_FILE_NAME
        dir_containing_script = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(dir_containing_script, folder, file + extension)

    @staticmethod
    def locate_testing_folder_to_serialize() -> str:
        # Get local path to the test folder (used when testing the program)
        test_folder = GlobalConfigs.FOLDER_USED_TO_TEST_PROGRAM
        folder_to_serialize = GlobalConfigs.FOLDER_TO_SERIALIZE_DURING_TEST
        dir_containing_script = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(dir_containing_script, test_folder, folder_to_serialize)

    @staticmethod
    def generate_path_to_expected_test_output() -> str:
        # Get path to expected output of a test run
        folder = GlobalConfigs.FOLDER_USED_TO_TEST_PROGRAM
        extension = '.txt'
        file = GlobalConfigs.EXPECTED_TEST_OUTPUT_FILE_NAME
        dir_containing_script = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(dir_containing_script, folder, file + extension)

    @staticmethod
    def verify_test_output() -> None:
        output_path = GlobalConfigs.generate_path_to_expected_test_output()
        with open(output_path, 'r') as f:
            output = f.read()

        expected_output_path = GlobalConfigs.generate_path_to_test_output()
        with open(expected_output_path, 'r') as f:
            expected_output = f.read()

        if output == expected_output:
            print("Test passed! Output is as expected...\n")
        else:
            print("Test failed! Output is not as expected.")
            print(f"Output length {len(output)} != expected output length {len(expected_output)}")
            print(f"Go to {GlobalConfigs.FOLDER_USED_TO_TEST_PROGRAM} and look at the outputs\n")
