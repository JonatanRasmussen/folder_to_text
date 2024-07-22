import os
import json
from typing import Dict, Any

class Persistence:
    """ Hardcoded values for config structure and input/output folders """
    # folder paths
    INPUT_FOLDER = "program_inputs"
    OUTPUT_FOLDER = "program_outputs"

    # names used in config.json
    FOLDER_TO_SERIALIZE = 'folder_to_serialize'
    BLACKLIST = 'blacklist'
    WHITELIST = 'whitelist'
    CONFIG_EXTENSIONS = 'extensions'
    CONFIG_FILES = 'files'
    CONFIG_FOLDERS = 'folders'


#%%
if __name__ == "__main__":
    print("This is a config script meant to be imported. Don't try to run it!")