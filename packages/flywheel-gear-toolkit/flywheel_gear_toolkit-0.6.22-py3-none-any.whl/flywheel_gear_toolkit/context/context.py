"""Hosts the GearToolkitContext class. Provides gear helper functions."""

import functools
import json
import logging
import os
import pathlib
import tempfile
import typing as t
import warnings
from pprint import pformat
from shutil import rmtree

try:
    import flywheel

    HAVE_FLYWHEEL = True
except (ModuleNotFoundError, ImportError):
    HAVE_FLYWHEEL = False


from ..logging import _recursive_update, configure_logging
from ..utils.metadata import Metadata
from .constants import BOTTOM_UP_PARENT_HIERARCHY

log = logging.getLogger(__name__)


def convert_config_type(input_str):
    """Converts strings in the format ``<value>:<type>`` (i.e. '4:integer') to a type
    consistent with the strin   g preceded by the last `:`.

    Args:
        input_str (str): A string in ``<value>:<type>`` format.

    Raises:
        ValueError: If input_str is not a string or the type is not recognized.

    Returns:
        object: A value consistent with the type specified.
    """
    if not isinstance(input_str, str):
        raise ValueError(f"input_str {input_str} is not str")

    if ":" not in input_str:
        input_str = input_str + ":"

    input_str, type_str = input_str.rsplit(":", maxsplit=1)

    type_str = type_str.lower()

    if type_str in ["boolean", "bool"] and input_str.lower() == "true":
        output = True

    elif type_str in ["boolean", "bool"] and input_str.lower() == "false":
        output = False

    elif type_str in ["boolean", "bool"] and input_str.lower() not in [
        "false",
        "true",
    ]:
        raise ValueError(f"Cannot convert {input_str} to a boolean")

    elif type_str in ["str", "", "string"]:
        output = input_str

    elif type_str == "number":
        if "." in input_str:
            output = float(input_str)
        else:
            output = int(input_str)

    elif type_str == "float":
        output = float(input_str)

    elif type_str in ["integer", "int"]:
        output = int(input_str)

    else:
        raise ValueError(f"Unrecognized type_str: {type_str}")

    return output


def deprecated(reason, version):
    """Decorator to mark a function as deprecated."""

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            warnings.warn(
                f"{func.__name__} is deprecated since version {version}. Reason: {reason}",
                category=DeprecationWarning,
                stacklevel=2,
            )
            return func(*args, **kwargs)

        return wrapper

    return decorator


class GearToolkitContext:
    """Provides helper functions for gear development, namely for accessing the gear's
    `config.json` and `manifest.json`.

    Args:
        gear_path (str, optional): A path to use, default behavior will use the current
            working directory (``os.getcwd()``).
        manifest_path (str, optional): A path to the gear's manifest.json file,
            defaults to ``self.path/'manifest.json'``.
        config_path (str, optional): A path to the gear's config.json file, defaults to
            ``self._path/'config.json'``.
        input_args (list, optional): List of arguments to parse to generate a
            ``config.json`` file. If not provided, ``sys.argv`` will be parsed instead.
        tempdir (bool, optional): whether to use ``tempfile.TemporaryDirectory()`` for
            ``_path``, defaults to False. Useful for testing.
        log_metadata (bool, optional): whether to log .metadata.json to log upon write,
            defaults to True.
        clean_on_error (bool, optional): whether to clean output directory upon exit
            with error, defaults to False.

    Attributes:
        _path (pathlib.Path): The result of ``pathlib.Path(gear_path or
            os.getcwd()).resolve()``.
        _client (flywheel.Client): An instance of the Flywheel client if a valid API
            key was provided or a user is currently logged into the Flywheel CLI.
        metadata (dict): Dictionary that stores updates to be dumped to
            `.metadata.json`.
        _temp_dir (tempfile.TemporaryDirectory): None unless initialized with
            `tempdir=True`.
        manifest (dict): Dictionary representation of `manifest.json`.
        config_json (dict): Dictionary representation of `config.json`.
    """

    def __init__(
        self,
        gear_path=None,
        manifest_path=None,
        config_path=None,
        input_args=None,
        tempdir=False,
        log_metadata=True,
        fail_on_validation=True,
        clean_on_error=False,
    ):
        warnings.warn(
            "The flywheel-gear-toolkit will be deprecated in an upcoming release as we are transitioning to the fw-gear package, currently in beta."
            "Please refer to https://flywheel-io.gitlab.io/public/gear-toolkit/index.html for additional information on the deprecation status.",
            DeprecationWarning,
        )

        self._temp_dir = None
        if tempdir:
            self._temp_dir = tempfile.TemporaryDirectory()
            gear_path = self._temp_dir.name

        self._path = pathlib.Path(gear_path or os.getcwd()).resolve()
        self._client = None
        self._out_dir = None
        self._work_dir = None
        self._log_metadata = log_metadata
        self.fail_on_validation = fail_on_validation
        self._clean_on_error = clean_on_error
        self.manifest = self._load_json(manifest_path or self._path / "manifest.json")
        if config_path or (self._path / "config.json").exists():
            self.config_json = self._load_json(config_path or self._path / "config.json")
        else:
            self.config_json = {
                "config": {},
                "inputs": {},
                "destination": {"id": "aex", "type": "acquisition"},
            }
        # Needs to be last
        self.metadata = Metadata(self)

    def init_logging(self, default_config_name=None, update_config=None):
        """Configures logging via `gear_toolkit.logging.templated.configure_logging`.

        If no ``default_config_name`` is provided, will get `debug` from the
        configuration options. If `debug` is False or not defined in the gear
        configuration options, ``default_config_name`` will be set to info.

        If `update_config` is not provided, manifest['custom']['log_config'] will be
        used (if defined in the manifest).

        Args:
            default_config_name (str, optional): A string, 'info' or 'debug', indicating
                the default template to use. (Defaults to 'info').
            update_config (dict, optional): A dictionary containing the keys, subkeys,
                and values of the templates to update. (Defaults to None).
        """
        if not default_config_name:
            if self.config.get("debug"):
                default_config_name = "debug"
            else:
                default_config_name = "info"
        if not update_config:
            if self.manifest:
                if isinstance(self.manifest.get("custom"), dict):
                    update_config = self.manifest["custom"].get("log_config", None)

        if default_config_name == "debug":
            """
            NOTE: The "filename" key defaults to "job.log" in the default config. This enables tests to run without having to specify or create a `/flywheel/v0/output` directory.
            """
            if job_id := self.config_json.get("job", {}).get("id", {}):
                log_file_name = f"job-{job_id}.log"
            else:
                log_file_name = "job.log"

            config_to_update = {
                "handlers": {
                    "file_handler": {
                        "filename": str(self.output_dir / log_file_name),
                    }
                }
            }
            update_config = {} if update_config is None else update_config
            update_config = _recursive_update(update_config, config_to_update)

        configure_logging(
            default_config_name=default_config_name,
            update_config=update_config,
        )
        return default_config_name, update_config

    @property
    def config(self):
        """Get the config dictionary from config.json.

        Returns:
            dict: The configuration dictionary.
        """
        return self.config_json["config"]

    @property
    def destination(self):
        """Get the destination reference.

        Returns:
            dict: The destination dictionary.
        """
        return self.config_json["destination"]

    @property
    def work_dir(self):
        """Get the absolute path to a work directory.

        Returns:
            pathlib.Path: The absolute path to work.
        """
        if self._work_dir is None:
            self._work_dir = self._path / "work"
            if not self._work_dir.exists():
                self._work_dir.mkdir(parents=True)
        return self._work_dir

    @property
    def output_dir(self):
        """Get the absolute path to the output directory.

        Returns:
            pathlib.Path: The absolute path to outputs.
        """
        if self._out_dir is None:
            self._out_dir = self._path / "output"
            if not self._out_dir.exists():
                self._out_dir.mkdir(parents=True)
        return self._out_dir

    @property
    def client(self):
        """Wrapper around self.get_client()."""
        if not self._client:
            self._client = self.get_client()
        return self._client

    def get_client(self):
        """Get the SDK client, if an api key input exists or CLI client exists.

        Returns:
          flywheel.Client: The Flywheel SDK client.
        """
        if not HAVE_FLYWHEEL:
            warnings.warn(
                "Please install the `sdk` extra or install `flywheel-sdk` within"
                " your gear in order to use the SDK client."
            )
            return None
        api_key = None
        client = None
        for inp in self.config_json["inputs"].values():
            if inp["base"] == "api-key" and inp["key"]:
                api_key = inp["key"]
                try:
                    client = flywheel.Client(api_key)
                except Exception as exc:  # pylint: disable=broad-except
                    log.error(
                        "An exception was raised when initializing client: %s",
                        exc,
                        exc_info=True,
                    )
        if api_key is None:
            try:
                client = flywheel.Client()
            except Exception as exc:  # pylint: disable=broad-except
                log.error(
                    "No api_key was provided and exception was raised when "
                    "attempting to log in via CLI %s",
                    exc,
                    exc_info=True,
                )
        return client

    def log_config(self):
        """Print the configuration and input files to the logger."""
        # Log destination
        log.info(
            "Destination is %s=%s",
            self.destination.get("type"),
            self.destination.get("id"),
        )

        # Log file inputs
        for inp_name, inp in self.config_json["inputs"].items():
            if inp["base"] != "file":
                continue

            container_type = inp.get("hierarchy", {}).get("type")
            container_id = inp.get("hierarchy", {}).get("id")
            file_name = inp.get("location", {}).get("name")

            log.info(
                'Input file "%s" is %s from %s=%s',
                inp_name,
                file_name,
                container_type,
                container_id,
            )

        # Log configuration values
        for key, value in self.config.items():
            log.info('Config "%s=%s"', key, value)

    def get_input(self, name):
        """The manifest.json has a field for 'inputs'. These are often the files to be analyzed
        or that aid in analyis (e.g., masks). This method gets the file named as the input ("name").

        Args:
            name (str): The name of the input.

        Returns:
            dict: The input dictionary, or None if not found.

        Example:
            gtk_context = GearTookitContext()
            gtk_context.get_input('input_image')
        """
        return self.config_json["inputs"].get(name)

    def get_input_file_object(self, name):
        """Get the specified input file object from config.json
        Args:
            name (str): The name of the input.

        Returns:
            dict: The input dictionary, or None if not found.
        """
        inp = self.get_input(name)
        if inp is None:
            return None
        if inp["base"] != "file":
            raise ValueError(f"The specified input {name} is not a file")
        return inp["object"]

    def get_input_file_object_value(self, name, key):
        """Get the value of the input file metadata from config.json.

        Args:
            name (str): The name of the input.
            key (str): The name of the file container metadata

        Raises:
            ValueError: if the input exists, but is not a file.

        Returns:
            Union[str, list, dict]: The value of the specified file metadata, or None if not found.
        """
        inp_obj = self.get_input_file_object(name)

        return inp_obj.get(key, None) if key in inp_obj.keys() else None

    def get_input_path(self, name):
        """Get the full path to the given input file.
        Sourced from the 'inputs' field in the manifest.json.

        Args:
            name (str): The name of the input.

        Raises:
            ValueError: if the input exists, but is not a file.

        Returns:
            str: The path to the input file if it exists, otherwise None.
        """
        inp = self.get_input(name)
        if inp is None:
            return None
        if inp["base"] != "file":
            raise ValueError(f"The specified input {name} is not a file")
        return inp["location"]["path"]

    def get_input_filename(self, name):
        """Get the the filename of given input file.
        Sourced from the 'inputs' field in the manifest.json.

        Args:
            name (str): The name of the input.

        Raises:
            ValueError: if the input exists, but is not a file.

        Returns:
            str: The filename to the input file if it exists, otherwise None.
        """
        inp = self.get_input(name)
        if inp is None:
            return None
        if inp["base"] != "file":
            raise ValueError(f"The specified input {name} is not a file")
        return inp["location"]["name"]

    def get_container_from_ref(self, ref):
        """Returns the container from its reference.

        Args:
            ref (dict): A dictionary with type and id keys defined.

        Returns:
            Container: A flywheel container.
        """
        container_type = ref.get("type")
        getter = getattr(self.client, f"get_{container_type}")
        return getter(ref.get("id"))

    def get_destination_container(self):
        """Returns the destination container."""
        return self.get_container_from_ref(self.destination)

    def get_parent(self, container):
        """Returns parent container of container input."""
        if container.container_type == "analysis":
            return self.get_container_from_ref(container.parent)
        elif container.container_type == "file":
            return container.parent
        elif container.container_type == "group":
            raise TypeError("Group container does not have a parent.")
        else:
            for cont_type in BOTTOM_UP_PARENT_HIERARCHY:
                if not container.parents.get(cont_type):
                    # not defined, parent must be up the hierarchy
                    continue
                return self.get_container_from_ref(
                    {"type": cont_type, "id": container.parents.get(cont_type)}
                )

    def get_destination_parent(self):
        """Returns the parent container of the destination container."""
        dest = self.get_destination_container()
        return self.get_parent(dest)

    def open_input(self, name, mode="r", **kwargs):
        """Open the named input file, derived from the 'inputs' field in the manifest.

        Args:
            name (str): The name of the input.
            mode (str): The open mode (Default value = 'r').
            **kwargs (dict): Keyword arguments for `open`.

        Raises:
            ValueError: If input ``name`` is not defined in config_json.
            FileNotFoundError: If the path in the config_json for input ``name`` is
                not a file/

        Returns:
            File: The file object.
        """
        path = self.get_input_path(name)
        if path is None:
            raise ValueError(f"Input {name} is not defined in the config.json")
        if not os.path.isfile(path):
            raise FileNotFoundError(f"Input {name} does not exist at {path}")
        return open(path, mode, **kwargs)

    def open_output(self, name, mode="w", **kwargs):
        """Open the named output file.

        Args:
            name (str): The name of the output.
            mode (str): The open mode (Default value = 'w').
            **kwargs (dict): Keyword arguments for `open`.

        Returns:
            File: The file object.
        """
        path = self.output_dir / name
        return path.open(mode, **kwargs)

    def update_container_metadata(
        self, container_type, deep: bool = True, **kwargs
    ) -> None:  # pragma: no cover
        """Wrapper around Metadata().update_container()."""
        warnings.warn(
            (
                "GearTookitContext.update_container_metadata() is deprecated. "
                "Please use GearTookitContext.metadata.update_container()."
            ),
            DeprecationWarning,
        )
        self.metadata.update_container(container_type, deep, **kwargs)

    def update_file_metadata(
        self, file_: t.Any, deep: bool = True, **kwargs
    ) -> None:  # pragma: no cover
        """Wrapper around Metadata().update_file()."""
        warnings.warn(
            (
                "GearTookitContext.update_file_metadata() is deprecated. "
                "Please use GearTookitContext.metadata.update_file()."
            ),
            DeprecationWarning,
        )
        self.metadata.update_file_metadata(
            file_, deep, container_type=self.destination["type"], **kwargs
        )

    def update_destination_metadata(self, deep: bool = True, **kwargs) -> None:  # pragma: no cover
        """Wrapper around Metadata().update_container()."""
        warnings.warn(
            (
                "GearTookitContext.update_destination_metadata() is deprecated. "
                "Please use GearTookitContext.metadata.update_container()."
            ),
            DeprecationWarning,
        )
        self.metadata.update_container(self.destination["type"], deep, **kwargs)

    def get_context_value(self, name):
        """Get the context input for name.
        (Checks the type of input selected. i.e., files are not context input) # not sure on this interpretation.

        Args:
            name (str): The name of the input.

        Returns:
            dict: The input context value, or None if not found.
        """
        inp = self.get_input(name)
        if not inp:
            return None
        if inp["base"] != "context":
            raise ValueError(f"The specified input {name} is not a context input")
        return inp.get("value")

    @deprecated(
        "download_session_bids is deprecated as it will not download necessary project-level files.",
        "0.6.19",
    )
    def download_session_bids(self, target_dir=None, **kwargs):
        """DEPRECATED: Download the session in bids format to target_dir.

        Args:
            target_dir (str): The destination directory (otherwise work/bids will be
                used) (Default value: 'work/bids').
            kwargs (dict): kwargs for `flywheel_bids.export_bids.download_bids_dir`.

        Returns:
            pathlib.Path: The absolute path to the downloaded bids directory.
        """
        warnings.warn(
            "download_session_bids is deprecated as it will not download necessary project-level files.\nPlease use `download_project_bids` instead.",
            DeprecationWarning,
        )

        # (
        #     parent_id,
        #     target_dir,
        #     download_bids_dir,
        #     kwargs,
        # ) = self._validate_bids_download(
        #     container_type="session", target_dir=target_dir, **kwargs
        # )
        # download_bids_dir(self.client, parent_id, "session", target_dir, **kwargs)
        # return target_dir

    def download_project_bids(self, target_dir=None, **kwargs):
        """Download the project in bids format to target_dir.

        Args:
            target_dir (str): The destination directory (otherwise work/bids will be
                used) (Default value = 'work/bids').
            src_data (bool): Whether or not to include src data (e.g. dicoms)
            (Default value = False).
            **kwargs: kwargs for ``flywheel_bids.export_bids.download_bids_dir``.

        Keyword Args:
            subjects (list): The list of subjects to include (via subject code)
                otherwise all subjects.
            sessions (list): The list of sessions to include (via session label)
                otherwise all sessions.
            folders (list): The list of folders to include (otherwise all folders) e.g.
                ['anat', 'func'].
            All the other kwargs for ``flywheel_bids.export_bids.download_bids_dir``.

        Returns:
            pathlib.Path: The absolute path to the downloaded bids directory.
        """
        (
            parent_id,
            target_dir,
            download_bids_dir,
            kwargs,
        ) = self._validate_bids_download(container_type="project", target_dir=target_dir, **kwargs)
        download_bids_dir(self.client, parent_id, "project", target_dir, **kwargs)
        return target_dir

    def __enter__(self):
        #        if self.report_usage_statistics:
        #            import multiprocessing
        #
        #            self.queue = multiprocessing.Manager().Queue()
        #            self.process = multiprocessing.Process(
        #                target=worker, args=(queue, interval), kwargs={"disk_usage": disk_usage}
        #            )
        #            process.start()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        #        if self.report_usage_statistics:
        #            self.process.terminate()
        #            # finish subprocess and report on usage.
        #            msg = f"Function {func.__name__} used: \n"
        #            while not self.queue.empty():
        #                time, usage = queue.get()
        #                msg += f"time: {time}, usage: {usage}\n"
        #            log.info(msg)

        if exc_type is None or (issubclass(exc_type, SystemExit) and exc_value.code == 0):
            self.metadata.update_zip_member_count(
                self.output_dir, container_type=self.destination["type"]
            )
            self.metadata.write(self.output_dir, self.fail_on_validation, self._log_metadata)
        elif self._clean_on_error:
            log.info("Cleaning output folder.")
            self._clean_output()
        else:
            log.debug(f"Skipping cleanup of {self.output_dir}")

        if self._temp_dir:
            self._temp_dir.cleanup()
        if self._client:
            sdk_usage = getattr(self._client.api_client.rest_client, "request_counts", None)
            if not sdk_usage:
                log.debug("SDK profiling not available in this version of flywheel-sdk")
            else:
                log.debug(f"SDK usage:\n{pformat(sdk_usage, indent=2)}")

    def _validate_bids_download(self, container_type, target_dir, **kwargs):
        """Prepare and validate `flywheel_bids.export_bids.download_bids_dir` arguments.

        Args:
            container_type (str): The container type for which to download BIDs (i.e.
                "session", "project")
            target_dir (pathlib.Path or str or None): The path to which to download the
                BIDs hierarchy
            **kwargs: kwargs for ``flywheel_bids.export_bids.download_bids_dir``

        Returns:
            (tuple): Tuple containing:
                (str): ID of the destinations container's parent of type
                    `container_type`.
                (pathlib.Path): Path to which BIDS will be downloaded.
                (function): flywheel_bids.export_bids.download_bids_dir.
                (dict): Keyword arguments to be passed to download_bids_dir.
        """
        # Raise a specific error if BIDS not installed
        download_bids_dir = self._load_download_bids()

        if not target_dir:
            target_dir = self.work_dir / "bids"
        elif isinstance(target_dir, pathlib.Path):
            pass
        elif isinstance(target_dir, str):
            target_dir = pathlib.Path(target_dir)
        else:
            raise TypeError(
                f"BIDs target_dir {target_dir} is of unexpected type ({type(target_dir)})"
            )
        # create target_dir if it doesn't exist
        if not target_dir.exists():
            target_dir.mkdir(parents=True)

        # Cleanup kwargs
        for key in ("subjects", "sessions", "folders"):
            if key in kwargs and kwargs[key] is None:
                kwargs.pop(key)

        # Resolve container type from parents
        dest_container = self.client.get(self.destination["id"])

        parent_id = dest_container.get(container_type)
        if parent_id is None:
            parent_id = dest_container.get("parents", {}).get(container_type)

        if parent_id is None:
            raise RuntimeError("Cannot find {} from destination".format(container_type))

        log.info("Using source container: %s=%s", container_type, parent_id)

        return parent_id, target_dir, download_bids_dir, kwargs

    def _load_download_bids(self):
        """Load the download_bids_dir function from flywheel_bids."""
        try:
            from flywheel_bids.export_bids import (
                download_bids_dir,  # pylint: disable=import-outside-toplevel
            )

            return download_bids_dir
        except ImportError:
            log.error("Cannot load flywheel-bids package.")
            log.error('Make sure it is installed with "pip install flywheel-bids"')
            raise RuntimeError("Unable to load flywheel-bids package, make sure it is installed!")

    @staticmethod
    def _load_json(filepath):
        """Return dictionary for input json file.

        Args:
          filepath (str): Path to a JSON file.

        Raises:
            RuntimeError: If filepath cannot be parsed as JSON.

        Returns:
            (dict): The dictionary representation of the JSON file at filepath.
        """
        json_dict = dict()
        if os.path.isfile(filepath):
            try:
                with open(filepath, "r") as f:
                    json_dict = json.load(f)
            except json.JSONDecodeError:
                raise RuntimeError(f"Cannot parse {filepath} as JSON.")

        return json_dict

    def _clean_output(self):
        for path in pathlib.Path(self.output_dir).glob("**/*"):
            if path.is_file():
                path.unlink()
            elif path.is_dir():
                rmtree(path)
