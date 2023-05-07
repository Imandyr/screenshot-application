""" Main application module """


# global imports
import sys
import datetime
from abc import ABC, abstractmethod
from typing import Any, List
from system_hotkey import SystemHotkey

# local imports
from .settings import ErrorWindow
from .main_window import MainWindow
from ..backend.settings import Settings
from ..errors.errors import ValidationError


class Application(ABC):
    """
    Base version of main application class.
    Used to work with application settings and initialize main window of application.

    attributes:
        settings_file_path: Path to settings file.
        settings: Dictionary with all application settings.
        main_window: Application main window object inherited from TK.

    methods:
        start_main_window: Method for starting a main window of application.

    """

    settings_file_path: str
    settings: Settings
    main_window: MainWindow

    @abstractmethod
    def __init__(self, *args, **kwargs) -> None:
        """ Initialization of class object """

    @abstractmethod
    def start_main_window(self, *args, **kwargs) -> None:
        """ Activate main window of application """


class ScreenshotApplication(Application):
    """
    Main class of application.
    Used to work with application settings and initialize main window of application.

    """

    def __init__(self, settings_file_path: str, *args, **kwargs) -> None:
        """
        Main class of application.
        Used to work with application settings and initialize main window of application.

        While initialized, create or load json file with settings by settings_file_path,
        create settings dict for all settings of application and create main_window object.

        :param settings_file_path: path for json file with settings.
        :param args: Args of Application.
        :param kwargs: Kwargs of Application.
        :return: None.

        """
        super().__init__(*args, **kwargs)
        print(f"Screenshot Application running ({datetime.datetime.now()})")

        # add settings file path
        self.settings_file_path = settings_file_path
        # create SystemHotkey object
        self.hk = SystemHotkey()

        try:
            # try to load settings from file
            self.settings = Settings.from_json(self.settings_file_path)
            # create main_window object
            self.main_window = MainWindow(self.settings)

        # if settings loading fails on validation, open window with error message instead and then raise exception
        except ValidationError as error:
            ErrorWindow("Screenshot Application Error", str(error))
            raise

    def start_main_window(self, *args, **kwargs) -> None:
        """
        Method what launch the main application window.

        :param args: args
        :param kwargs: kwargs
        :return: None
        """
        super().start_main_window(*args, **kwargs)

        # add hotkeys
        full_screenshot_hotkey = self.settings["full_screenshot_hotkey"]
        cropped_screenshot_hotkey = self.settings["cropped_screenshot_hotkey"]
        self.add_hotkey(self.hk, full_screenshot_hotkey,
                        lambda event: self.main_window.main_page.full_screenshot.create_screenshot())
        self.add_hotkey(self.hk, cropped_screenshot_hotkey,
                        lambda event: self.main_window.main_page.cropped_screenshot.create_screenshot())

        # run main window of application
        self.main_window.mainloop()

        # delete hotkeys when main window is closed
        self.hk.unregister(full_screenshot_hotkey)
        self.hk.unregister(cropped_screenshot_hotkey)

        # stop this instance of application
        print(f"Screenshot Application closed ({datetime.datetime.now()})")
        sys.exit()

    @staticmethod
    def add_hotkey(hk: SystemHotkey, key: List[str], func: Any, *args, **kwargs) -> None:
        """
        Method for adding hotkey to function using SystemHotkey.

        :param hk: SystemHotkey object what will be used to add hotkeys.
        :param key: List of str with sequence of keyboard key what should be pressed for function activation.
        :param func: Function what should be activated on hotkey press.
        :param args: hk args.
        :param kwargs: hk kwargs.
        :return: None
        """
        hk.register(key, callback=func, overwrite=True, *args, **kwargs)











