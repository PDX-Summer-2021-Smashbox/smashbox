
import importlib.resources

from PIL import ImageTk, Image
import smashbox_viewer.resources.skins.default as resources
from smashbox_viewer.button_roles import BUTTON_ROLES
from smashbox_viewer.button_locations import BUTTON_LOCATIONS, BUTTON_NAMES
from tkinter.constants import BOTH, CENTER, END, LEFT, RIGHT, VERTICAL

import tkinter as tk
from tkinter import filedialog as fd
#from smashbox_viewer.gui import get_resource 
import json




def get_resource(filename):
    """
    Wrapper around importlib's resources functionality. Returns a context
    manager that represents a filehandle.
    """
    return importlib.resources.path(resources, filename)

class Mapper:
    """
    Class to map the buttons to their roles.
    Two options to use this class; 1) CLI
                                   2) GUI

    The cli will return the mapped button dictionary, then export it to mapped.json
    The gui will save and export the mapped buttons
    TODO:
        File dialouge for saving, importing, exporting
    """

    def __init__(self):
        self.mapped_buttons = {}
        self.buttons = []
        self.done = False
        self.button_imgs = {}

        # import the button skin images
        self.import_btn_imgs()


    def gui(self, master, background):
        self.master = master

        self.mp_frame = tk.Frame(master=self.master)
        self.mp_frame.pack()
        self.mp_canvas = tk.Canvas(self.mp_frame, width=1560, height=624)
        self.mp_canvas.pack()

        self.mp_canvas.create_image(0, 0, anchor="nw", image=background)
        self.master.resizable(False, False)

        # place the buttons
        self.place_btns()

        self.map_frame = tk.Frame(master=self.master)
        self.map_frame.place(x=1224, y=1)

        self.list_bx = tk.Listbox(master=self.map_frame, width=53, height=30)
        self.list_bx.pack(side=LEFT)

        self.sb = tk.Scrollbar(master=self.map_frame, orient=VERTICAL)
        self.sb.pack(side=RIGHT, fill=BOTH)

        self.list_bx.configure(yscrollcommand=self.sb.set, justify=CENTER)
        self.sb.config(command=self.list_bx.yview)

        for btn in BUTTON_ROLES:
            self.list_bx.insert(END, btn)

        # Add the mapping buttons
        self.save_exit_btn = tk.Button(
            master=self.master,
            text="Save / Exit",
            width=41,
            height=1,
            command=self.close_gui,
        )
        self.import_btn = tk.Button(
            master=self.master,
            text="Import",
            width=41,
            height=1,
            command=self.import_mapped,
        )
        self.export_btn = tk.Button(
            master=self.master,
            text="Export",
            width=41,
            height=1,
            command=self.export_mapped,
        )

        self.save_exit_btn.place(x=1243, y=501)
        self.import_btn.place(x=1243, y=552)
        self.export_btn.place(x=1243, y=586)
        
        # import the current button mapping
        self.import_mapped()


    # Destroy all the mapper controls
    def close_gui(self):
        self.map_frame.destroy()
        self.mp_frame.destroy()
        self.list_bx.destroy()
        self.sb.destroy()
        self.save_exit_btn.destroy()
        self.import_btn.destroy()
        self.export_btn.destroy()
        self.mp_canvas.destroy()

        # Destroy the buttons
        for btn in self.buttons:
            btn.destroy()
        self.buttons.clear()

        # export the mapped buttons and destroy the mapper
        self.export_mapped()
        self.done = True
        self.master.destroy()

    def cli(self):
        print("INDEX    BUTTON ROLE")
        for indx, role in enumerate(BUTTON_ROLES):
            print(f"{indx}    |  {role}")

        for button in BUTTON_NAMES:
            map_index = self.verify_input(button)
            self.mapped_buttons[button] = BUTTON_ROLES[map_index]

        self.export_mapped()
        return self.mapped_buttons

    def verify_input(self, button):
        map_index = -1
        while not int(map_index) in range(len(BUTTON_ROLES)):
            index = input(f"Set {button} to index: ")
            map_index = index if index.isdigit() else -1

        return int(map_index)

    # Gets the item selected from listbox and maps to the clicked btn
    def map_btn(self, btn):
        selected_btn = self.list_bx.get(self.list_bx.curselection())
        self.mapped_buttons[btn] = selected_btn
        index = BUTTON_NAMES.index(btn)
        self.buttons[index].configure(image=self.button_imgs[selected_btn])
        print(self.mapped_buttons)


    # Loads A_Button as default image
    def place_btns(self):
        for indx, btn in enumerate(BUTTON_NAMES):
            self.buttons.append(
                tk.Button(
                    master=self.master,
                    image=self.button_imgs["Button_A"],
                    border=0,
                    highlightthickness=0,
                    bg="white",
                    bd=0,
                    command=lambda b=btn: self.map_btn(b),
                )
            )

            self.buttons[indx].place(
                x=BUTTON_LOCATIONS[btn][0], y=BUTTON_LOCATIONS[btn][1] - 20
            )

    def export_mapped(self):
        with open("mapped.json", "w") as export_file:
            export_file.write(json.dumps(self.mapped_buttons, indent=4))

    def import_mapped(self):
        with open("mapped.json", "r") as import_file:
            self.mapped_buttons = json.load(import_file)

        # Retrieves the button index and sets button the image accordingly
        for k, v in self.mapped_buttons.items():
            btn_indx = self.get_btn_number(k)
            self.buttons[btn_indx].configure(image=self.button_imgs[v])

        print(self.mapped_buttons)

    def import_btn_imgs(self):
        self.button_imgs = {}
        for btn in BUTTON_ROLES:
            with get_resource(f"{btn}.png") as img_fh:
                self.button_imgs[btn] = ImageTk.PhotoImage(Image.open(img_fh))

    # Used for thread control
    def is_done(self):
        return self.done

    def reset_done(self):
        self.done = False

    # Returns the digit at the end of the button name.
    # Used for retrieving the button at b# index
    def get_btn_number(self, key):
        text = key.split("_")
        return int(text[1]) - 1


# Testing


def main():
    test_mapper = Mapper()
    mapped_roles = test_mapper.cli()

    print(mapped_roles)


if __name__ == "__main__":
    main()
