import os
from folder_serializer import FolderSerializer, FolderSerializerTesting

#%%
if __name__ == "__main__":
    # Test run
    FolderSerializerTesting.main()

    # Actual Run
    config_name = "bulletin_board" # Input name of config file that should be loaded
    FolderSerializer.main(config_name)