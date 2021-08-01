from smashbox_viewer.button_roles import BUTTON_ROLES
from smashbox_viewer.button_locations import BUTTON_LOCATIONS, BUTTON_NAMES
from tkinter.constants import ANCHOR, BOTH, BOTTOM, CENTER, END, LEFT, NE, RIGHT, S, SE, SW, TOP, VERTICAL

import tkinter as tk

from PIL import Image, ImageFont, ImageDraw

class Mapper:
    '''
    Class to map the buttons to their roles.
    Two options to use this class; 1) CLI
                                   2) GUI

    The cli will return the mapped button dictionary

    TODO
        Clean up code a bit  
        GUI client                             
    '''
    def __init__(self):
        self.mapped_buttons = {}
        self.buttons = []
        
    def verify_input(self, button):
        map_index = -1
        while not int(map_index) in range(len(BUTTON_ROLES)):
            index = input(f"Set {button} to index: ")
            map_index = index if index.isdigit() else -1

        return int(map_index)
 
    def cli(self):
        print("INDEX    BUTTON ROLE")
        for indx, role in enumerate(BUTTON_ROLES):
            print(f"{indx}    |  {role}")
        
        for button in BUTTON_NAMES:
            map_index = self.verify_input(button)
            self.mapped_buttons[button] = BUTTON_ROLES[map_index]
        
        return self.mapped_buttons

    def gui(self, master, background, button_img):
        self.master = master
        self.button_img = button_img
        self.mp_frame = tk.Frame(master=self.master)
        self.mp_frame.pack()
        self.mp_canvas = tk.Canvas(self.mp_frame, width=1219, height=624)
        self.mp_canvas.pack()

        self.mp_canvas.create_image(0,0, anchor="nw", image=background)
        self.place_btns()


        #self.bt_frame.pack_forget()
        self.mp_canvas.configure(width=1560, height=624)

        # place the buttons
        #self.place_btns()

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
        self.save_btn = tk.Button(master=self.master,
                                    text="Set", width=16,
                                    height=1)
        self.cancel_btn = tk.Button(master=self.master,
                                    text="Cancel", width=16,
                                    height=1, command=self.close_gui)
        self.import_btn = tk.Button(master=self.master, 
                                    text="Import", width=41,
                                    height=1)
        self.export_btn = tk.Button(master=self.master,
                                    text="Export", width=41,
                                    height=1)

        self.save_btn.place(x=1243, y=501)
        self.cancel_btn.place(x=1416, y=501)
        self.import_btn.place(x=1243, y=552)
        self.export_btn.place(x=1243, y=586)
        

    def close_gui(self):
        self.map_frame.destroy()
        self.list_bx.destroy()
        self.sb.destroy()
        self.save_btn.destroy()
        self.cancel_btn.destroy()
        self.import_btn.destroy()
        self.export_btn.destroy()
        self.mp_canvas.destroy()

    def map_btn(self, btn):
        self.mapped_buttons[btn] = self.list_bx.get(self.list_bx.curselection())
        print(self.mapped_buttons)


    def place_btns(self):
        for indx, btn in enumerate(BUTTON_NAMES):
            self.buttons.append(tk.Button(self.master, image=self.button_img,
                                border=0, highlightthickness=0,bg="white", bd=0, 
                                command=lambda b=btn: self.map_btn(b))
                            )

            self.buttons[indx].place(x=BUTTON_LOCATIONS[btn][0], y=BUTTON_LOCATIONS[btn][1])




# Testing

def main():
    test_mapper = Mapper()
    mapped_roles = test_mapper.cli()

    print(mapped_roles)

if __name__ == "__main__":
    main()
