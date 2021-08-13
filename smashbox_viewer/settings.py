from tkinter.constants import TOP, BOTTOM, CENTER, END, LEFT, RIGHT, VERTICAL

import tkinter as tk
from tkinter import filedialog as fd
import json


class Settings:

    def __init__(self):
        self.done = False


    def open_settings(self, master):
        self.master = master
        self.master.title("Settings")
        self.set_frame = tk.Frame(master=self.master)
        self.set_frame.pack()
        self.canvas = tk.Canvas(self.set_frame, width=500, height=500)
        self.canvas.pack()

        # Add listbox and two buttons
        self.list_bx = tk.Listbox(master=self.set_frame, width=30, height=15)
        self.list_bx.pack(side=TOP)
        self.add_btn = tk.Button(
            master=self.master,
            text="Add",
            width=15,
            height=1,
            command=self.add_path(),
        )
        self.add_btn.pack(side=BOTTOM)


    def close_settings(self):
        self.list_bx.destroy()
        self.add_btn.destroy()
        self.set_frame.destroy()
        self.canvas.destroy()

        self.done = True

    def is_done(self):
        return self.done
    
    def reset_done(self):
        self.done = False
