import os
from folder_serializer import FolderSerializer

if __name__ == "__main__":
    # Test run
    FolderSerializer.create_and_execute_test_run()

    # Actual Run
    config_name = "vuhdo" # Load your config file here
    FolderSerializer.create_and_execute_from_config(config_name)