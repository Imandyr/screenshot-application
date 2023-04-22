""" Various custom widgets """


# global imports
import tkinter as tk
import tkinter.ttk as ttk
from typing import Any

# local imports


class WidgetScrollbar(tk.Frame):
    """
    A class containing frame with scrollbar for listing of various widgets.

    """

    def __init__(self, parent: tk.Frame, *args, **kwargs) -> None:
        """
        A class containing frame with scrollbar for listing of various widgets.

        When initialized, creating an object with frame in which every added widget will be listed by scrollbar.

        example of scrollbar population:
            >>>> for row in range(100):\
                    tk.Label(self.frame, text="row number: %s" % row).grid(row=row, column=0)

        :param parent: Parent widget for this frame.
        :param args: args
        :param kwargs: kwargs
        """
        super().__init__(parent, *args, **kwargs)

        # create frame for screenshot widgets contained inside canvas added to Scrollbar

        self.canvas = tk.Canvas(self, borderwidth=0, background="#ffffff")
        self.frame = tk.Frame(self.canvas, background="#ffffff")
        self.vsb = tk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.vsb.set)

        self.vsb.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)
        self.canvas.create_window((4, 4), window=self.frame, anchor="nw", tags="self.frame")

        self.frame.bind("<Configure>", self.on_frame_configure)

    def on_frame_configure(self, event: Any) -> None:
        """ Reset the scroll region to encompass the inner frame. """
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))





