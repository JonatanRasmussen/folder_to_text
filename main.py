import os
from folder_serializer import FolderSerializer
from testing import Testing


if __name__ == "__main__":
    # Test run
    Testing.main()

    # Actual Run
    config_name = "self" # Input name of config file that should be loaded
    FolderSerializer.main(config_name)