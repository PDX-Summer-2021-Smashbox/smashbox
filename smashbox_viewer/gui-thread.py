import importlib.resources
from os import read
from tkinter.font import BOLD
from smashbox_viewer.button_roles import BUTTON_ROLES
from tkinter.constants import ANCHOR, BOTH, BOTTOM, CENTER, END, LEFT, NE, RIGHT, S, SE, SW, TOP, VERTICAL
from smashbox_viewer.mapper import Mapper
import tkinter as tk

from PIL import ImageTk, Image
import threading, queue, pygame, sys


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

    def __init__(self, master, queue, end):
        self.master = master
        self.queue = queue
        self.buttons = []
        self.mapper = Mapper()

        master.title("Smashbox Viewer")

        self.master.protocol("WM_DELETE_WINDOW", END)

        self.master.resizable(False, False)

        # Right click context menu
        self.menu = tk.Menu(master=self.master, tearoff=False)
        self.menu.add_command(label="mapper gui", command=self.gui_map)
        self.menu.add_command(label="mapper cli", command=self.cli_map)
        master.bind("<Button-3>", self.show_menu)

        self.bt_frame = tk.Frame(master=self.master)
        self.bt_frame.pack(side=LEFT)
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
        '''
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
        ]'''


    def processEvent(self):
        while self.queue.qsize():
            event = self.queue.get(0)
            self.update(event)

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

        self.canvas.update_idletasks()
        self.canvas.update()

    # Right click context menu
    def show_menu(self, event):
        try:
            self.menu.post(event.x_root, event.y_root)
        finally:
            self.menu.grab_release()

    def gui_map(self):
        '''
        Hides the current canvas, frame, and disables the context menu,
        then calls the mapper gui. 
        '''
        # Disable context menu while in mapper
        self.master.unbind("<Button-3>")

        # Grab the base image for the mapper gui background
        with get_resource("base.png") as base_img:
            self.base = ImageTk.PhotoImage(Image.open(base_img))

        self.canvas.forget()
        self.bt_frame.forget()

        self.map_gui = self.mapper.gui
        self.map_gui(self.master, self.base, 
                    self.button, self.restore_gui)


    def cli_map(self):
        self.mapped_roles = self.mapper.cli() 
        print(self.mapped_roles)


    # Restore the canvas, frame, and context menu
    def restore_gui(self, mapped_btns):
        self.bt_frame.pack()
        self.canvas.pack()

        self.master.bind("<Button-3>", self.show_menu)
        self.mapped_roles = mapped_btns
        print(self.mapped_roles)


class ThreadClient:
    def __init__(self, master, device):
        self.master = master
        self.device = device
        self.queue = queue.Queue()
        self.gui = Gui(master, self.queue, self.end)
        self.gui.canvas.update()
        self.running = 1
        self.t1 = threading.Thread(target=self.runVis).start()

        self.eventCall()

    def eventCall(self):
        self.gui.processEvent()
        if not self.running:
            self.master.destroy()
            sys.exit()
        self.master.after(0, self.eventCall)

    def runVis(self):
        for event in EventGenerator(self.device):
            if not self.running:
                sys.exit()
            self.queue.put(event)
            print(event)

    def end(self):
        self.running = 0


# Testing program


def main():
    pygame.display.init()
    pygame.joystick.init()
    device = JoystickPoller(pygame.joystick.Joystick(0))
    device.joystick.init()

    root = tk.Tk()
    gui = ThreadClient(root, device)
    root.mainloop()


if __name__ == "__main__":
    main()
