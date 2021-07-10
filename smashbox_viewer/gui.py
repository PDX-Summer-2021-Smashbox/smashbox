from smashbox_viewer.event_gen import EventGenerator
from smashbox_viewer.button_locations import BUTTON_LOCATIONS
from smashbox_viewer.poller import *
import tkinter as tk
from PIL import ImageTk, Image
import pygame


class Gui:
    def __init__(self, master):
        self.master = master
        master.title("Smashbox Viewer")

        self.bt_frame = tk.Frame(master=self.master)
        self.bt_frame.pack()

        self.canvas = tk.Canvas(self.bt_frame, width=1219, height=624)
        self.canvas.pack()

        self.background = ImageTk.PhotoImage(
            Image.open("resources/skins/default/base-unmapped.png")
        )
        self.button = ImageTk.PhotoImage(Image.open("resources/skins/default/A-2.png"))
        self.pressed = ImageTk.PhotoImage(Image.open("resources/skins/default/A.png"))
        self.canvas.create_image(0, 0, anchor="nw", image=self.background)
        self.buttons = []
        for bt in BUTTON_LOCATIONS:
            self.buttons.append(
                self.canvas.create_image(
                    BUTTON_LOCATIONS[bt][0], BUTTON_LOCATIONS[bt][1], image=self.button
                )
            )

    def update(self, diff):
        if "Button" not in diff[0]:
            return
        key = diff[0].split("n")
        num = int(key[1])+1
        if diff[1] == 1:
            self.canvas.itemconfig(self.buttons[num],image=self.pressed)
        else:
            self.canvas.itemconfig(self.buttons[num],image=self.button)
        #self.canvas.update_idletasks()
        self.master.update()

        



if __name__ == "__main__":
    root = tk.Tk()
    my_gui = Gui(root)

    pygame.display.init()
    pygame.joystick.init()
    device = JoystickPoller(pygame.joystick.Joystick(0))
    device.joystick.init()

   
    # root.mainloop()
    root.update()

    for event in EventGenerator(device):
        my_gui.update(event)
        print(event)

    
