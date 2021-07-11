import importlib.resources
import tkinter as tk

from PIL import ImageTk, Image
import pygame

from smashbox_viewer.event_gen import EventGenerator
from smashbox_viewer.button_locations import BUTTON_LOCATIONS
from smashbox_viewer.poller import *
import smashbox_viewer.resources.skins.default as resources


def get_resource(filename):
    """
    Wrapper around importlib's resources functionality. Returns a context
    manager that represents a filehandle.
    """
    return importlib.resources.path(resources, filename)


class Gui:
    """
    Class to display controller output based from EventGenerator.
    Takes a tkinter window on initialization and puts a frame/canvas with
    all the buttons and axis visualization.

    TODO - Once mapping is done button images need to be properly
    choosen and assigned with button locations. Buttons will probably
    need a data structure to track location, button image, pressed image.
    """

    def __init__(self, master):
        self.master = master
        self.buttons = []

        master.title("Smashbox Viewer")
        self.bt_frame = tk.Frame(master=self.master)
        self.bt_frame.pack()
        self.canvas = tk.Canvas(self.bt_frame, width=1219, height=624)
        self.canvas.pack()

        with get_resource("base-unmapped.png") as img_fh:
            self.background = ImageTk.PhotoImage(Image.open(img_fh))

        with get_resource("A-2.png") as img_fh:
            self.button = ImageTk.PhotoImage(Image.open(img_fh))

        with get_resource("A.png") as img_fh:
            self.pressed = ImageTk.PhotoImage(Image.open(img_fh))

        self.canvas.create_image(0, 0, anchor="nw", image=self.background)

        for bt in BUTTON_LOCATIONS:
            self.buttons.append(
                self.canvas.create_image(
                    BUTTON_LOCATIONS[bt][0], BUTTON_LOCATIONS[bt][1], image=self.button
                )
            )

        # Joystick / trigger drawing for debuging
        self.boxes = [
            # Joystick boxes
            self.canvas.create_rectangle(200, 300, 300, 400, outline="black"),
            self.canvas.create_rectangle(200, 400, 300, 500, outline="black"),
            # Trigger Single axis
            self.canvas.create_rectangle(350, 300, 375, 400, outline="black"),
            self.canvas.create_rectangle(350, 400, 375, 500, outline="black"),
        ]
        # Stick one center locations, and oval representaion
        self.stick1 = [
            245,
            345,
            self.canvas.create_oval(245, 345, 255, 355, fill="grey", outline="black"),
        ]
        # Stick two center locations, and oval
        self.stick2 = [
            245,
            445,
            self.canvas.create_oval(245, 445, 255, 455, fill="yellow", outline="black"),
        ]

        # Trigger center locations, and rectangle representations
        self.triggers = [
            350,
            450,
            self.canvas.create_rectangle(350, 345, 375, 355, fill="blue"),
            self.canvas.create_rectangle(350, 445, 375, 455, fill="blue"),
        ]

    """
    Takes tuple events from the Eventgenerator and changes images
    for button changes, moves joystick and trigger shapes on axis
    events.

    TODO: once mapping is handled will need to handle buttons individually
    to get proper images
    """

    def update(self, diff):
        if "Button" in diff[0]:
            key = diff[0].split("n")
            num = int(key[1]) + 1
            if diff[1] == 1:
                self.canvas.itemconfig(self.buttons[num], image=self.pressed)
            else:
                self.canvas.itemconfig(self.buttons[num], image=self.button)

        if "Axis0" in diff[0]:
            loc = self.canvas.coords(self.stick1[2])
            loc[0] = diff[1] * 50 + self.stick1[0]
            loc[2] = loc[0] + 10
            self.canvas.coords(self.stick1[2], loc)
        if "Axis1" in diff[0]:
            loc = self.canvas.coords(self.stick1[2])
            loc[1] = diff[1] * 50 + self.stick1[1]
            loc[3] = loc[1] + 10
            self.canvas.coords(self.stick1[2], loc)

        if "Axis5" in diff[0]:
            loc = self.canvas.coords(self.stick2[2])
            loc[0] = diff[1] * 50 + self.stick2[0]
            loc[2] = loc[0] + 10
            self.canvas.coords(self.stick2[2], loc)
        if "Axis2" in diff[0]:
            loc = self.canvas.coords(self.stick2[2])
            loc[1] = diff[1] * 50 + self.stick2[1]
            loc[3] = loc[1] + 10
            self.canvas.coords(self.stick2[2], loc)

        if "Axis3" in diff[0]:
            loc = self.canvas.coords(self.triggers[2])
            loc[1] = diff[1] * 50 + self.triggers[0]
            loc[3] = loc[1] + 10
            self.canvas.coords(self.triggers[2], loc)
        if "Axis4" in diff[0]:
            loc = self.canvas.coords(self.triggers[3])
            loc[1] = diff[1] * 50 + self.triggers[1]
            loc[3] = loc[1] + 10
            self.canvas.coords(self.triggers[3], loc)

        self.master.update()


# Testing program


def main():
    root = tk.Tk()
    my_gui = Gui(root)

    pygame.display.init()
    pygame.joystick.init()
    device = JoystickPoller(pygame.joystick.Joystick(0))
    device.joystick.init()

    root.update()

    for event in EventGenerator(device):
        my_gui.update(event)
        print(event)


if __name__ == "__main__":
    main()
