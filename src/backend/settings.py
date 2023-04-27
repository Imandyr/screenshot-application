""" Module with various settings related functions and classes """


# global imports
from pathlib import Path
import os
import json
from enum import Enum
import tkinter as tk
from tkinter import messagebox
# import tkinter.ttk as ttk

# local imports
from ..errors.errors import InvalidFileFormat, ReadFileError, ValidationError


class ErrorWindow(tk.Tk):
    """
    Class of error window what shows given error message and then destroy itself.
    """
    def __init__(self, header: str, message: str, *args, **kwargs) -> None:
        """
        Class of error window what shows given error message and then destroy itself.

        When initialized, creates invisible tkinter window, show error message and then delete itself.

        :param header: header of error message.
        :param message: message of error.
        :param args: Args of Tk.
        :param kwargs: Kwargs of Tk.
        """
        super().__init__(*args, **kwargs)

        # make this window invisible
        self.withdraw()
        # show error message
        messagebox.showerror(header, message)
        # delete this window
        self.destroy()


class SupportedImageFormats(Enum):
    """
    Class for enumeration of supported image file formats.
    """
    png, PNG = "png", "PNG"
    jpeg, JPEG, jpg, JPG = "jpeg", "JPEG", "jpg", "JPG"
    bmp, BMP = "bmp", "BMP"


class Settings(dict):
    """
    Class of application settings.
    Used to load, write and validate settings.

    methods:
        from_json: Method for loading and validating of settings from json file.
        validate_settings_dict: Method for validation of settings values inside settings object.
        write_settings_file: Method for writing values from settings dict to settings file.
        load_settings_file: Method for loading values from settings file to settings dict.

    """

    @classmethod
    def from_json(cls, settings_file_path: str, *args, **kwargs) -> "Settings":
        """
        Class method for creation of settings object by loading it from json file and perform validation of values.

        :param settings_file_path: Path to settings file.
        :param args: Args for cls initialisation.
        :param kwargs: Kwargs for cls initialisation.
        :return: Instance of Settings class with values from json file.
        """

        # create Settings class instance
        self = cls(settings_file_path, *args, **kwargs)
        # load values from json file
        self.load_settings_file()
        # perform validation
        self.validate_settings_dict()

        # return settings object
        return self

    def __init__(self, settings_file_path: str, *args, **kwargs) -> None:
        """
        Class of application settings.
        Used to load, write and validate settings.

        When initialized, add

        :param settings_file_path: Path to settings file.
        :param args: Args for superclass initialisation.
        :param kwargs: Kwargs for superclass initialisation.
        """
        super().__init__(*args, **kwargs)

        # add settings file path
        self.settings_file_path = settings_file_path

    def validate_settings_dict(self) -> None:
        """
        Function for perform validation of settings values in given settings dict.
        If validation fails, raises an exception with description of problem.

        :return: None or raise an exception.
        """

        # create dict with all necessary settings keys and their types
        keys = {
            "use_global_save_dir": "bool", "global_save_dir": "str", "use_global_file_format": "bool",
            "global_file_format": "str", "enable_sound": "bool", "full_screenshot_hotkey": ["str"],
            "cropped_screenshot_hotkey": ["str"],
        }

        # check the presence of necessary settings keys
        for key in keys.keys():
            try:
                value = self[key]
            except Exception:
                raise ValidationError(f"Necessary parameter '{key}' isn't specified in settings.")

            # check types of values
            if str(type(value).__name__) != keys[key] and not type(value) == list:
                raise ValidationError(f"Value of settings parameter '{key}' should have type '{keys[key]}'.")

            # if type of value is list, check type of elements in it
            if type(value) == list:
                try:
                    if len(value) > 0:
                        for e in value:
                            if str(type(e).__name__) != keys[key][0]:
                                raise ValueError
                    else:
                        raise ValueError
                except Exception:
                    raise ValidationError(f"Value of settings parameter '{key}' should have type '{keys[key]}'.")

        # check if "use_global_save_dir" is enabled
        if not self["use_global_save_dir"]:
            raise ValidationError(f"Settings parameter 'use_global_save_dir'should have value 'true'.")

        # check if "use_global_file_format" is enabled
        if not self["use_global_file_format"]:
            raise ValidationError(f"Settings parameter 'use_global_file_format' should have value 'true'.")

        # check existence of "global_save_dir" directory
        if not os.path.exists(self["global_save_dir"]):
            raise ValidationError(f"Directory '{self['global_save_dir']}' "
                                  f"from settings parameter 'global_save_dir' isn't exist.")

        # check if image format in "global_file_format" is supported
        try:
            SupportedImageFormats(self["global_file_format"])
        except ValueError:
            raise ValidationError(f"File format '{self['global_file_format']}' from settings parameter "
                                  f"'global_file_format' isn't supported.")

    def write_settings_file(self, *args, **kwargs) -> None:
        """
        Method for writing settings dict to settings json file.

        :param args: args
        :param kwargs: kwargs
        :return: None
        """

        # open file
        with open(file=self.settings_file_path, encoding="utf-8", mode="w") as settings_file:
            # try to write settings dict to file
            try:
                json.dump(self, settings_file)
            except Exception:
                raise Exception("Exception occurred during settings file write")

    def load_settings_file(self, *args, **kwargs) -> None:
        """
        Method for loading settings from json settings file and set it values to settings dict.

        :param args: args
        :param kwargs: kwargs
        :return: None
        """

        # check if settings file exist
        if os.path.exists(self.settings_file_path):
            # check if file format is .json
            if Path(self.settings_file_path).suffix == '.json':
                # try to load settings dict from file
                try:
                    # open file
                    with open(file=self.settings_file_path, encoding="utf-8", mode="r") as settings_file:
                        # try to load settings dict from file
                        settings = json.load(settings_file)
                        self.update(settings)
                except Exception:
                    raise ReadFileError("Settings file is invalid and cannot be loaded correctly.")
            else:
                raise InvalidFileFormat("Settings file must be in .json format.")
        else:
            raise FileNotFoundError("Settings file didn't exist or placed in a different directory.")












