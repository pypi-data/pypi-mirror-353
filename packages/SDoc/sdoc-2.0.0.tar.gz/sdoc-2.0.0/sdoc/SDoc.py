import configparser
import os
from typing import List

from sdoc import sdoc2
from sdoc.error import SDocError
from sdoc.format.Format import Format
from sdoc.helper.PathResolver import PathResolver
from sdoc.io.SDocIO import SDocIO
from sdoc.sdoc1.SDoc1Interpreter import SDoc1Interpreter
from sdoc.sdoc2.NodeStore import NodeStore
from sdoc.sdoc2.SDoc2Interpreter import SDoc2Interpreter


class SDoc:
    """
    The SDoc program.
    """

    # ------------------------------------------------------------------------------------------------------------------
    def __init__(self, io: SDocIO):
        """
        Object contructor.

        :param io: The IO object.
        """
        self._io: SDocIO = io
        """
        The IO object.
        """

        self._format: Format | None = None
        """
        The class for generation the document in the target format.
        """

        self._target_dir: str = '.'
        """
        The directory where the document in the target format must be created.
        """

        self._temp_dir: str = '.'
        """
        The directory where temporary files are stored.
        """

        self._config_path: str = ''
        """
        The path of the config file.
        """

        self._nodes_paths: List[str] = []
        """
        A list with path names from with node modules must be imported.
        """

        self._formatter_paths: List[str] = []
        """
        A list with path names from with node modules must be imported.
        """

        self._errors: int = 0
        """
        The total number of errors encountered at SDoc level 1 and level 2.
        """

    # ------------------------------------------------------------------------------------------------------------------
    @property
    def config_path(self) -> str:
        """
        Getter for config_path.
        """
        return self._config_path

    # ------------------------------------------------------------------------------------------------------------------
    @config_path.setter
    def config_path(self, config_path: str) -> None:
        """
        Setter for config_path.

        :param config_path: The path of the config file.
        """
        self._config_path = config_path

    # ------------------------------------------------------------------------------------------------------------------
    @property
    def target_dir(self) -> str:
        """
        Getter for target_dir.
        """
        return self.target_dir

    # ------------------------------------------------------------------------------------------------------------------
    @property
    def temp_dir(self) -> str:
        """
        Getter for temp_dir.
        """
        return self.temp_dir

    # ------------------------------------------------------------------------------------------------------------------
    def _config_create_formatter(self, config: configparser.ConfigParser) -> None:
        """
        Creates the formatter for generating the document in the target format.

        :param config: The config parser.
        """
        available_formats = ['html']

        # Read the target format of the document.
        target_format = config.get('sdoc', 'format', fallback=None)
        if target_format not in available_formats:
            raise SDocError(
                f"The format '{target_format}' is not available in SDoc. Set another in config file '{self._config_path}'")

        if not target_format:
            raise SDocError(f"Option 'format' in section 'sdoc' not set in config file '{self._config_path}'")

        # Read the class name for formatting the SDoc2 nodes into the target format.
        section = 'format_' + target_format
        class_name = config.get(section, 'class', fallback=None)
        if not class_name:
            raise SDocError(f"Option 'class' in section '{section}' not set in config file '{self._config_path}'")

        # Import the class.
        try:
            parts = class_name.split('.')
            module = ".".join(parts[:-1])
            __import__(module)
            m = __import__(module)
            for comp in parts[1:]:
                m = getattr(m, comp)
        except AttributeError:
            raise SDocError(
                f"There is no module named '{class_name}'! Set name correctly in config file '{self._config_path}'")

        # Create the formatter.
        self._format = m(self._io, target_format, config)

    # ------------------------------------------------------------------------------------------------------------------
    def _config_set_temp_dir(self, config: configparser.ConfigParser) -> None:
        """
        Reads the directory for storing temporary files.

        :param config: The config parser.
        """
        self._temp_dir = config.get('sdoc', 'temp_dir', fallback=self._temp_dir)

        if not self._temp_dir:
            raise SDocError("Option 'temp_dir' in section 'sdoc' not set correctly in config file '{0!s}'".
                            format(self._config_path))

        if not os.access(self._temp_dir, os.W_OK):
            raise SDocError(f"Directory '{self._temp_dir}' is not writable")

    # ------------------------------------------------------------------------------------------------------------------
    def _config_set_target_dir(self, config: configparser.ConfigParser) -> None:
        """
        Reads the directory where the document in the target format must be created.

        :param config: The config parser.
        """
        self._target_dir = config.get('sdoc', 'target_dir', fallback=self._target_dir)

        if not self._target_dir:
            raise SDocError(
                f"Option 'target_dir' in section 'sdoc' not set correctly in config file '{self._config_path}'")

        if not os.access(self._target_dir, os.W_OK):
            raise SDocError(f"Directory '{self._target_dir}' is not writable")

    # ------------------------------------------------------------------------------------------------------------------
    def _read_config_file(self) -> None:
        """
        Reads the configuration file.
        """
        config = configparser.ConfigParser()
        config.read(self._config_path)

        # Get the temp and target directory.
        self._config_set_temp_dir(config)
        self._config_set_target_dir(config)

        # Create the formatter for generating the document in the target format.
        self._config_create_formatter(config)

        self._formatter_paths.append(os.path.dirname(__file__) + '/sdoc2/formatter')
        self._nodes_paths.append(os.path.dirname(__file__) + '/sdoc2/node')

    # ------------------------------------------------------------------------------------------------------------------
    def _create_node_store(self) -> None:
        """
        Creates the node store (for storing nodes).
        """
        sdoc2.node_store = NodeStore(self._io)

    # ------------------------------------------------------------------------------------------------------------------
    @staticmethod
    def importing(path: str) -> None:
        """
        Imports modules from a specific path.

        :param path: The specific path.
        """
        modules = os.listdir(os.path.dirname(__file__) + path)

        path = path.replace('/', '.')

        for module in modules:
            if module != '__init__.py' and module[-3:] == '.py':
                __import__('sdoc' + path + module[:-3], locals(), globals())

    # ------------------------------------------------------------------------------------------------------------------
    def _import_nodes(self) -> None:
        """
        Imports nodes from a path which is declared below.
        """
        # @todo improve
        self.importing('/sdoc2/node/')

    # ------------------------------------------------------------------------------------------------------------------
    def _import_formatters(self) -> None:
        """
        Imports formatters from a path which is declared below.
        """
        # @todo improve
        self.importing('/sdoc2/formatter/html/')

    # ------------------------------------------------------------------------------------------------------------------
    def init(self) -> None:
        """
        Executes initiations required before running SDoc.
        """
        self._read_config_file()
        self._create_node_store()
        self._import_nodes()
        self._import_formatters()

    # ------------------------------------------------------------------------------------------------------------------
    def run_sdoc1(self, sdoc1_path: str, sdoc2_path: str, log_errors: bool = True) -> int:
        """
        Run the SDoc1 parser and returns the error count.

        :param sdoc1_path: The path of the SDoc1 document.
        :param sdoc2_path: The path where the SDoc2 document must be stored.
        :param log_errors: Whether the number of errors will be logged.
        """
        self._io.title('SDoc1')

        interpreter1 = SDoc1Interpreter(self._io)
        self._errors += interpreter1.process(sdoc1_path, sdoc2_path)

        if log_errors and self._errors:
            self._io.write_line('')
            self._io.title('Errors')
            self._io.write_error(f'There were {self._errors} errors in total.')

        return self._errors

    # ------------------------------------------------------------------------------------------------------------------
    def run_sdoc2(self, sdoc2_path: str, log_errors: bool = True) -> int:
        """
        Run the SDoc2 parser and returns the error count.

        :param sdoc2_path: The path of the SDoc2 document.
        :param log_errors: Whether the number of errors will be logged.
        """
        self._io.write_line('')
        self._io.title('SDoc2')

        interpreter2 = SDoc2Interpreter(self._io)
        self._errors += interpreter2.process(sdoc2_path)

        if log_errors and self._errors:
            self._io.write_line(" ")
            self._io.title('Errors')
            self._io.write_error(f'There were {self._errors} errors in total.')

        return self._errors

    # ------------------------------------------------------------------------------------------------------------------
    def run_format(self, log_errors: bool = True) -> int:
        """
        Generates the target document in the specific format and returns the error count.

        :param log_errors: Whether the number of errors will be logged.
        """
        self._io.write_line('')
        self._io.title('Format')

        self._errors += sdoc2.node_store.generate(self._format)

        if log_errors and self._errors:
            self._io.write_line(" ")
            self._io.title('Errors')
            self._io.write_error(f'There were {self._errors} errors in total.')

        return self._errors

    # ------------------------------------------------------------------------------------------------------------------
    def run_sdoc(self, main_filename: str, log_errors: bool = True) -> int:
        """
        Runs the SDoc1 and SDoc2 parser and returns the error count.

        :param main_filename: The path to the SDoc1 document.
        :param log_errors: Whether the number of errors will be logged.
        """
        self.init()

        PathResolver.set_home(main_filename)

        temp_filename = self._temp_dir + '/' + os.path.basename(main_filename) + '.sdoc2'
        self.run_sdoc1(main_filename, temp_filename, False)
        self.run_sdoc2(temp_filename, False)
        self.run_format(False)

        if log_errors and self._errors:
            self._io.write_line('')
            self._io.title('Errors')
            self._io.write_error(f'There were {self._errors} errors in total.')

        return self._errors

# ----------------------------------------------------------------------------------------------------------------------
