import os
from folder_serializer import FolderSerializer

class Testing:
    # Folder paths for testing
    FOLDER_USED_TO_TEST_PROGRAM = "folder_used_to_test_program"
    FOLDER_TO_SERIALIZE_DURING_TEST = "folder_to_be_serialized"

    # Files used for testing
    TEST_INPUT_FILE = "test_configs.json"
    TEST_OUTPUT_FILE = "test_output.txt"
    EXPECTED_TEST_OUTPUT_FILE_NAME = "expected_test_output.txt"

    @staticmethod
    def main() -> None:
        config_path = Testing.load_testing_config()
        serializer = FolderSerializer.create_from_config(config_path)
        serializer.folder_to_serialize = Testing.testing_folder_to_serialize()
        serializer.serialize_folder()
        output = Testing.generate_path_to_test_output()
        serializer.write_output(output)
        Testing.verify_test_output()

    @staticmethod
    def load_testing_config() -> str:
        folder = Testing.FOLDER_USED_TO_TEST_PROGRAM
        file = Testing.TEST_INPUT_FILE
        local_path = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(local_path, folder, file)

    @staticmethod
    def generate_path_to_test_output() -> str:
        folder = Testing.FOLDER_USED_TO_TEST_PROGRAM
        file = Testing.TEST_OUTPUT_FILE
        local_path = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(local_path, folder, file)

    @staticmethod
    def testing_folder_to_serialize() -> str:
        test_folder = Testing.FOLDER_USED_TO_TEST_PROGRAM
        folder_to_serialize = Testing.FOLDER_TO_SERIALIZE_DURING_TEST
        local_path = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(local_path, test_folder, folder_to_serialize)

    @staticmethod
    def generate_path_to_expected_test_output() -> str:
        folder = Testing.FOLDER_USED_TO_TEST_PROGRAM
        file = Testing.EXPECTED_TEST_OUTPUT_FILE_NAME
        local_path = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(local_path, folder, file)

    @staticmethod
    def verify_test_output() -> None:
        output_path = Testing.generate_path_to_test_output()
        with open(output_path, 'r') as f:
            output = f.read()

        expected_output_path = Testing.generate_path_to_expected_test_output()
        with open(expected_output_path, 'r') as f:
            expected_output = f.read()

        if output == expected_output:
            print(f"Test passed! {Testing.TEST_OUTPUT_FILE} ({len(output)} characters) == {Testing.EXPECTED_TEST_OUTPUT_FILE_NAME} ({len(expected_output)} characters)...\n")
        else:
            print(f"Test failed! {Testing.TEST_OUTPUT_FILE} ({len(output)} characters) != {Testing.EXPECTED_TEST_OUTPUT_FILE_NAME} ({len(expected_output)} characters)")
            print(f"Investigate output at {output_path}")

if __name__ == "__main__":
    Testing.main()