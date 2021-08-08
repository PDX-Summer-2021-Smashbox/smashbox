import importlib.resources

import tkinter as tk


from PIL import ImageTk, Image
import threading, queue, pygame

from smashbox_viewer.mapper import Mapper
from smashbox_viewer.calibrator import Calibrator
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

    def __init__(self, master, queue, device, end):
        self.master = master
        self.queue = queue
        self.device = device
        self.buttons = []

        self.mapper = Mapper()
        self.mapped_btns = []

        self.calibrator = Calibrator()
        self.calibrate = False
        self.cal_event = threading.Event()

        master.title("Smashbox Viewer")

        self.master.protocol("WM_DELETE_WINDOW", end)
        self.master.resizable(False, False)

        """
        self.menu_frame = tk.Frame(master=self.master)
        self.menu_frame.pack()

        self.menu = tk.StringVar(self.menu_frame)
        self.menu.set("Select")
        self.select = tk.OptionMenu(self.menu_frame, self.menu, "one", "two")
        self.select.pack()
        """

        self.bt_frame = tk.Frame(master=self.master)
        self.bt_frame.pack()
        self.canvas = tk.Canvas(self.bt_frame, width=1219, height=624)
        self.canvas.pack()

        # Right click context menu
        self.menu = tk.Menu(master=self.master, tearoff=False)
        self.menu.add_command(label="Mapper GUI", command=lambda: self.queue.put("map"))
        self.menu.add_command(label="Mapper CLI", command=self.cli_map)
        self.menu.add_command(label="Calibrator", command=lambda: self.queue.put("cal"))
        self.master.bind("<Button-3>", self.show_menu)

        with get_resource("base-unmapped.png") as img_fh:
            self.background = ImageTk.PhotoImage(Image.open(img_fh))

        with get_resource("base.png") as img_fh:
            self.base = ImageTk.PhotoImage(Image.open(img_fh))

        with get_resource("Button_A.png") as img_fh:
            self.button = ImageTk.PhotoImage(Image.open(img_fh))

        with get_resource("Button_A_Pressed.png") as img_fh:
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

    def cli_map(self):
        self.mapped_btns = self.mapper.cli()

    def open_map(self):
        # Hide visualizer
        self.master.withdraw()

        root = tk.Toplevel()
        self.mapper.gui(root, self.base, self.button)
        while True:
            root.update_idletasks()
            root.update()
            if self.mapper.done:
                self.mapper.reset_done()
                break

        # Bring back visualizer
        self.master.deiconify()

    def open_cal(self):
        self.calibrate = True
        self.master.unbind("<Button-3>")
        thread = threading.Thread(
            target=self.calibrator.gui,
            args=(self.canvas, self.mapped_btns, self.cal_event),
        )
        thread.daemon = True
        thread.start()
        self.master.update_idletasks()
        self.master.update()

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

        # Open up mapping gui
        if "map" in diff:
            self.open_map()

        # Run calibration over gui
        if "cal" in diff:
            self.open_cal()

        # Close calibration TODO - set by role not button number
        if self.calibrate and ("Button9", 1) == diff:
            self.calibrator.close_gui()
            self.master.bind("<Button-3>", self.show_menu)

        # Send frame to calibration when 'A' button is pressed
        if self.calibrate and ("Button1", 1) == diff:
            self.calibrator.put_frame(self.device.poll())
            self.cal_event.set()

        # Redo to calibration when 'B' button is pressed
        if self.calibrate and ("Button2", 1) == diff:
            self.calibrator.redo()
            self.cal_event.set()

        # TODO - When mapping structure is done this should change image by role
        if "Button" in diff[0]:
            key = diff[0].split("n")
            num = int(key[1]) + 1
            if diff[1] == 1:
                self.canvas.itemconfig(self.buttons[num], image=self.pressed)
            else:
                self.canvas.itemconfig(self.buttons[num], image=self.button)

        # TODO - Once tranlastion is finished REMOVE all Axis monitoring
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


class ThreadClient:
    def __init__(self, master, device):
        self.master = master
        self.device = device
        self.queue = queue.Queue()
        self.gui = Gui(master, self.queue, self.device, self.end)
        self.gui.canvas.update()
        self.running = 1
        self.t1 = threading.Thread(target=self.runVis)
        self.t1.daemon = True
        self.t1.start()

        self.eventCall()

    def eventCall(self):
        self.gui.processEvent()
        if not self.running:
            self.master.destroy()
        self.master.after(0, self.eventCall)

    def runVis(self):
        for event in EventGenerator(self.device):
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
