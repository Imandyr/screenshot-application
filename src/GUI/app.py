""" Main application module """


# global imports
from abc import ABC, abstractmethod
import tkinter as tk
import tkinter.ttk as ttk
from pathlib import Path
import os
import json
from typing import Any, List
from system_hotkey import SystemHotkey


# local imports
from .widgets import WidgetScrollbar
from .screenshot_widgets import FullScreenshotWidget, CroppedScreenshotWidget


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
    if type(key) == list and type(key[0]) == str:
        try:
            hk.register(key, callback=func, *args, **kwargs)
        except Exception:
            raise Exception(f"Hotkey sequence {key} or function {func} may be invalid.")
    else:
        raise TypeError(f"Hotkey sequence {key} must be in type List[str], but it isn't.")


class Application(ABC):
    """
    Base version of main application class.
    Used to work with application settings and initialize main window of application.

    attributes:
        settings_file_path: Path to settings file.
        settings: Dictionary with all application settings.
        main_window: Application main window object inherited from TK.

    methods:
        write_settings_file: Method for writing values from settings dict to settings file.
        load_settings_file: Method for loading values from settings file to settings dict.
        start_main_window: Method for starting a main window of application.

    """

    settings_file_path: str
    settings: dict
    main_window: tk.Tk

    @abstractmethod
    def __init__(self, *args, **kwargs) -> None:
        """ Initialization of class object """

    @abstractmethod
    def write_settings_file(self, *args, **kwargs) -> None:
        """ Write settings dict to file """

    @abstractmethod
    def load_settings_file(self, *args, **kwargs) -> None:
        """ Load settings dict from file """

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
        :param args: args
        :param kwargs: kwargs
        :return: None

        """
        super().__init__(*args, **kwargs)

        # create settings dict
        self.settings = {}
        # add settings file path
        self.settings_file_path = settings_file_path

        # check if file format is .json
        if Path(self.settings_file_path).suffix == '.json':
            try:
                # load or create settings file depending on it's existence
                if os.path.exists(settings_file_path):
                    self.load_settings_file()
                else:
                    self.write_settings_file()
            except Exception:
                raise ValueError("Settings file is invalid and cannot be loaded correctly.")
        else:
            raise ValueError("Settings file must be in .json format.")

        # create main_window object
        self.main_window = MainWindow(self)

    def write_settings_file(self, *args, **kwargs) -> None:
        """
        Method for writing settings dict to settings json file.

        :param args: args
        :param kwargs: kwargs
        :return: None
        """
        super().write_settings_file(*args, **kwargs)

        # open file
        with open(file=self.settings_file_path, encoding="utf-8", mode="w") as settings_file:
            # try to write settings dict to file
            try:
                json.dump(self.settings, settings_file)
            except Exception:
                raise Exception("Exception occurred during settings file write")

    def load_settings_file(self, *args, **kwargs) -> None:
        """
        Method for loading settings from json settings file to settings dict

        :param args: args
        :param kwargs: kwargs
        :return: None
        """
        super().load_settings_file(*args, **kwargs)

        # open file
        with open(file=self.settings_file_path, encoding="utf-8", mode="r") as settings_file:
            # try to load settings dict from file
            try:
                self.settings = json.load(settings_file)
            except Exception:
                raise Exception("Exception occurred during settings file read")

    def start_main_window(self, *args, **kwargs) -> None:
        """
        Method what launch the main application window.

        :param args: args
        :param kwargs: kwargs
        :return: None
        """
        super().start_main_window(*args, **kwargs)

        # run main window of application
        self.main_window.mainloop()


class MainWindow(tk.Tk):
    """
    A main window of application where all objects from the main window be stored.

    """

    def __init__(self, application: Application, *args, **kwargs) -> None:
        """
        A main window of application where all objects from the main window be stored.

        When initialized, setup window parameters and create frame for MainPage object.

        :param application: Main application object with settings.
        """
        super().__init__(*args, **kwargs)

        # add icon to the main window
        try:
            self.iconphoto(True, tk.PhotoImage(file="./src/assets/icon.png"))
        except Exception:
            raise Exception("'icon.png' file should be in the './src/assets' directory.")

        # add title to the window
        self.wm_title("Screenshot Application")
        # make window not resizable
        self.resizable(False, False)

        # create frame and assigning it to container for all main window content
        self.container = tk.Frame(self, height=700, width=600)
        # specifying the region where the frame is packed in window
        self.container.pack(side="top", fill="both", expand=True)

        # configuring the location of the container using grid
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        # create MainPage frame object with all widgets and add it to container frame
        self.main_page = MainPage(self.container, self, application)
        self.main_page.grid(row=0, column=0, sticky="nsew")


class MainPage(tk.Frame):
    """
    A class containing all widgets from the main window.

    """

    def __init__(self, parent: tk.Frame, main_window: tk.Tk, application: Application, *args, **kwargs) -> None:
        """
        A class containing all widgets from the main window.

        When initialized, creates all widgets for main page.

        :param parent: Parent widget for this frame.
        :param main_window: Main window object of application.
        :param application: Instance of main application object.
        :param args: args
        :param kwargs: kwargs
        """
        super().__init__(parent, *args, **kwargs)

        # create WidgetScrollbar object for all screenshot widgets what should be listed in scrollbar
        self.screenshot_scrollbar = WidgetScrollbar(self)
        self.screenshot_scrollbar.canvas.configure(height=60)
        self.screenshot_scrollbar.pack(side="top", fill="both", expand=True)

        # create button for opening of settings window
        self.settings_button = tk.Button(self, text="settings", command=self.open_settings_window)
        self.settings_button.pack(side="bottom", fill="both", expand=True)
        # create label in what been stored path to settings file
        self.settings_label = tk.Label(self, text=f"settings file: '{application.settings_file_path}'")
        self.settings_label_pack = False

        # # create all ScreenshotWidget objects, based on frame contained inside screenshot_scrollbar

        # add widget of full screenshot creation
        self.full_screenshot = FullScreenshotWidget(self.screenshot_scrollbar.frame, application.settings)
        self.full_screenshot.pack(side="top", anchor="nw")

        # add widget for cropped screenshot creation
        self.cropped_screenshot = CroppedScreenshotWidget(self.screenshot_scrollbar.frame, main_window,
                                                          application.settings)
        self.cropped_screenshot.pack(side="top", anchor="nw")

        # # add hotkeys to all .create_screenshot() methods from all ScreenshotWidgets

        # create SystemHotkey object
        hk = SystemHotkey()

        # add hotkey to full_screenshot
        add_hotkey(hk, application.settings["full_screenshot_hotkey"],
                   lambda event: self.full_screenshot.create_screenshot())
        # add hotkey to cropped_screenshot
        add_hotkey(hk, application.settings["cropped_screenshot_hotkey"],
                   lambda event: self.cropped_screenshot.create_screenshot())

    def open_settings_window(self, *args, **kwargs) -> None:
        """
        Method for opening of settings menu.

        Should be done somewhere after settings window creation,
        but now its just show or hide path to settings file on label.

        """
        if self.settings_label_pack:
            self.settings_label.pack_forget()
            self.settings_label_pack = False
        else:
            self.settings_label.pack(side="bottom", fill="both", expand=True)
            self.settings_label_pack = True






