"""
# Setup

This module defines the Setup, which contains the complete configuration information for a test.

The Setup class contains all configuration items that are specific for a test or observation
and is normally (during nominal operation/testing) loaded automatically from the configuration
manager. The Setup includes type and identification of hardware that is used, calibration files,
software versions, reference frames and coordinate systems that link positions of alignment
equipment, conversion functions for temperature sensors, etc.

The configuration information that is in the Setup can be navigated in two different ways. First,
the Setup is a dictionary, so all information can be accessed by keys as in the following example.

    >>> setup = Setup({"gse": {"hexapod": {"ID": 42, "calibration": [0,1,2,3,4,5]}}})
    >>> setup["gse"]["hexapod"]["ID"]
    42

Second, each of the _keys_ is also available as an attribute of the Setup and that make it
possible to navigate the Setup with dot-notation:

    >>> id = setup.gse.hexapod.ID

In the above example you can see how to navigate from the setup to a device like the PUNA Hexapod.
The Hexapod device is connected to the control server and accepts commands as usual. If you want to
know which keys you can use to navigate the Setup, use the `keys()` method.

    >>> setup.gse.hexapod.keys()
    dict_keys(['ID', 'calibration'])
    >>> setup.gse.hexapod.calibration
    [0, 1, 2, 3, 4, 5]

To get a full printout of the Setup, you can use the `pretty_str()` method. Be careful, because
this can print out a lot of information when a full Setup is loaded.

    >>> print(setup)
    Setup
    └── gse
        └── hexapod
            ├── ID: 42
            └── calibration: [0, 1, 2, 3, 4, 5]

### Special Values

Some of the information in the Setup is interpreted in a special way, i.e. some values are
processed before returning. Examples are the device classes and calibration/data files. The
following values are treated special if they start with:

* `class//`: instantiate the class and return the object
* `factory//`: instantiates a factory and executes its `create()` method
* `csv//`: load the CSV file and return a numpy array
* `yaml//`: load the YAML file and return a dictionary
* `pandas//`: load a CSV file into a pandas Dataframe
* `int-enum//`: dynamically create the enumeration and return the Enum object

#### Device Classes

Most of the hardware components in the Setup will have a `device` key that defines the class for
the device controller. The `device` keys have a value that starts with `class//` and it will
return the device object. As an example, the following defines the Hexapod device:

    >>> setup = Setup(
    ...   {
    ...     "gse": {
    ...       "hexapod": {"ID": 42, "device": "class//egse.hexapod.symetrie.puna.PunaSimulator"}
    ...     }
    ...   }
    ... )
    >>> setup.gse.hexapod.device.is_homing_done()
    False
    >>> setup.gse.hexapod.device.info()
    'Info about the PunaSimulator...'

In the above example you see that we can call the `is_homing_done()` and `info()` methodes
directly on the device by navigating the Setup. It would however be better (more performant) to
put the device object in a variable and work with that variable:

    >>> hexapod = setup.gse.hexapod.device
    >>> hexapod.homing()
    >>> hexapod.is_homing_done()
    True
    >>> hexapod.get_user_positions()

If you need, for some reason, to have access to the actual raw value of the hexapod device key,
use the `get_raw_value()` method:

    >>> setup.gse.hexapod.get_raw_value("device")
    <egse.hexapod.symetrie.puna.PunaSimulator object at ...

#### Data Files

Some information is too large to add to the Setup as such and should be loaded from a data file.
Examples are calibration files, flat-fields, temperature conversion curves, etc.

The Setup will automatically load the file when you access a key that contains a value that
starts with `csv//` or `yaml//`.

    >>> setup = Setup({
    ...     "instrument": {"coeff": "csv//cal_coeff_1234.csv"}
    ... })
    >>> setup.instrument.coeff[0, 4]
    5.0

Note: the resource location is always relative to the path defined by the *PROJECT*_CONF_DATA_LOCATION
environment variable.

The Setup inherits from a NavigableDict (aka navdict) which is also defined in this module.

---

"""

from __future__ import annotations

__all__ = [
    "Setup",
    "navdict",  # noqa: ignore typo
    "list_setups",
    "load_setup",
    "get_setup",
    "submit_setup",
    "SetupError",
    "load_last_setup_id",
    "save_last_setup_id",
]

import csv
import enum
import importlib
import logging
import os
import re
import textwrap
import warnings
from functools import lru_cache
from pathlib import Path
from typing import Any
from typing import Optional
from typing import Union

import rich
from ruamel.yaml import YAML
from rich.tree import Tree

logger = logging.getLogger("cgse-setup")


class SetupError(Exception):
    """A setup-specific error."""


def _load_class(class_name: str):
    """
    Find and returns a class based on the fully qualified name.

    A class name can be preceded with the string `class//` or `factory//`. This is used in YAML
    files where the class is then instantiated on load.

    Args:
        class_name (str): a fully qualified name for the class
    """
    if class_name.startswith("class//"):
        class_name = class_name[7:]
    elif class_name.startswith("factory//"):
        class_name = class_name[9:]

    module_name, class_name = class_name.rsplit(".", 1)
    module = importlib.import_module(module_name)
    return getattr(module, class_name)


def _load_csv(resource_name: str):
    """Find and return the content of a CSV file."""

    if resource_name.startswith("csv//"):
        resource_name = resource_name[5:]

    parts = resource_name.rsplit("/", 1)
    in_dir, fn = parts if len(parts) > 1 else [None, parts[0]]

    try:
        csv_location = Path(in_dir or '.') / fn
        with open(csv_location, 'r', encoding='utf-8') as file:
            csv_reader = csv.reader(file)
            data = list(csv_reader)
    except FileNotFoundError:
        logger.error(f"Couldn't load resource '{resource_name}', file not found", exc_info=True)
        raise

    return data


def _load_int_enum(enum_name: str, enum_content):
    """Dynamically build (and return) and IntEnum.

    Args:
        - enum_name: Enumeration name (potentially prepended with "int_enum//").
        - enum_content: Content of the enumeration, as read from the setup.
    """
    if enum_name.startswith("int_enum//"):
        enum_name = enum_name[10:]

    definition = {}
    for side_name, side_definition in enum_content.items():
        if "alias" in side_definition:
            aliases = side_definition["alias"]
        else:
            aliases = []
        value = side_definition["value"]

        definition[side_name] = value

        for alias in aliases:
            definition[alias] = value
    return enum.IntEnum(enum_name, definition)


def _load_yaml(resource_name: str):
    """Find and return the content of a YAML file."""

    if resource_name.startswith("yaml//"):
        resource_name = resource_name[6:]

    parts = resource_name.rsplit("/", 1)

    in_dir, fn = parts if len(parts) > 1 else [None, parts[0]]

    try:
        yaml_location = Path(in_dir or '.')

        yaml = YAML(typ='safe')
        with open(yaml_location / fn, 'r') as file:
            data = yaml.load(file)

    except FileNotFoundError:
        logger.error(f"Couldn't load resource '{resource_name}', file not found", exc_info=True)
        raise
    except IsADirectoryError:
        logger.error(f"Couldn't load resource '{resource_name}', file seems to be a directory", exc_info=True)
        raise

    return data


def _get_attribute(self, name, default):
    try:
        attr = object.__getattribute__(self, name)
    except AttributeError:
        attr = default
    return attr


def _parse_filename_for_setup_id(filename: str) -> str | None:
    """Returns the setup_id from the filename, or None when no match was found."""

    # match = re.search(r"SETUP_([^_]+)_(\d+)", filename)
    match = re.search(r"SETUP_(\w+)_([\d]{5})_([\d]{6})_([\d]{6})\.yaml", filename)

    # TypeError when match is None

    try:
        return match[2]  # match[2] is setup_id
    except (IndexError, TypeError):
        return None


def disentangle_filename(filename: str) -> tuple:
    """
    Returns the site_id and setup_id (as a tuple) that is extracted from the Setups filename.

    Args:
        filename (str): the filename or fully qualified file path as a string.

    Returns:
        A tuple (site_id, setup_id).
    """
    if filename is None:
        return ()

    match = re.search(r"SETUP_(\w+)_([\d]{5})_([\d]{6})_([\d]{6})\.yaml", filename)

    if match is None:
        return ()

    site_id, setup_id = match[1], match[2]

    return site_id, setup_id


def get_last_setup_id_file_path(site_id: str = None) -> Path:
    """
    Return the fully expanded file path of the file containing the last loaded Setup in the configuration manager.
    The default location for this file is the data storage location.

    Args:
        site_id: The SITE identifier (overrides the SITE_ID environment variable)

    """
    location = get_data_storage_location(site_id=site_id)

    return Path(location).expanduser().resolve() / "last_setup_id.txt"


def load_last_setup_id(site_id: str = None) -> int:
    """
    Returns the ID of the last Setup that was used by the configuration manager.
    The file shall only contain the Setup ID which must be an integer on the first line of the file.
    If no such ID can be found, the Setup ID = 0 will be returned.

    Args:
        site_id: The SITE identifier
    """

    last_setup_id_file_path = get_last_setup_id_file_path(site_id=site_id)
    try:
        with last_setup_id_file_path.open("r") as fd:
            setup_id = int(fd.read().strip())
    except FileNotFoundError:
        setup_id = 0
        save_last_setup_id(setup_id)

    return setup_id


def save_last_setup_id(setup_id: int | str, site_id: str = None):
    """
    Makes the given Setup ID persistent, so it can be restored upon the next startup.

    Args:
        setup_id: The Setup identifier to be saved
        site_id: The SITE identifier

    """

    last_setup_id_file_path = get_last_setup_id_file_path(site_id=site_id)
    with last_setup_id_file_path.open("w") as fd:
        fd.write(f"{int(setup_id):d}")


class NavigableDict(dict):
    """
    A NavigableDict is a dictionary where all keys in the original dictionary are also accessible
    as attributes to the class instance. So, if the original dictionary (setup) has a key
    "site_id" which is accessible as `setup['site_id']`, it will also be accessible as
    `setup.site_id`.

    Examples:
        >>> setup = NavigableDict({'site_id': 'KU Leuven', 'version': "0.1.0"})
        >>> assert setup['site_id'] == setup.site_id
        >>> assert setup['version'] == setup.version

    Note:
        We always want **all** keys to be accessible as attributes, or none. That means all
        keys of the original dictionary shall be of type `str`.

    """

    def __init__(self, head: dict = None, label: str = None):
        """
        Args:
            head (dict): the original dictionary
            label (str): a label or name that is used when printing the navdict
        """
        head = head or {}
        super().__init__(head)
        self.__dict__["_memoized"] = {}
        self.__dict__["_label"] = label

        # By agreement, we only want the keys to be set as attributes if all keys are strings.
        # That way we enforce that always all keys are navigable, or none.

        if any(True for k in head.keys() if not isinstance(k, str)):
            return

        for key, value in head.items():
            if isinstance(value, dict):
                setattr(self, key, NavigableDict(head.__getitem__(key)))
            else:
                setattr(self, key, head.__getitem__(key))

    def add(self, key: str, value: Any):
        """Set a value for the given key.

        If the value is a dictionary, it will be converted into a NavigableDict and the keys
        will become available as attributes provided that all the keys are strings.

        Args:
            key (str): the name of the key / attribute to access the value
            value (Any): the value to assign to the key
        """
        if isinstance(value, dict) and not isinstance(value, NavigableDict):
            value = NavigableDict(value)
        setattr(self, key, value)

    def clear(self) -> None:
        for key in list(self.keys()):
            self.__delitem__(key)

    def __repr__(self):
        return f"{self.__class__.__name__}({super()!r})"

    def __delitem__(self, key):
        dict.__delitem__(self, key)
        object.__delattr__(self, key)

    def __setattr__(self, key, value):
        # logger.info(f"called __setattr__({self!r}, {key}, {value})")
        if isinstance(value, dict) and not isinstance(value, NavigableDict):
            value = NavigableDict(value)
        self.__dict__[key] = value
        super().__setitem__(key, value)
        try:
            del self.__dict__["_memoized"][key]
        except KeyError:
            pass

    def __getattribute__(self, key):
        # logger.info(f"called __getattribute__({key})")
        value = object.__getattribute__(self, key)
        if isinstance(value, str) and value.startswith("class//"):
            try:
                dev_args = object.__getattribute__(self, "device_args")
            except AttributeError:
                dev_args = ()
            return _load_class(value)(*dev_args)
        if isinstance(value, str) and value.startswith("factory//"):
            factory_args = _get_attribute(self, f"{key}_args", {})
            return _load_class(value)().create(**factory_args)
        if isinstance(value, str) and value.startswith("int_enum//"):
            content = object.__getattribute__(self, "content")
            return _load_int_enum(value, content)
        if isinstance(value, str) and value.startswith("csv//"):
            if key in self.__dict__["_memoized"]:
                return self.__dict__["_memoized"][key]
            content = _load_csv(value)
            self.__dict__["_memoized"][key] = content
            return content
        if isinstance(value, str) and value.startswith("yaml//"):
            if key in self.__dict__["_memoized"]:
                return self.__dict__["_memoized"][key]
            content = _load_yaml(value)
            self.__dict__["_memoized"][key] = content
            return content
        if isinstance(value, str) and value.startswith("pandas//"):
            separator = object.__getattribute__(self, "separator")
            return _load_pandas(value, separator)
        else:
            return value

    def __delattr__(self, item):
        # logger.info(f"called __delattr__({self!r}, {item})")
        object.__delattr__(self, item)
        dict.__delitem__(self, item)

    def __setitem__(self, key, value):
        # logger.info(f"called __setitem__({self!r}, {key}, {value})")
        if isinstance(value, dict) and not isinstance(value, NavigableDict):
            value = NavigableDict(value)
        super().__setitem__(key, value)
        self.__dict__[key] = value
        try:
            del self.__dict__["_memoized"][key]
        except KeyError:
            pass

    def __getitem__(self, key):
        # logger.info(f"called __getitem__({self!r}, {key})")
        value = super().__getitem__(key)
        if isinstance(value, str) and value.startswith("class//"):
            try:
                dev_args = object.__getattribute__(self, "device_args")
            except AttributeError:
                dev_args = ()
            return _load_class(value)(*dev_args)
        if isinstance(value, str) and value.startswith("csv//"):
            return _load_csv(value)
        if isinstance(value, str) and value.startswith("int_enum//"):
            content = object.__getattribute__(self, "content")
            return _load_int_enum(value, content)
        else:
            return value

    def set_private_attribute(self, key: str, value: Any) -> None:
        """Sets a private attribute for this object.

        The name in key will be accessible as an attribute for this object, but the key will not
        be added to the dictionary and not be returned by methods like keys().

        The idea behind this private attribute is to have the possibility to add status information
        or identifiers to this classes object that can be used by save() or load() methods.

        Args:
            key (str): the name of the private attribute (must start with an underscore character).
            value: the value for this private attribute

        Examples:
            >>> setup = NavigableDict({'a': 1, 'b': 2, 'c': 3})
            >>> setup.set_private_attribute("_loaded_from_dict", True)
            >>> assert "c" in setup
            >>> assert "_loaded_from_dict" not in setup
            >>> assert setup.get_private_attribute("_loaded_from_dict") == True

        """
        if key in self:
            raise ValueError(f"Invalid argument key='{key}', this key already exists in dictionary.")
        if not key.startswith("_"):
            raise ValueError(f"Invalid argument key='{key}', must start with underscore character '_'.")
        self.__dict__[key] = value

    def get_private_attribute(self, key: str) -> Any:
        """Returns the value of the given private attribute.

        Args:
            key (str): the name of the private attribute (must start with an underscore character).

        Returns:
            the value of the private attribute given in `key`.

        Note:
            Because of the implementation, this private attribute can also be accessed as a 'normal'
            attribute of the object. This use is however discouraged as it will make your code less
            understandable. Use the methods to access these 'private' attributes.
        """
        if not key.startswith("_"):
            raise ValueError(f"Invalid argument key='{key}', must start with underscore character '_'.")
        return self.__dict__[key]

    def has_private_attribute(self, key):
        """
        Check if the given key is defined as a private attribute.

        Args:
            key (str): the name of a private attribute (must start with an underscore)
        Returns:
            True if the given key is a known private attribute.
        Raises:
            ValueError: when the key doesn't start with an underscore.
        """
        if not key.startswith("_"):
            raise ValueError(f"Invalid argument key='{key}', must start with underscore character '_'.")

        try:
            _ = self.__dict__[key]
            return True
        except KeyError:
            return False

    def get_raw_value(self, key):
        """
        Returns the raw value of the given key.

        Some keys have special values that are interpreted by the AtributeDict class. An example is
        a value that starts with 'class//'. When you access these values, they are first converted
        from their raw value into their expected value, e.g. the instantiated object in the above
        example. This method allows you to access the raw value before conversion.
        """
        try:
            return object.__getattribute__(self, key)
        except AttributeError:
            raise KeyError(f"The key '{key}' is not defined.")

    def __str__(self):
        return self.pretty_str()

    def pretty_str(self, indent: int = 0):
        """
        Returns a pretty string representation of the dictionary.

        Args:
            indent (int): number of indentations (of four spaces)

        Note:
            The indent argument is intended for the recursive call of this function.
        """
        msg = ""

        for k, v in self.items():
            if isinstance(v, NavigableDict):
                msg += f"{'    ' * indent}{k}:\n"
                msg += v.pretty_str(indent + 1)
            else:
                msg += f"{'    ' * indent}{k}: {v}\n"

        return msg

    def __rich__(self) -> Tree:
        tree = Tree(self.__dict__["_label"] or "NavigableDict", guide_style="dim")
        walk_dict_tree(self, tree, text_style="dark grey")
        return tree

    def _save(self, fd, indent: int = 0):
        """
        Recursive method to write the dictionary to the file descriptor.

        Indentation is done in steps of four spaces, i.e. `'    '*indent`.

        Args:
            fd: a file descriptor as returned by the open() function
            indent (int): indentation level of each line [default = 0]

        """
        from egse.device import DeviceInterface

        # Note that the .items() method returns the actual values of the keys and doesn't use the
        # __getattribute__ or __getitem__ methods. So the raw value is returned and not the
        # _processed_ value.

        for k, v in self.items():
            # history shall be saved last, skip it for now

            if k == "history":
                continue

            # make sure to escape a colon in the key name

            if isinstance(k, str) and ":" in k:
                k = '"' + k + '"'

            if isinstance(v, NavigableDict):
                fd.write(f"{'    ' * indent}{k}:\n")
                v._save(fd, indent + 1)
                fd.flush()
                continue

            if isinstance(v, DeviceInterface):
                v = f"class//{v.__module__}.{v.__class__.__name__}"
            if isinstance(v, float):
                v = f"{v:.6E}"
            fd.write(f"{'    ' * indent}{k}: {v}\n")
            fd.flush()

        # now save the history as the last item

        if "history" in self:
            fd.write(f"{'    ' * indent}history:\n")
            self.history._save(fd, indent + 1)

    def get_memoized_keys(self):
        return list(self.__dict__["_memoized"].keys())


navdict = NavigableDict  # noqa: ignore typo
"""Shortcut for NavigableDict and more Pythonic."""


class Setup(NavigableDict):
    """The Setup class represents a version of the configuration of the test facility, the
    test setup and the Camera Under Test (CUT)."""

    def __init__(self, nav_dict: NavigableDict | dict = None, label: str = None):
        super().__init__(nav_dict or {}, label=label)

    @staticmethod
    def from_dict(my_dict) -> Setup:
        """Create a Setup from a given dictionary.

        Remember that all keys in the given dictionary shall be of type 'str' in order to be
        accessible as attributes.

        Examples:
            >>> setup = Setup.from_dict({"ID": "my-setup-001", "version": "0.1.0"})
            >>> assert setup["ID"] == setup.ID == "my-setup-001"

        """
        return Setup(my_dict, label="Setup")

    @staticmethod
    def from_yaml_string(yaml_content: str = None) -> Setup:
        """Loads a Setup from the given YAML string.

        This method is mainly used for easy creation of Setups from strings during unit tests.

        Args:
            yaml_content (str): a string containing YAML

        Returns:
            a Setup that was loaded from the content of the given string.
        """

        if not yaml_content:
            raise ValueError("Invalid argument to function: No input string or None given.")

        setup_dict = yaml.safe_load(yaml_content)

        if "Setup" in setup_dict:
            setup_dict = setup_dict["Setup"]

        return Setup(setup_dict, label="Setup")

    @staticmethod
    @lru_cache(maxsize=300)
    def from_yaml_file(filename: Union[str, Path] = None, add_local_settings: bool = True) -> Setup:
        """Loads a Setup from the given YAML file.

        Args:
            filename (str): the path of the YAML file to be loaded
            add_local_settings (bool): if local settings shall be loaded and override the settings from the YAML file.

        Returns:
            a Setup that was loaded from the given location.

        Raises:
            ValueError: when no filename is given.
        """

        if not filename:
            raise ValueError("Invalid argument to function: No filename or None given.")

        # logger.info(f"Loading {filename}...")

        setup_dict = read_configuration_file(filename, force=True)
        if setup_dict == {}:
            warnings.warn(f"Empty Setup file: {filename!s}")

        try:
            setup_dict = setup_dict["Setup"]
        except KeyError:
            warnings.warn(f"Setup file doesn't have a 'Setup' group: {filename!s}")

        setup = Setup(setup_dict, label="Setup")
        setup.set_private_attribute("_filename", Path(filename))
        if setup_id := _parse_filename_for_setup_id(str(filename)):
            setup.set_private_attribute("_setup_id", setup_id)

        return setup

    def to_yaml_file(self, filename=None):
        """Saves a NavigableDict to a YAML file.

        When no filename is provided, this method will look for a 'private' attribute
        `_filename` and use that to save the data.

        Args:
            filename (str|Path): the path of the YAML file where to save the data

        Note:
            This method will **overwrite** the original or given YAML file and therefore you might
            lose proper formatting and/or comments.

        """
        if not filename:
            try:
                filename = self.get_private_attribute("_filename")
            except KeyError:
                raise ValueError("No filename given or known, can not save Setup.")

        print(f"Saving Setup to {filename!s}")

        with Path(filename).open("w") as fd:
            fd.write(f"# Setup generated by:\n#\n#    Setup.to_yaml_file(setup, filename='{filename}')\n#\n")
            fd.write(f"# Created on {format_datetime()}\n\n")
            fd.write("Setup:\n")

            self._save(fd, indent=1)

        self.set_private_attribute("_filename", Path(filename))

    def __rich__(self) -> Tree:
        tree = super().__rich__()

        if self.has_private_attribute("_filename"):
            filename = self.get_private_attribute("_filename")
            tree.add(f"Loaded from: {filename}", style="grey50")

        return tree

    def get_filename(self) -> str | None:
        """Returns the filename for this Setup or None when no filename could be determined."""
        if self.has_private_attribute("_filename"):
            return self.get_private_attribute("_filename")
        else:
            return None
