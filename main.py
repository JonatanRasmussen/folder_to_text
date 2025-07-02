import os
from folder_serializer import FolderSerializer, FolderSerializerTesting

#%%
if __name__ == "__main__":
    # Test run
    FolderSerializerTesting.main_test()

    # Actual Run
    config_name = "self" # Input name of config file that should be loaded
    FolderSerializer.main(config_name)