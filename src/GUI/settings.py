""" Module with various settings GUI related functions and classes """


# global imports
import re
import sys
import json
import datetime
import subprocess
import tkinter as tk
from tkinter import messagebox
# import tkinter.ttk as ttk

# local imports
from ..errors.errors import ValidationError
from ..backend.settings import Settings


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


class SettingsWindow(tk.Toplevel):
    """
    Class with settings window of application.

    """
    def __init__(self, main_window: tk.Tk, settings: Settings, *args, **kwargs) -> None:
        """
        Class with settings window of application.

        When initialized, creates toplevel window with functional for modification of application settings.

        :param main_window: Main window object.
        :param settings: Settings object.
        :param args: Args of tk.Toplevel.
        :param kwargs: Kwargs of tk.Toplevel.
        """
        super().__init__(master=main_window, *args, **kwargs)
        self.main_window = main_window
        # create objects for current and new settings
        self.settings = settings

        # grab and focus on current window
        self.grab_set()
        self.focus_force()
        # add protocol on closing of cropping window
        self.protocol("WM_DELETE_WINDOW", self.close_window)
        # add title to the window
        self.wm_title("Settings of Screenshot Application")
        # make window not resizable
        self.resizable(False, False)

        # create base frame for all widgets
        self.container = tk.Frame(self, height=400, width=400, borderwidth=3, background="#ffffff")
        self.container.pack(side="top", fill="both", expand=True)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        # # create GUI for application setting modification

        # create frame for all settings changing widgets
        self.option_container = tk.Frame(self.container, height=400, width=400, borderwidth=3)
        self.option_container.pack(side="top", fill="both", expand=True)

        # create option for set of images save directory
        self.output_label = tk.Label(self.option_container, text="Output directory: ")
        self.output_label.grid(column=0, row=0)
        self.output_entry = tk.Entry(self.option_container)
        self.output_entry.grid(column=1, row=0)
        self.output_entry.insert(0, self.settings["global_save_dir"])

        # create option for set of images file format
        self.format_label = tk.Label(self.option_container, text="Output file format: ")
        self.format_label.grid(column=0, row=1)
        self.format_entry = tk.Entry(self.option_container)
        self.format_entry.grid(column=1, row=1)
        self.format_entry.insert(0, self.settings["global_file_format"])

        # create option for set of hotkey combination for full screenshot take
        self.fs_hotkey_label = tk.Label(self.option_container, text="Full screenshot hotkey: ")
        self.fs_hotkey_label.grid(column=0, row=2)
        self.fs_hotkey_entry = tk.Entry(self.option_container)
        self.fs_hotkey_entry.grid(column=1, row=2)
        self.fs_hotkey_entry.insert(0, str(self.settings["full_screenshot_hotkey"])[1:-1])

        # create option for set of hotkey combination for cropped screenshot take
        self.cs_hotkey_label = tk.Label(self.option_container, text="Cropped screenshot hotkey: ")
        self.cs_hotkey_label.grid(column=0, row=3)
        self.cs_hotkey_entry = tk.Entry(self.option_container)
        self.cs_hotkey_entry.grid(column=1, row=3)
        self.cs_hotkey_entry.insert(0, str(self.settings["cropped_screenshot_hotkey"])[1:-1])

        # create option for enable of disable all sound from application
        self.sound_variable = tk.BooleanVar(value=self.settings["enable_sound"])
        self.sound_label = tk.Label(self.option_container, text="Enable sound: ")
        self.sound_label.grid(column=0, row=4)
        self.sound_checkbutton = tk.Checkbutton(self.option_container, variable=self.sound_variable)
        self.sound_checkbutton.grid(column=1, row=4)

        # create button for new settings applying
        self.apply_button = tk.Button(self.container, text="Apply settings",
                                      command=self.apply_new_settings, background="#f0f0f0")
        self.apply_button.pack(side="bottom", fill="both", expand=True)

    def apply_new_settings(self) -> None:
        """
        Method for validating and applying values from settings entries as settings of application.

        :return: None.
        """
        # set entries values as new settings values
        self.settings["global_save_dir"] = self.output_entry.get()
        self.settings["global_file_format"] = self.format_entry.get()
        self.settings["enable_sound"] = self.sound_variable.get()

        try:
            # try to convert string hotkey combination to list of strings
            fs_hotkey = re.sub("'", '"', self.fs_hotkey_entry.get())
            cs_hotkey = re.sub("'", '"', self.cs_hotkey_entry.get())
            self.settings["full_screenshot_hotkey"] = json.loads(f'[{fs_hotkey}]')
            self.settings["cropped_screenshot_hotkey"] = json.loads(f'[{cs_hotkey}]')

            try:
                # validate new settings values
                self.settings.validate_settings_dict()

                # write new settings to file, destroy all windows and restart application
                self.main_window.destroy()
                self.settings.write_settings_file()
                print(f"Settings has been changed ({datetime.datetime.now()})")
                subprocess.Popen(['python', sys.argv[0]])

            except ValidationError as error:
                # if validation fails, raise error message with cause
                messagebox.showerror("Validation Error", str(error))

        except json.decoder.JSONDecodeError:
            # raise error message if string is incorrect to conversion
            messagebox.showerror("Validation Error", "Incorrect syntax for hotkey combination.")

    def close_window(self) -> None:
        """
        Method for close of settings window.

        :return: None.
        """
        # release cropping window
        self.grab_release()
        # destroy cropping window
        self.destroy()






