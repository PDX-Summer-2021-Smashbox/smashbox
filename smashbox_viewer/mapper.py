from smashbox_viewer.button_roles import BUTTON_ROLES
from smashbox_viewer.button_locations import BUTTON_NAMES
import tkinter as tk

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
 
    def gui(self, canvas, bt_frame):
        canvas = tk.Canvas(bt_frame, width=1600, height=620)
        canvas.pack()


# Testing

def main():
    test_mapper = Mapper()
    mapped_roles = test_mapper.cli()

    print(mapped_roles)

if __name__ == "__main__":
    main()