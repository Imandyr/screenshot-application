""" Module with various settings related functions and classes """

# global imports
import os
import json
# import time
# import collections
from enum import Enum
from pathlib import Path
from system_hotkey import SystemHotkey, InvalidKeyError, SystemRegisterError  # , util

# local imports
from ..errors.errors import InvalidFileFormat, ReadFileError, ValidationError


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

        # create hotkey object
        hk = SystemHotkey()

        # create dict with all necessary settings keys and their types
        keys = {
            "use_global_save_dir": "bool", "global_save_dir": "str", "use_global_file_format": "bool",
            "global_file_format": "str", "enable_sound": "bool", "clipboard_copy": "bool",
            "full_screenshot_hotkey": ["str"], "cropped_screenshot_hotkey": ["str"],
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
                    raise ValidationError(f"Value of settings parameter '{key}' "
                                          f"should have shape and type '{keys[key]}'.")

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

        # check if clipboard_copy is True but os is not windows
        if self["clipboard_copy"] is True and not os.name == "nt":
            raise ValidationError("Copying screenshot image to clipboard available only on Windows system.")

        # check if full_screenshot_hotkey and cropped_screenshot_hotkey have the same value
        if self["full_screenshot_hotkey"] == self["cropped_screenshot_hotkey"]:
            raise ValidationError("Hotkeys for Full screenshot and Cropped screenshot cannot be the same.")

        # check if hotkeys for full_screenshot_hotkey and cropped_screenshot_hotkey is supported by system_hotkey
        try:
            hk.parse_hotkeylist(self["full_screenshot_hotkey"])
        except (SystemRegisterError, InvalidKeyError):
            raise ValidationError(f"Hotkey combination '{self['full_screenshot_hotkey']}' "
                                  f"for parameter 'full_screenshot_hotkey' is not supported.")
        try:
            hk.parse_hotkeylist(self["cropped_screenshot_hotkey"])
        except (SystemRegisterError, InvalidKeyError):
            raise ValidationError(f"Hotkey combination '{self['cropped_screenshot_hotkey']}' "
                                  f"for parameter 'cropped_screenshot_hotkey' is not supported.")

        # code below is my attempt to catch strange exception when been said that hotkey is already be in use,
        # but in reality it isn't (like when you try to use ["shift", "f12"] as hotkey combination).
        # the problem with this exception been in impossibility to catch it normally,
        # because it has been ignored in thread and main script just continuing its execution without noticing.

        # I try different approaches, but I just can't handle it and for now It's still a problem.

        # # function for direct register of keys for bypassing .register(), because this method is run in thread
        # # and I can't catch exceptions from there
        # def direct_register(hotkey: collections.Iterable, callback=None, overwrite=True, *args) -> None:
        #     """Its looks bad, but I can't fild better solution to check is hotkey already in use or not."""
        #     assert isinstance(hotkey, collections.Iterable) and type(hotkey) not in (str, bytes)
        #     target_key = hk.order_hotkey(hotkey)
        #     keycode, masks = hk.parse_hotkeylist(target_key)
        #     if tuple(hotkey) in hk.keybinds:
        #         if overwrite:
        #             hk.unregister(hotkey)
        #         else:
        #             msg = 'existing bind detected... unregister or set overwrite to True'
        #             raise SystemRegisterError(msg, *hotkey)
        #     if os.name == 'nt':
        #         def reg():
        #             uniq = util.unique_int(hk.hk_ref.keys())
        #             hk.hk_ref[uniq] = (keycode, masks)
        #             hk._nt_the_grab(keycode, masks, uniq)
        #         hk.hk_action_queue.put(lambda: reg())
        #         time.sleep(hk.check_queue_interval * 3)
        #     else:
        #         hk._the_grab(keycode, masks)
        #     if callback:
        #         hk.keybinds[tuple(target_key)] = callback
        #     else:
        #         hk.keybinds[tuple(target_key)] = args
        #     if hk.verbose:
        #         print('Printing all keybinds')
        #         print(hk.keybinds)
        #     if os.name == 'posix' and hk.use_xlib:
        #         hk.disp.flush()
        #
        #     if not hk.hk_action_queue.empty():
        #         try:
        #             exc = hk.hk_action_queue.get(block=False)
        #             x = exc()
        #             print(x)
        #         except Exception as ex:
        #             raise SystemRegisterError()
        #     else:
        #         pass
        #
        # # check if hotkeys for full_screenshot_hotkey and cropped_screenshot_hotkey is already in use
        # try:
        #     # hk.register(self["full_screenshot_hotkey"], callback=lambda x: 0)
        #     direct_register(self["full_screenshot_hotkey"], callback=lambda x: 0)
        #     hk.unregister(self["full_screenshot_hotkey"])
        # except SystemRegisterError:
        #     raise ValidationError(f"Hotkey combination '{self['full_screenshot_hotkey']}' "
        #                           f"for parameter 'full_screenshot_hotkey' is invalid or "
        #                           f"could be already in use elsewhere.")
        # try:
        #     # hk.register(self["cropped_screenshot_hotkey"], callback=lambda x: 0)
        #     direct_register(self["cropped_screenshot_hotkey"], callback=lambda x: 0)
        #     hk.unregister(self["cropped_screenshot_hotkey"])
        # except SystemRegisterError:
        #     raise ValidationError(f"Hotkey combination '{self['cropped_screenshot_hotkey']}' "
        #                           f"for parameter 'cropped_screenshot_hotkey' is invalid or "
        #                           f"could be already in use elsewhere.")

    def write_settings_file(self) -> None:
        """
        Method for writing settings dict to settings json file.

        :return: None
        """

        # open file
        with open(file=self.settings_file_path, encoding="utf-8", mode="w") as settings_file:
            # try to write settings dict to file
            try:
                json.dump(self, settings_file)
            except Exception:
                raise Exception("Exception occurred during settings file write")

    def load_settings_file(self) -> None:
        """
        Method for loading settings from json settings file and set it values to settings dict.

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
