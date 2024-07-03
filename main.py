import os
from typing import Dict, Set
from folder_serializer import FolderSerializer

#%%
if __name__ == "__main__":

    my_blacklist: Dict[str, Set[str]] = {
        'extensions': {
            '.exe', '.dll', '.bin',  '.pyc', '.csproj', '.sln',
            '.jpg', '.png', '.svg', '.import', '.tscn', '.godot',
            '.gitignore', '.gitattributes', '.json',
        },
        'files': {
            'config.ini', 'secret.txt', 'devdiary.txt',
            '.gitignore', '.gitattributes',
        },
        'folders': {
            'temp', 'cache', '.git', '.vscode', '.godot',
        },
    }

    my_whitelist: Dict[str, Set[str]] = {
        'extensions': set(),
        'files': set(),
        'folders': set(),
    }

    processor = FolderSerializer(my_blacklist, my_whitelist)
    my_folder = "input_output"
    my_input_name = f"{my_folder}/input.txt"
    my_output_nane = f"{my_folder}/output.txt"
    processor.execute(my_input_name, my_output_nane)