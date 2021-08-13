import importlib.resources
from smashbox_viewer.button_roles import BUTTON_ROLES
from smashbox_viewer.translator import QuasiTranslator, RawTranslator
import tkinter as tk

from PIL import ImageTk, Image
import threading, queue, pygame, json

from ast import literal_eval
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
    "default": resources,
    "black": other_package_name,
    "transparent":
}

get_resources(skins_dict["default"], filename)
"""


def get_resource(filename):
    """
    Wrapper around importlib's resources functionality. Returns a context
    manager that represents a filehandle.
    """
    return importlib.resources.path(resources, filename)


def parse_calibration_dict(file):
    raw_dict = json.load(file)
    return {
        outer_k: {
            literal_eval(inner_k): inner_v for inner_k, inner_v in outer_v.items()
        }
        for outer_k, outer_v in raw_dict.items()
    }


class Gui:
    """
    Class to display controller output based from EventGenerator.
    Takes a tkinter window on initialization and puts a frame/canvas with
    all the buttons and axis visualization.

    TODO - Once mapping is done button images need to be properly
    choosen and assigned with button locations. Buttons will probably
    need a data structure to track location, button image, pressed image.
    """

    def __init__(self, master, device):
        self.master = master
        self.device = device

        self.new_map = True
        self.translate = True
        self.btnmapping = False
        self.calibrate = False

        self.buttons = {}
        self.btn_images = {}
        self.layout = {}
        self.profile = {}
        self.sticks = {}
        self.running = 1

        self.queue = queue.Queue()
        self.mapper = Mapper()
        self.btnmapper = ButtonMapper()
        self.calibrator = Calibrator()
        self.cal_event = threading.Event()

        try:
            with open("mapped.json") as file:
                self.layout = json.load(file)
        except:
            # LOAD DEFAULT if no custom
            pass

        try:
            with open("profile.json") as file:
                self.profile = parse_calibration_dict(file)
                self.new_map = False

        except:
            self.translate = False
            pass

        master.title("Smashbox Viewer")
        self.master.protocol("WM_DELETE_WINDOW", self.end_gui)
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

        for role in self.layout.values():
            imgs = []
            if role == "Button_Disabled":
                with get_resource(f"Transparent.png") as img_fh:
                    imgs.append(ImageTk.PhotoImage(Image.open(img_fh)))

                with get_resource(f"Transparent.png") as img_fh:
                    imgs.append(ImageTk.PhotoImage(Image.open(img_fh)))

            else:
                with get_resource(f"{role}.png") as img_fh:
                    imgs.append(ImageTk.PhotoImage(Image.open(img_fh)))

                with get_resource(f"{role}_Pressed.png") as img_fh:
                    imgs.append(ImageTk.PhotoImage(Image.open(img_fh)))

            self.btn_images.update({role: imgs})

        self.canvas.create_image(0, 0, anchor="nw", image=self.background)

        for btn, role, img in zip(
            BUTTON_LOCATIONS, self.btn_images.keys(), self.btn_images.values()
        ):
            # print(btn + " " + role + " " + img)
            self.buttons.update(
                {
                    role: self.canvas.create_image(
                        BUTTON_LOCATIONS[btn][0], BUTTON_LOCATIONS[btn][1], image=img[0]
                    )
                }
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

        self.master.update_idletasks()
        self.master.update()
        self.run_gui()

    def cli_map(self):
        self.layout = self.mapper.cli()

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
        calthread = threading.Thread(
            target=self.calibrator.gui,
            args=(self.canvas, self.layout, self.cal_event, self.refresh),
        )
        calthread.daemon = True
        calthread.start()

    def open_btn(self):
        self.new_map = False
        self.btnmapping = True
        btnthread = threading.Thread(
            target=self.btnmapper.build_btns,
            args=(
                self.profile,
                self.layout,
                self.canvas,
                self.cal_event,
                self.end_btnmap,
                self.refresh
            ),
        )
        btnthread.daemon = True
        btnthread.start()

    def processEvent(self):
        while self.queue.qsize():
            event = self.queue.get(0)
            self.update(event)

    def refresh(self):
        self.master.update_idletasks()
        self.master.update()

    def update(self, event):
        # Open up mapping gui
        if "map" in event:
            self.open_map()

        # Run calibration over gui
        elif "cal" in event:
            self.open_cal()

        elif self.btnmapping and "Button" in event[0] and 1 == event[1]:
            self.btnmapper.put_event(event)
            self.cal_event.set()

        elif not self.btnmapping:

            # Close calibration
            if self.calibrate and ("Button_Start", 1) == event:
                self.calibrator.close_gui()
                self.calibrate = False
                self.master.bind("<Button-3>", self.show_menu)
                self.profile.update(self.calibrator.get_calibration())
                self.sticks = self.calibrator.get_sticks()
                self.switch()
                print(self.sticks)
                print(self.profile)
                # self.save_profile()

            # Send frame to calibration when 'A' button is pressed
            if self.calibrate and ("Button_A", 1) == event:
                print("SEND FRAME")
                self.calibrator.put_frame(self.device.poll())
                self.cal_event.set()

            # Redo to calibration when 'B' button is pressed
            if self.calibrate and ("Button_B", 1) == event:
                self.calibrator.redo()
                self.cal_event.set()

            # TODO - When mapping structure is done this should change image by role

            if event[1] == 1:
                self.canvas.itemconfig(
                    self.buttons[event[0]], image=self.btn_images[event[0]][1]
                )
            else:
                self.canvas.itemconfig(
                    self.buttons[event[0]], image=self.btn_images[event[0]][0]
                )

        self.canvas.update_idletasks()
        self.canvas.update()

    # Right click context menu
    def show_menu(self, event):
        if not self.btnmapping:
            try:
                self.menu.post(event.x_root, event.y_root)
            finally:
                self.menu.grab_release()

    def save_profile(self):
        with open("profile.json", "w") as export_file:
            export_file.write(json.dumps(self.profile, indent=4))

    def end_btnmap(self):
        self.btnmapping = False
        self.switch()

    def end_gui(self):
        self.running = 0

    def run_gui(self):
        self.event_gen = EventGenerator(self.device)
        self.t1 = threading.Thread(target=self.runVis)
        self.t1.daemon = True
        self.t1.start()
        self.eventCall()

    def eventCall(self):
        self.processEvent()
        if not self.running:
            self.save_profile()
            self.master.destroy()
        else:
            self.master.after(0, self.eventCall)

    def runVis(self):
        if self.translate:
            self.t_device = RawTranslator(
                FrameParser(self.device, self.sticks.copy()),
                self.layout.values(),
                self.profile.copy(),
            )
            for event in EventGenerator(self.t_device):
                self.queue.put(event)
                print(event)
        else:
            for event in EventGenerator(self.device):
                if self.translate:
                    break
                self.queue.put(event)
                print(event)

    def switch(self):
        self.translate = True
        self.t1 = threading.Thread(target=self.runVis)
        self.t1.daemon = True
        self.t1.start()
        self.eventCall()


# Testing program


def main():
    pygame.display.init()
    pygame.joystick.init()
    device = JoystickPoller(pygame.joystick.Joystick(0))
    device.joystick.init()

    root = tk.Tk()
    gui = Gui(root, device)
    root.mainloop()


if __name__ == "__main__":
    main()
