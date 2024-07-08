import os
import json
from typing import Dict, Any

class Persistence:
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

    @staticmethod
    def load_config(config_path: str) -> Dict[str, Any]:
        with open(config_path, 'r') as f:
            config = json.load(f)
        for list_type in [Persistence.BLACKLIST, Persistence.WHITELIST]:
            for key in config[list_type]:
                # Convert lists to sets for blacklist and whitelist
                config[list_type][key] = set(config[list_type][key])
        return config

    @staticmethod
    def generate_path_to_config(config_name: str) -> str:
        folder = Persistence.INPUT_FOLDER
        extension = ".json"
        return os.path.join(folder, config_name + extension)

    @staticmethod
    def generate_path_to_output(config_name: str) -> str:
        folder = Persistence.OUTPUT_FOLDER
        extension = '.txt'
        return os.path.join(folder, config_name + extension)

if __name__ == "__main__":
    print("This is a script for setting configurations. Don't try to run it!")