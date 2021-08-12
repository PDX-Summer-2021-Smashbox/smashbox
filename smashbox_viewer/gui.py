import importlib.resources
import tkinter as tk

from PIL import ImageTk, Image
import threading, queue, pygame, json

from smashbox_viewer.mapper import Mapper
from smashbox_viewer.calibrator import Calibrator
from smashbox_viewer.button_map import ButtonMapper
from smashbox_viewer.event_gen import EventGenerator
from smashbox_viewer.button_locations import BUTTON_LOCATIONS
from smashbox_viewer.poller import *
import smashbox_viewer.resources.skins.default as resources


"""
TODO
SKIN SELECTION 

from smashbox_viewer.resources.skins import *

skins_dict = {
    "default" : resources,
    "other" : other_package_name,
    #...
}

get_resources(skins_dict["default"], filename)
"""


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
        self.btn_images = []
        self.btn_map = {}
        self.new_map = True

        self.mapper = Mapper()
        with open("mapped.json") as file:
            self.mapped_btns = json.load(file)

        self.btnmapper = ButtonMapper()
        self.btnmapping = [False]
        self.calibrator = Calibrator()
        self.calibrate = False
        self.cal_event = threading.Event()

        master.title("Smashbox Viewer")

        self.master.protocol("WM_DELETE_WINDOW", end)
        self.master.resizable(False, False)

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

        for btn in self.mapped_btns.values():
            imgs = []
            if btn == "Button_Disabled":
                with get_resource(f"Transparent.png") as img_fh:
                    imgs.append(ImageTk.PhotoImage(Image.open(img_fh)))

                with get_resource(f"Transparent.png") as img_fh:
                    imgs.append(ImageTk.PhotoImage(Image.open(img_fh)))

            else:
                with get_resource(f"{btn}.png") as img_fh:
                    imgs.append(ImageTk.PhotoImage(Image.open(img_fh)))

                with get_resource(f"{btn}_Pressed.png") as img_fh:
                    imgs.append(ImageTk.PhotoImage(Image.open(img_fh)))

            self.btn_images.append(imgs)

        self.canvas.create_image(0, 0, anchor="nw", image=self.background)

        for btn, img in zip(BUTTON_LOCATIONS, self.btn_images):
            self.buttons.append(
                self.canvas.create_image(
                    BUTTON_LOCATIONS[btn][0], BUTTON_LOCATIONS[btn][1], image=img[0]
                )
            )

        if self.new_map == True:
            self.canvas.create_text(
                (1219 / 2),
                20,
                fill="red",
                font="Arial 20 bold",
                text="No buttons bound, Press Button_Start",
                anchor="center",
                tag="prompt",
            )
            self.open_btn()

    def cli_map(self):
        self.mapped_btns = self.mapper.cli()

    def open_map(self):
        # Hide visualizer
        self.master.withdraw()

        root = tk.Toplevel()
        self.mapper.gui(root, self.base)
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
        calthread = threading.Thread(
            target=self.calibrator.gui,
            args=(self.master, self.canvas, self.mapped_btns, self.cal_event),
        )
        calthread.daemon = True
        calthread.start()

    def open_btn(self):
        self.new_map = False
        self.btnmapping = [True]
        btnthread = threading.Thread(
            target=self.btnmapper.build_btns,
            args=(self.mapped_btns, self.canvas, self.cal_event, self.btnmapping),
        )
        btnthread.daemon = True
        btnthread.start()

    def processEvent(self):
        while self.queue.qsize():
            event = self.queue.get(0)
            self.update(event)

    def update(self, event):

        if self.btnmapping[0] and "Button" in event[0] and 1 == event[1]:
            self.btnmapper.put_event(event)
            self.cal_event.set()

        else:
            # Open up mapping gui
            if "map" in event:
                self.open_map()

            # Run calibration over gui
            if "cal" in event:
                self.open_cal()

            # Close calibration TODO - set by role not button number
            if self.calibrate and ("Button_Start", 1) == event:
                self.calibrator.close_gui()
                self.calibrate = False
                self.master.bind("<Button-3>", self.show_menu)

            # Send frame to calibration when 'A' button is pressed
            if self.calibrate and ("Button_A", 1) == event:
                self.calibrator.put_frame(self.device.poll())
                self.cal_event.set()

            # Redo to calibration when 'B' button is pressed
            if self.calibrate and ("Button_B", 1) == event:
                self.calibrator.redo()
                self.cal_event.set()

            # TODO - When mapping structure is done this should change image by role
            if "Button" in event[0]:
                key = event[0].split("n")
                num = int(key[1]) + 1
                if event[1] == 1:
                    self.canvas.itemconfig(
                        self.buttons[num], image=self.btn_images[num][1]
                    )
                else:
                    self.canvas.itemconfig(
                        self.buttons[num], image=self.btn_images[num][0]
                    )

        self.canvas.update_idletasks()
        self.canvas.update()

    # Right click context menu
    def show_menu(self, event):
        if not self.btnmapping[0]:
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
        self.gui.canvas.update_idletasks()
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
        else:
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
