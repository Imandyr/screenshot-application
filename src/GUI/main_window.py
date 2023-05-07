""" Module with main window. """


# global imports
import os
import subprocess
import tkinter as tk
# import tkinter.ttk as ttk

# local imports
from .settings import SettingsWindow
from .widgets import WidgetScrollbar
from .screenshot_widgets import FullScreenshotWidget, CroppedScreenshotWidget
from ..backend.settings import Settings
from ..errors.errors import InvalidFilePathError


class MainWindow(tk.Tk):
    """
    A main window of application where all objects from the main window be stored.

    """

    def __init__(self, settings: Settings, *args, **kwargs) -> None:
        """
        A main window of application where all objects from the main window be stored.

        When initialized, setup window parameters and create frame for MainPage object.

        :param settings: Object with settings of application.
        """
        super().__init__(*args, **kwargs)

        # add icon to the main window
        try:
            self.iconphoto(True, tk.PhotoImage(file="./src/assets/icon.png"))
        except Exception:
            raise InvalidFilePathError("'icon.png' file should be in the './src/assets' directory.")

        # add title to the window
        self.wm_title("Screenshot Application")
        # make window not resizable
        self.resizable(False, False)

        # create frame and assigning it to container for all main window content
        self.container = tk.Frame(self, height=700, width=600, borderwidth=3, background="#ffffff")
        # specifying the region where the frame is packed in window
        self.container.pack(side="top", fill="both", expand=True)

        # configuring the location of the container using grid
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        # create MainPage frame object with all widgets and add it to container frame
        self.main_page = MainPage(self.container, self, settings)
        self.main_page.grid(row=0, column=0, sticky="nsew")


class MainPage(tk.Frame):
    """
    A class containing all widgets from the main window.

    """

    def __init__(self, parent: tk.Frame, main_window: MainWindow, settings: Settings, *args, **kwargs) -> None:
        """
        A class containing all widgets from the main window.

        When initialized, creates all widgets for main page.

        :param parent: Parent widget for this frame.
        :param main_window: Main window object of application.
        :param settings: Instance of settings object.
        :param args: args
        :param kwargs: kwargs
        """
        super().__init__(parent, *args, **kwargs)
        self.main_window = main_window
        self.settings = settings

        # create frame for screenshot widgets
        self.screenshot_frame = tk.Frame(self, borderwidth=3)
        self.screenshot_frame.pack(side="top", fill="both", expand=True)

        # create frame for buttons
        self.button_frame = tk.Frame(self)
        self.button_frame.pack(side="bottom", fill="both", expand=True)

        # create button for opening of settings window
        self.settings_button = tk.Button(self.button_frame, text="settings", command=self.open_settings_window)
        self.settings_button.pack(side="left", fill="both", expand=True)

        # create button for opening of directory with saved screenshots
        self.save_directory_button = tk.Button(self.button_frame, text="open save directory",
                                               command=self.open_save_directory)
        self.save_directory_button.pack(side="right", fill="both", expand=True)

        # # create all ScreenshotWidget objects, based on frame contained inside screenshot_scrollbar

        # add widget of full screenshot creation
        self.full_screenshot = FullScreenshotWidget(self.screenshot_frame, settings)
        self.full_screenshot.pack(side="top", anchor="nw", fill="both", expand=True)

        # add widget for cropped screenshot creation
        self.cropped_screenshot = CroppedScreenshotWidget(self.screenshot_frame, main_window,
                                                          settings)
        self.cropped_screenshot.pack(side="top", anchor="nw", fill="both", expand=True)

    def open_settings_window(self, *args, **kwargs) -> None:
        """
        Method for opening of settings menu.

        :param args: Args for SettingsWindow.
        :param kwargs: Kwargs for SettingsWindow.
        :return: None.
        """
        SettingsWindow(self.main_window, self.settings, *args, **kwargs)

    def open_save_directory(self, *args, **kwargs) -> None:
        """
        Method for opening directory with all saved screenshots in user file explorer.

        :param args: Args for subprocess.Popen.
        :param kwargs: Kwargs for subprocess.Popen.
        :return: None.
        """
        path_to_save_directory = os.path.abspath(self.settings["global_save_dir"])
        subprocess.Popen(fr'explorer "{path_to_save_directory}"', *args, **kwargs)





