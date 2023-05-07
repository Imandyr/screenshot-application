""" All screenshot creation related widgets """


# global imports
from typing import Tuple
from abc import abstractmethod
from PIL import Image, ImageTk
import numpy as np
import tkinter as tk
# import tkinter.ttk as ttk
import datetime
import os
import re

# import  mixer and hide pygame support prompt
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
from pygame import mixer

# local imports
from ..backend import screenshot_creation
from ..backend.settings import Settings


class ScreenshotWidget(tk.Frame):
    """
    Base class of all screenshot widgets.
    Used for creation of screenshot widget for communication between backed Screenshot object and GUI.

    attributes:
        settings: Dictionary with all application settings.
        backend: Object of Screenshot class using for making screenshots.

    methods:
        create_screenshot: Method for screenshot creation by using Screenshot object.

    """

    settings: Settings
    backend: screenshot_creation.Screenshot

    @abstractmethod
    def __init__(self, parent: tk.Frame, settings: Settings, *args, **kwargs) -> None:
        """ Initialization of object """
        super().__init__(parent, *args, **kwargs)

        # check if "use_global_save_dir" and "use_global_file_format" is true
        self.settings = settings
        if not self.settings["use_global_save_dir"] and not self.settings["use_global_file_format"]:
            raise ValueError(f"Class {self.__class__.__name__} can only be used with settings:"
                             f" 'use_global_save_dir' == True and 'use_global_file_format' == True.")

        # initialize sound mixer
        self.mixer = mixer
        self.mixer.init()
        try:
            self.sound = self.mixer.Sound("./src/assets/sign.wav")
        except Exception:
            raise FileNotFoundError("'sign.wav' file should be in the './src/assets' directory.")

    @abstractmethod
    def create_screenshot(self, *args, **kwargs) -> None:
        """ Method for screenshot creation by using Screenshot object. """


class FullScreenshotWidget(ScreenshotWidget):
    """
    Widget for full monitor screenshot creation.

    """

    def __init__(self, parent: tk.Frame, settings: Settings, *args, **kwargs) -> None:
        """
        Widget for full monitor screenshot creation.

        When initialized, creates all necessary widgets inside screenshot widget frame and backend object for
        screenshot creation.

        :param parent: Parent widget for this frame.
        :param settings: Dictionary with all application settings.
        :param args: args
        :param kwargs: kwargs
        """
        super().__init__(parent, settings, *args, **kwargs)

        # initialize settings and backend screenshot creation object
        self.backend = screenshot_creation.MonitorScreenshot(
            save_dir=self.settings["global_save_dir"],
            file_format=self.settings["global_file_format"])

        # create widget label
        hotkey = re.sub(', ', '+', str(self.settings['full_screenshot_hotkey']))[1:-1]
        widget_label = tk.Label(self, background="#ffffff", text=f"Full screenshot (hotkey: {hotkey}): ")
        widget_label.pack(side="left", fill="both", expand=True)

        # create button for test screenshot creation
        test_screenshot_button = tk.Button(self, text="Create screenshot", command=self.create_screenshot)
        test_screenshot_button.pack(side="right", fill="both", expand=False)

    def create_screenshot(self, *args, **kwargs) -> None:
        """
        Method for screenshot creation by using inner backend Screenshot object.

        :param args: args
        :param kwargs: kwargs
        :return: None
        """

        # take screenshot image
        self.backend.take_screenshot(*args, **kwargs)
        # edit screenshot image
        self.backend.edit_screenshot(*args, **kwargs)
        # save screenshot image to file
        self.backend.save_screenshot(*args, **kwargs)
        # delete no more necessary image
        self.backend.image = None

        print(f"Full screenshot was taken ({datetime.datetime.now()})")

        # play sound as sign of success if enabled
        if self.settings["enable_sound"]:
            self.sound.play()


class CroppedScreenshotWidget(ScreenshotWidget):
    """
    Widget for creation of cropped screenshot.

    """

    def __init__(self, parent: tk.Frame, main_window: tk.Tk, settings: Settings, *args, **kwargs) -> None:
        """
        Widget for creation of cropped screenshot.

        When initialized, creates all necessary widgets inside screenshot widget frame and backend object for
        screenshot creation.

        :param parent: Parent widget for this frame.
        :param main_window: Main window object of application.
        :param settings: Dictionary with all application settings.
        :param args: args
        :param kwargs: kwargs
        """
        super().__init__(parent, settings, *args, **kwargs)

        # add main window object
        self.main_window = main_window

        # initialize settings and backend screenshot creation object
        self.backend = screenshot_creation.CroppedMonitorScreenshot(
            save_dir=self.settings["global_save_dir"],
            file_format=self.settings["global_file_format"])

        # create widget label
        hotkey = re.sub(', ', '+', str(self.settings['cropped_screenshot_hotkey']))[1:-1]
        widget_label = tk.Label(self, background="#ffffff", text=f"Cropped screenshot (hotkey: {hotkey}): ")
        widget_label.pack(side="left", fill="both", expand=True)

        # create button for test screenshot creation
        test_screenshot_button = tk.Button(self, text="Create screenshot", command=self.create_screenshot)
        test_screenshot_button.pack(side="right", fill="both", expand=False)

    def create_screenshot(self, *args, **kwargs) -> None:
        """
        Method for screenshot creation by using inner backend Screenshot object and CroppingWindow object for
        marking coordinates for screenshot cropping.

        :param args: args
        :param kwargs: kwargs
        :return: None
        """
        # create screenshot only if main window is currently not have any toplevel windows
        if not any(isinstance(widget[1], tk.Toplevel) for widget in self.main_window.children.items()):

            # take screenshot image
            self.backend.take_screenshot(*args, **kwargs)

            # create cropping window and run marking of cropping coordinates on image
            cropping_window = CroppingWindow(self.main_window, takefocus=True)
            box = cropping_window.mark_cropping_box(self.backend.image)

            # edit screenshot image
            self.backend.edit_screenshot(box=box, *args, **kwargs)
            # save screenshot image to file
            self.backend.save_screenshot(*args, **kwargs)
            # delete no more necessary image
            self.backend.image = None

            print(f"Cropped screenshot was taken ({datetime.datetime.now()})")

            # play sound as sign of success if enabled
            if self.settings["enable_sound"]:
                self.sound.play()


class CroppingWindow(tk.Toplevel):
    """
    Window for marking a box of coordinates on image using GUI, by which it can be cropped in a future.

    """

    def __init__(self, parent: tk.Tk, *args, **kwargs) -> None:
        """
        Window for marking a box of coordinates on image using GUI, by which it can be cropped in a future.

        When initialized, create window with base for image cropping box marking.

        :param parent: Parent window of application.
        :param args: args
        :param kwargs: kwargs
        """
        super().__init__(master=parent, *args, **kwargs)

        # create instance parent variable
        self.parent = parent
        # create blank cropping box with tkinter int variables
        self.cropping_box = [tk.IntVar(), tk.IntVar(), tk.IntVar(), tk.IntVar()]
        # create objects of canvas, rectangle and its coordinates variables for denoting a cropping box on image
        self.canvas, self.rect, self.rect_start_x, self.rect_start_y, self.rect_end_x, self.rect_end_y = \
            None, None, None, None, None, None

        # grab current window
        self.grab_set()
        # make main window invisible
        self.parent.withdraw()
        # focus on current window
        self.focus_force()
        # add protocol on closing of cropping window
        self.protocol("WM_DELETE_WINDOW", self.close_window)
        # add title to the window
        self.wm_title("Screenshot Cropping")
        # open in full-screen
        self.attributes('-fullscreen', True)
        # make window not resizable
        self.resizable(False, False)

        # create frame and assigning it as container for all main window content
        self.container = tk.Frame(self, height=300, width=600)
        # specifying the region where the frame is packed in window
        self.container.pack(side="top", fill="both", expand=True)
        # configuring the location of the container using grid
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

    def mark_cropping_box(self, image: np.ndarray) -> Tuple[int, int, int, int]:
        """
        Method what draw image and give user an interface for marking a box of pixel coordinates
        by which it can be cropped later.

        The use of interface is simple, just press left mouse button where you want to be a first corner of
        cropped image and release it on second corner. after press and release of mouse button, cropping window
        will be closed and obtained coordinates box will be returned from method.

        :param image: Object with image what should be cropped.
        :return: Box of pixel coordinates by which image can be cropped later.
        """

        # draw image inside canvas
        image = ImageTk.PhotoImage(image=Image.fromarray(np.uint8(image)))
        self.canvas = tk.Canvas(self.container, width=image.width(), height=image.height(), highlightthickness=0)
        self.canvas.pack(side="top", fill="both", expand=True)
        self.canvas.create_image(0, 0, image=image, anchor=tk.NW)

        # set cursor position on press and release as box coordinates, and draw rectangle while mouse move between them
        self.canvas.bind("<ButtonPress-1>", self._on_mouse_press)
        self.canvas.bind("<B1-Motion>", self._on_mouse_move)
        self.canvas.bind("<ButtonRelease-1>", self._on_mouse_release)

        # wait until mouse will be released and self.cropping_box[3] IntVar will be modified
        self.canvas.wait_variable(self.cropping_box[3])

        # reverse box corners if they have been taken in reverse sequence
        if self.cropping_box[0].get() > self.cropping_box[2].get():
            temp = self.cropping_box[0]
            self.cropping_box[0] = self.cropping_box[2]
            self.cropping_box[2] = temp
        if self.cropping_box[1].get() > self.cropping_box[3].get():
            temp = self.cropping_box[1]
            self.cropping_box[1] = self.cropping_box[3]
            self.cropping_box[3] = temp

        # if box values is somehow equal, add 1 pixel to 3 and 4 coordinates
        if self.cropping_box[0].get() == self.cropping_box[2].get():
            self.cropping_box[2].set(self.cropping_box[2].get() + 1)
        if self.cropping_box[1].get() == self.cropping_box[3].get():
            self.cropping_box[3].set(self.cropping_box[3].get() + 1)

        # close window
        self.close_window()

        # return box of cropping coordinates
        return self.cropping_box[0].get(), self.cropping_box[1].get(), self.cropping_box[2].get(), \
            self.cropping_box[3].get()

    def _on_mouse_press(self, event) -> None:
        """
        Method for taking coordinates of mouse and set it as first corner of box, and also creates a rectangle.
        Should be used on mouse press.
        """
        # add coordinates of first cropping corner
        self.cropping_box[0].set(self.winfo_pointerx()), self.cropping_box[1].set(self.winfo_pointery())
        # create rectangle
        self.rect = self.canvas.create_rectangle(self.cropping_box[0].get(), self.cropping_box[1].get(),
                                                 self.cropping_box[0].get()+1, self.cropping_box[1].get()+1,
                                                 width=1, outline='red')

    def _on_mouse_move(self, event) -> None:
        """
        Method for drawing and updating of rectangle on mouse move.
        Should be used on mouse move.
        """
        # update coordinates of rectangle based on cursor movement
        self.canvas.coords(self.rect, self.cropping_box[0].get(), self.cropping_box[1].get(),
                           self.winfo_pointerx(), self.winfo_pointery())

    def _on_mouse_release(self, event) -> None:
        """
        Method for taking coordinates of mouse and set it as second corner of box.
        Should be used on mouse release.
        """
        self.cropping_box[2].set(self.winfo_pointerx()), self.cropping_box[3].set(self.winfo_pointery())

    def close_window(self) -> None:
        """
        Method for close of cropping window.
        """
        # release cropping window
        self.grab_release()
        # minimize parent window
        self.parent.state('iconic')
        # destroy cropping window
        self.destroy()

