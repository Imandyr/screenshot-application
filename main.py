""" Test use of application """


# global imports
import tkinter as tk

# local imports
from src.GUI import app


# function for test use
def test_run() -> None:
    settings_file_path = r"settings.json"
    application = app.ScreenshotApplication(settings_file_path)
    application.start_main_window()


# run test function
if __name__ == "__main__":
    test_run()


