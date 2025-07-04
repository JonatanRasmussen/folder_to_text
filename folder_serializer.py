import os
import json
from typing import Dict, Set, ClassVar, List
from dataclasses import dataclass

@dataclass
class FolderSerializer:
    """A class for serializing any folders content. Supports blacklist, whitelist and ordering."""
    folder_to_serialize: str

    # File extensions that are blacklisted by default
    BINARY_FILE_EXTENSIONS: ClassVar[Set[str]] = {
        # Images
        '.png', '.jpg', '.jpeg', '.gif', '.bmp', '.svg', '.ico', '.webp', '.tiff', '.tif',
        '.psd', '.ai', '.eps', '.raw', '.cr2', '.nef', '.dng', '.heic', '.heif', '.avif',

        # Executables and binaries
        '.exe', '.dll', '.bin', '.so', '.dylib', '.msi', '.deb', '.rpm', '.dmg', '.pkg',
        '.app', '.apk', '.ipa', '.com', '.bat', '.cmd', '.scr', '.sys', '.drv',

        # Documents
        '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx', '.odt', '.ods', '.odp',
        '.rtf', '.pages', '.numbers', '.key', '.pub', '.one', '.vsd', '.vsdx',

        # Archives
        '.zip', '.rar', '.7z', '.tar', '.gz', '.bz2', '.xz', '.lz', '.lzma', '.z',
        '.tgz', '.tbz2', '.txz', '.cab', '.iso', '.img', '.nrg', '.mdf',

        # Media
        '.mp3', '.mp4', '.avi', '.wav', '.ogg', '.mov', '.mkv', '.flv', '.wmv', '.m4v',
        '.m4a', '.aac', '.flac', '.wma', '.opus', '.webm', '.3gp', '.f4v', '.vob',
        '.ts', '.m2ts', '.mts', '.asf', '.rm', '.rmvb',

        # Compiled code
        '.pyc', '.pyo', '.class', '.o', '.obj', '.lib', '.a', '.jar', '.war', '.ear',
        '.beam', '.hi', '.cmi', '.cmo', '.cmx', '.rlib', '.pdb', '.ilk', '.exp',

        # Project files
        '.csproj', '.sln', '.vcxproj', '.vcproj', '.vbproj', '.fsproj', '.proj',
        '.xcodeproj', '.xcworkspace', '.pbxproj', '.sublime-project', '.sublime-workspace',

        # Game engine files
        '.import', '.tscn', '.godot', '.unity', '.unitypackage', '.asset', '.prefab',
        '.scene', '.mat', '.fbx', '.blend', '.mb', '.ma', '.max', '.3ds',

        # Database files
        '.db', '.sqlite', '.sqlite3', '.mdb', '.accdb', '.dbf', '.bak', '.ldf',

        # Font files
        '.ttf', '.otf', '.woff', '.woff2', '.eot', '.pfb', '.pfm', '.afm',

        # Certificate/Key files
        '.p12', '.pfx', '.cer', '.crt', '.der', '.pem', '.csr', '.jks',

        # Other binary/data files
        '.cache', '.tmp', '.log', '.dmp', '.core', '.swap', '.lock', '.pid',
        '.dat', '.data', '.idx', '.pack', '.sample'
    }

    # Folders that are blacklisted by default
    GLOBAL_BLACKLISTED_FOLDERS: ClassVar[Set[str]] = {
        # Version control
        '.git', '.svn', '.hg', '.bzr', '.cvs', '.fossil', '.darcs',

        # IDE/Editor folders
        '.vscode', '.idea', '.vs', '.vscode-server', '.atom', '.sublime',
        '.brackets', '.eclipse', '.netbeans', '.komodo', '.vim', '.emacs.d',

        # Python
        '__pycache__', '.pytest_cache', '.mypy_cache', '.coverage', '.tox',
        'venv', 'env', '.env', '.venv', 'virtualenv', 'site-packages',
        '.python-version', 'pip-wheel-metadata', '.hypothesis',

        # Node.js/JavaScript
        'node_modules', '.npm', '.yarn', '.pnp', '.next', '.nuxt',
        'bower_components', 'jspm_packages', '.nyc_output', 'coverage',

        # Java/JVM
        'target', 'build', '.gradle', '.m2', '.ivy2', '.sbt', 'classes',
        'out', 'lib', 'libs', 'dependencies',

        # .NET/C#
        'bin', 'obj', 'packages', '.nuget', 'TestResults',
        'BenchmarkDotNet.Artifacts', 'StyleCopReport.xml',

        # Ruby
        '.bundle', 'vendor', '.rbenv', '.rvm', '.yardoc',

        # Go
        '.godeps', '_vendor', 'pkg', '.go-version',

        # Rust
        '.cargo',

        # PHP
        '.composer', '.phpunit.result.cache',

        # Build/Cache folders
        'dist', 'output', 'temp', 'cache', '.cache', 'tmp', '.tmp', '.temp',
        'artifacts', 'generated', 'release', 'debug',

        # Testing
        'test-results', 'test-reports', 'htmlcov', 'lcov-report',

        # Documentation builds
        '_build', '_site', '.jekyll-cache', '.sass-cache', 'gh-pages',
        'docs/_build', 'site', 'public', '_public',

        # Game engines
        '.godot', '.import', 'Library', 'Temp', 'Build', 'Logs',
        'UserSettings', 'Builds', 'AssetStoreTools',

        # Web frameworks/tools
        '.svelte-kit', '.astro', '.vuepress', '.docusaurus', 'storybook-static', '.storybook',

        # Mobile development
        'DerivedData', '.expo', '.flutter-plugins', '.flutter-plugins-dependencies',
        'ios/Pods', 'android/.gradle', 'android/app/build',

        # Web cache/data
        'webcache', 'wowhead_cache', 'cached_wowhead_html', 'scraped_data',
        'downloads', 'uploads', 'assets/cache', 'storage/cache',

        # Static assets (often large/not code)
        'Images', 'images', 'Fonts', 'fonts', 'Libs', 'assets/images',
        'static/images', 'public/images', 'resources/images', 'media',

        # OS folders
        '.DS_Store', 'Thumbs.db', 'Desktop.ini', '.Spotlight-V100',
        '.Trashes', '.fseventsd', '.TemporaryItems', '.AppleDouble',

        # Package managers
        '.maven', '.pip', '.gem', '.stack', '.cabal', '.opam', '.esy',

        # Deployment/Infrastructure
        'terraform', '.terraform', '.terragrunt-cache', '.serverless',
        'helm', '.kube', '.minikube', 'docker-data', '.docker',

        # Logs
        'logs', 'log', 'Log', '.logs', 'syslog', 'access.log',
        'error.log', 'debug.log', 'application.log'
    }

    @staticmethod
    def main(config_name: str) -> None:
        """Serialize folder in 'config_name'.json and write output to 'config_name'.txt"""
        FALLBACK_FOLDER = FolderSerializer._FALLBACK_FOLDER
        INPUT_FOLDER = FolderSerializer._INPUT_FOLDER
        OUTPUT_FOLDER = FolderSerializer._OUTPUT_FOLDER

        # Try to create serializer from config, with fallback to folder_to_text subdirectory
        config_path = os.path.join(INPUT_FOLDER, f"{config_name}.json")
        try:
            serializer = FolderSerializer.create_from_config(config_path)
            output_path = os.path.join(OUTPUT_FOLDER, f"{config_name}.txt")
        except FileNotFoundError:
            fallback_config_path = os.path.join(FALLBACK_FOLDER, INPUT_FOLDER, f"{config_name}.json")
            serializer = FolderSerializer.create_from_config(fallback_config_path)
            output_path = os.path.join(FALLBACK_FOLDER, OUTPUT_FOLDER, f"{config_name}.txt")

        serializer.serialize_folder()
        serializer.print_summary()
        serializer.write_output(output_path)

    ###########################
    ### PRIVATE CLASS STUFF ###
    ###########################

    # Hardcoded values for input/output folders
    _INPUT_FOLDER = "program_inputs"
    _OUTPUT_FOLDER = "program_outputs"
    _FALLBACK_FOLDER = "folder_to_text"

    # Keys used in config.json
    _FOLDER_TO_SERIALIZE = 'folder_to_serialize'
    _BLACKLIST = 'blacklist'
    _WHITELIST = 'whitelist'
    _CONFIG_EXTENSIONS = 'extensions'
    _CONFIG_FILES = 'files'
    _CONFIG_FOLDERS = 'folders'
    _SHOW_FIRST = 'show_first'
    _SHOW_LAST = 'show_last'
    _LLM_SEPARATOR = 'llm_separator'

    # Class fields
    _blacklist: Dict[str, Set[str]]
    _whitelist: Dict[str, Set[str]]
    _show_first: Dict[str, List[str]]
    _show_last: Dict[str, List[str]]
    _llm_separator: Dict[str, str]
    _output_path: str = ""
    _folder_content_as_str: str = ""
    _traversed_files: int = 0
    _skipped_files: int = 0
    _binary_files: int = 0
    _read_errors: int = 0
    _hierarchy: str = ""

    @classmethod
    def create_from_config(cls, config_path: str) -> 'FolderSerializer':
        # Load config json
        with open(config_path, 'r') as f:
            config = json.load(f)

        # Convert blacklist / whitelist from list to set
        for list_type in [cls._BLACKLIST, cls._WHITELIST]:
            for key in config[list_type]:
                config[list_type][key] = set(config[list_type][key])

        # Set defaults for new optional configs
        show_first = config.get(cls._SHOW_FIRST, {cls._CONFIG_FILES: [], cls._CONFIG_FOLDERS: []})
        show_last = config.get(cls._SHOW_LAST, {cls._CONFIG_FILES: [], cls._CONFIG_FOLDERS: []})
        llm_separator = config.get(cls._LLM_SEPARATOR, {"enabled": False, "text": "--- End of Code / Start of Instructions ---"})

        # Create class instance from config
        return cls(
            folder_to_serialize=config[cls._FOLDER_TO_SERIALIZE],
            _blacklist=config[cls._BLACKLIST],
            _whitelist=config[cls._WHITELIST],
            _show_first=show_first,
            _show_last=show_last,
            _llm_separator=llm_separator,
        )

    def print_summary(self) -> None:
        print(self._hierarchy)
        print(f"Errors: {self._read_errors}")
        print(f"Binaries: {self._binary_files}")
        print(f"Files Read: {self._traversed_files}")
        print(f"Skipped: {self._skipped_files}")

    def write_output(self, output_path: str) -> None:
        try:
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(self._folder_content_as_str)
            print(f"Output successfully written to {output_path}")
            print(f"Length of output: {len(self._folder_content_as_str)} characters (~{int(len(self._folder_content_as_str) / 3.5)} tokens)\n")
        except Exception as e:
            print(f"Error writing to {output_path} {str(e)}\n")

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
            # Filter and sort folders
            filtered_dirs = [d for d in dirs if self._should_process_folder(d)]
            dirs[:] = self._sort_items(filtered_dirs, self._CONFIG_FOLDERS)

            # Sort files according to show_first/show_last rules
            sorted_files = self._sort_items(files, self._CONFIG_FILES)

            for file in sorted_files:
                file_path = os.path.join(root, file)
                relative_path = os.path.relpath(file_path, self.folder_to_serialize)

                if not self._should_process_file(file):
                    self._skipped_files += 1
                    continue

                file_extension = os.path.splitext(file)[-1].lower()
                if file_extension in self.BINARY_FILE_EXTENSIONS:
                    self._folder_content_as_str += f"\n\n--- Start of File: {relative_path} ---\n\n"
                    self._folder_content_as_str += "[Binary file - NOT DISPLAYED]"
                    self._folder_content_as_str += f"\n\n--- End of File: {relative_path} ---\n\n"
                    self._binary_files += 1
                else:
                    try:
                        with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                            self._folder_content_as_str += f"\n\n--- Start of File: {relative_path} ---\n\n"
                            file_content = f.read()
                            if len(file_content) == 0:
                                self._folder_content_as_str += "[Empty file - NOTHING TO DISPLAY]"
                            else:
                                self._folder_content_as_str += file_content
                            self._folder_content_as_str += f"\n\n--- End of File: {relative_path} ---\n\n"
                            self._traversed_files += 1
                    except Exception as e:
                        self._read_errors += 1
                        print(f"Error reading file {file_path}: {str(e)}")

        # Add LLM separator if enabled
        if self._llm_separator.get("enabled", False):
            separator_text = self._llm_separator.get("text", "--- End of Code / Start of Instructions ---")
            self._folder_content_as_str += f"\n\n{separator_text}\n\n"

    def _sort_items(self, items: List[str], item_type: str) -> List[str]:
        """Sort items according to show_first and show_last rules"""
        show_first = self._show_first.get(item_type, [])
        show_last = self._show_last.get(item_type, [])

        first_items = []
        last_items = []
        regular_items = []

        for item in items:
            # For files, check both full name and name without extension
            # For folders, only check the folder name
            matches_first = False
            matches_last = False

            if item_type == self._CONFIG_FILES:
                item_name_no_ext = os.path.splitext(item)[0]
                # Check if the item exactly matches or if the name without extension exactly matches
                matches_first = item in show_first or item_name_no_ext in show_first
                matches_last = item in show_last or item_name_no_ext in show_last
            else:
                matches_first = item in show_first
                matches_last = item in show_last

            if matches_first:
                first_items.append(item)
            elif matches_last:
                last_items.append(item)
            else:
                regular_items.append(item)

        # Sort each group to maintain consistent ordering within groups
        # but preserve the order specified in show_first/show_last lists
        def get_priority_index(item_list, target_item):
            if target_item in item_list:
                return item_list.index(target_item)
            if item_type == self._CONFIG_FILES:
                name_no_ext = os.path.splitext(target_item)[0]
                if name_no_ext in item_list:
                    return item_list.index(name_no_ext)
            return len(item_list)

        first_items.sort(key=lambda x: get_priority_index(show_first, x))
        last_items.sort(key=lambda x: get_priority_index(show_last, x))
        regular_items.sort()

        return first_items + regular_items + last_items

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

            # Get all items and sort them
            all_items = sorted(os.listdir(current_path))
            dirs = [item for item in all_items if os.path.isdir(os.path.join(current_path, item))]
            files = [item for item in all_items if os.path.isfile(os.path.join(current_path, item))]

            # Sort directories and files according to show_first/show_last rules
            sorted_dirs = self._sort_items(dirs, self._CONFIG_FOLDERS)
            sorted_files = self._sort_items(files, self._CONFIG_FILES)

            # Add directories first
            for item in sorted_dirs:
                item_path = os.path.join(current_path, item)
                hierarchy += self._get_hierarchy(item_path, prefix)

            # Then add files
            for item in sorted_files:
                file_extension = os.path.splitext(item)[-1].lower()
                if not self._should_process_file(item):
                    hierarchy += f"{prefix}{item} {file_skipped}\n"
                elif file_extension in self.BINARY_FILE_EXTENSIONS:
                    hierarchy += f"{prefix}{item} {file_binary}\n"
                else:
                    hierarchy += f"{prefix}{item}\n"

        return hierarchy

    def _should_process_folder(self, folder_name: str) -> bool:
        # Check global blacklist first
        if folder_name in self.GLOBAL_BLACKLISTED_FOLDERS:
            return False

        # Then check user-defined whitelist/blacklist
        if self._whitelist[self._CONFIG_FOLDERS] and folder_name not in self._whitelist[self._CONFIG_FOLDERS]:
            return False
        return folder_name not in self._blacklist[self._CONFIG_FOLDERS]

    def _should_process_file(self, file_name: str) -> bool:
        # Check file extension against global binary blacklist first
        file_extension = os.path.splitext(file_name)[-1].lower()
        if file_extension in self.BINARY_FILE_EXTENSIONS:
            return False

        # Then check user-defined extension rules
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
        if file_name in self._blacklist[self._CONFIG_FILES] or file_name_without_extension in self._blacklist[self._CONFIG_FILES]:
            return False
        return True


#######################
### TESTING SECTION ###
#######################

class FolderSerializerTesting:
    """This class is used ONLY for testing of FolderSerializer"""

    @staticmethod
    def main_test() -> None:
        """Test FolderSerializer with dummy data"""
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
        try:
            with open(output_path, 'r', encoding='utf-8') as f:  # Added encoding for consistency
                output = f.read()
        except FileNotFoundError:
            print(f"Test failed! Output file {output_path} was not created.")
            return
        except Exception as e:
            print(f"Test failed! Error reading output file: {str(e)}")
            return

        expected_output_path = FolderSerializerTesting._generate_path_to_expected_test_output()
        try:
            with open(expected_output_path, 'r', encoding='utf-8') as f:  # Added encoding for consistency
                expected_output = f.read()
        except FileNotFoundError:
            print(f"Test failed! Expected output file {expected_output_path} not found.")
            return
        except Exception as e:
            print(f"Test failed! Error reading expected output file: {str(e)}")
            return

        msg_output = f"{FolderSerializerTesting._TEST_OUTPUT_FILE} ({len(output)} characters)"
        msg_expected = f"{FolderSerializerTesting._EXPECTED_TEST_OUTPUT_FILE} ({len(expected_output)} characters)"

        if output == expected_output:
            print(f"Test passed! {msg_output} == {msg_expected}...\n")
        else:
            print(f"Test failed! {msg_output} != {msg_expected}")
            print(f"Investigate output at {output_path}\n")

            # Additional debugging information
            lines_output = output.split('\n')
            lines_expected = expected_output.split('\n')

            if len(lines_output) != len(lines_expected):
                print(f"Line count differs: got {len(lines_output)}, expected {len(lines_expected)}")

            # Show first difference
            for i, (line_out, line_exp) in enumerate(zip(lines_output, lines_expected)):
                if line_out != line_exp:
                    print(f"First difference at line {i+1}:")
                    print(f"  Got:      '{line_out}'")
                    print(f"  Expected: '{line_exp}'")
                    break