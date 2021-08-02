from smashbox_viewer.button_roles import BUTTON_ROLES
from smashbox_viewer.button_locations import BUTTON_LOCATIONS, BUTTON_NAMES
from tkinter.constants import BOTH, CENTER, END, LEFT, RIGHT, VERTICAL

import tkinter as tk
import json
import smashbox_viewer.gui 

from PIL import Image, ImageTk, ImageFont, ImageDraw

import smashbox_viewer.resources.skins.default as resources
class Mapper:
    """
    Class to map the buttons to their roles.
    Two options to use this class; 1) CLI
                                   2) GUI

    The cli and gui will return the mapped button dictionary
    """

    def __init__(self):
        self.mapped_buttons = {}
        self.buttons = []
        self.done = False

    def end(self):
        self.master.destroy()

    def gui(self, master, x, y):
        self.master = master
        #with smashbox_viewer.gui.get_resource("A-2.png") as img_fh:
            #self.button_img = ImageTk.PhotoImage(Image.open(img_fh))
        #smashbox_viewer.gui.get_resource()
        #self.button_img = button_img

        #self.restore_function = rst_func
        self.master.protocol("WM_DELETE_WINDOW", self.end)

        self.mp_frame = tk.Frame(master=self.master)
        self.mp_frame.pack()
        self.mp_canvas = tk.Canvas(self.mp_frame, width=1560, height=624)
        self.master.geometry(f"1560x624+{x}+{y}")
        self.mp_canvas.pack()

        #self.mp_canvas.create_image(0, 0, anchor="nw", image=background)

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

        # Restore the main gui and pass in the newly mapped buttons
        # export the mapped buttons
        self.export_mapped()
        self.done = True
        self.master.destroy()
        #self.open_new_window(self.master)
        #self.restore_function(self.mapped_buttons)

    def cli(self):
        print("INDEX    BUTTON ROLE")
        for indx, role in enumerate(BUTTON_ROLES):
            print(f"{indx}    |  {role}")

        for button in BUTTON_NAMES:
            map_index = self.verify_input(button)
            self.mapped_buttons[button] = BUTTON_ROLES[map_index]

        return self.mapped_buttons

    def verify_input(self, button):
        map_index = -1
        while not int(map_index) in range(len(BUTTON_ROLES)):
            index = input(f"Set {button} to index: ")
            map_index = index if index.isdigit() else -1

        return int(map_index)

    def map_btn(self, btn):
        self.mapped_buttons[btn] = self.list_bx.get(self.list_bx.curselection())
        print(self.mapped_buttons)

    def place_btns(self):
        for indx, btn in enumerate(BUTTON_NAMES):
            self.buttons.append(
                tk.Button(
                    master=self.master,
                    #image=self.button_img,
                    border=0,
                    highlightthickness=0,
                    bg="green",
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

        print(self.mapped_buttons)


    def open_new_window(self, root):
        master = tk.Tk()
        master.title("new window")
        master.geometry(f"1219x624+{root.winfo_x()}+{root.winfo_y()}")

        root.destroy()

        test_frame = tk.Frame(master=master)
        test_frame.pack()
        test_canvas = tk.Canvas(test_frame, width=1219, height=624)
        test_canvas.pack()
        label = tk.Label(master, text="new window")
        label.place(x=100, y=100)

    def is_done(self):
        return self.done

    def reset_done(self):
        self.done = False


# Testing


def main():
    test_mapper = Mapper()
    mapped_roles = test_mapper.cli()

    print(mapped_roles)


if __name__ == "__main__":
    main()
