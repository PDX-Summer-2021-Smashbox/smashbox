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
    """
    Helper function to convert JSON loaded dictionary keys/values from strings
    back into ints, floats, and tuples.
    """
    raw_dict = json.load(file)
    return {
        outer_k: {
            literal_eval(inner_k): inner_v for inner_k, inner_v in outer_v.items()
        }
        for outer_k, outer_v in raw_dict.items()
    }

def parse_dict_json(dict):
    """
    Helper function that convers Python dictionary keys/values into strings
    to be dumped into a JSON file.
    """
    return {
        outer_k: {
            str(inner_k): inner_v for inner_k, inner_v in outer_v.items()
        }
        for outer_k, outer_v in dict.items()
    }

class Gui:
    """
    Class to display controller output based from EventGenerator.
    Takes a tkinter window on initialization and puts a frame/canvas with
    all the buttons and axis visualization.

    Handles the swapping between the button vizualizer, the mapper, and the calibrator.

    TODO - Fix the thread handling

    Current issue: The event handing is run in a background thread to allow normal 
    Tkinter keyboard/mouse handling.  This needs to be restarted based on changes in calibration
    between the raw events from the controller and the translated events when the calibration
    dictionary is loaded.

    Currently the calibration thread is not closing properly on exit. So everytime the calibration quit
    signal is sent the thread contiues to run until the program is closed.
    """

    def __init__(self, master, device):
        """
        Initializes all defaults for flags and storage for mapping and calibration

        Builds the intial window passed of the mapping and profile files if present.

        Using the profile provided builds the screen with the approriate buttons, 
        loading them into memory in a dictionary. The order of the profile is the same
        as the button locations so the loop can place them in the correct spots on screen.

        If there is no profile forces the user to build the profile for buttons only.
        """
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
        self.sticks = {} #{'Astick': ('Axis0', 'Axis1'), 'Cstick': ('Axis3', 'Axis4')} # TODO: CHANGE THIS BACK {}
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
        """
        Opens the command line mapping interface
        """
        self.layout = self.mapper.cli()

    def open_map(self):
        """
        Hides the visualizer window and opens the mapper in
        a new tk window, when that window signals an exit,
        shows the visualizer again.        
        """
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
        """
        Opens the calibration gui in a seperate thread.  Still uses the same
        window as the visualizer.

        Adds the starting prompt text to get around tkinter update issues.
        """
        self.calibrate = True
        self.master.unbind("<Button-3>")
        self.canvas.create_text(
            (self.canvas.winfo_width() / 2),
            20,
            fill="red",
            font="Arial 20 bold",
            text="Getting baseline only press A",
            anchor="center",
            tag="prompt",
        )

        self.canvas.create_text(
            (self.canvas.winfo_width() / 2),
            600,
            fill="red",
            font="Arial 20 bold",
            text="Calibrating - Press Start to exit.",
            anchor="center",
            tag="bot_text",
        )
        self.master.update_idletasks()
        self.master.update()
        calthread = threading.Thread(
            target=self.calibrator.gui,
            args=(self.canvas, self.layout, self.cal_event),
        )
        calthread.daemon = True
        calthread.start()

    def open_btn(self):
        """
        Used to map buttons to calibration dictionary.
        Assigns flags for the update function to work properly
        and opens the button mapper in a new thread.
        """
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
            ),
        )
        btnthread.daemon = True
        btnthread.start()

    def update(self, event):
        """
        Handles the control of the changes in the gui.
        Events come from the queue and based on the event and the
        current settings of flags runs other functions or updates
        the images on the canvas for button presses


        """
        # Open up mapping gui
        if "map" in event:
            self.open_map()

        # Run calibration over gui
        elif "cal" in event:
            self.open_cal()

        # If the button mapper is active, sends the raw gamepad events to the mapper
        elif self.btnmapping and "Button" in event[0] and 1 == event[1]:
            self.btnmapper.put_event(event)
            self.cal_event.set()

        elif not self.btnmapping:

            # Close calibration, rest flag, rebind menu button, update calibration and sticks
            # Restart the event generator to use translated events
            if self.calibrate and ("Button_Start", 1) == event:
                self.calibrator.close_gui()
                self.calibrate = False
                self.master.bind("<Button-3>", self.show_menu)
                self.profile.update(self.calibrator.get_calibration())
                self.sticks = self.calibrator.get_sticks()
                self.switch()
                self.save_profile()

            # Send frame to calibrator when 'A' button is pressed
            if self.calibrate and ("Button_A", 1) == event:
                print("SEND FRAME")
                self.calibrator.put_frame(self.device.poll())
                self.cal_event.set()

            # Send Redo to calibration when 'B' button is pressed
            if self.calibrate and ("Button_B", 1) == event:
                self.calibrator.redo()
                self.cal_event.set()

            # Swaps the image for the approriate role, which is event[0], based on
            # the state from the event[1]. 1 is pressed, 0 is released
            if event[1] == 1:
                self.canvas.itemconfig(
                    self.buttons[event[0]], image=self.btn_images[event[0]][1]
                )
            else:
                self.canvas.itemconfig(
                    self.buttons[event[0]], image=self.btn_images[event[0]][0]
                )

        # Update the canvas at the end of every cycle
        self.canvas.update_idletasks()
        self.canvas.update()

    # Right click context menu
    def show_menu(self, event):
        """
        Show the context menu where the user right clicks on the window
        """
        if not self.btnmapping:
            try:
                self.menu.post(event.x_root, event.y_root)
            finally:
                self.menu.grab_release()

    def save_profile(self):
        """
        Dumps the calibration dictionary to the profile as a JSON
        """
        with open("profile.json", "w") as export_file:
            export_file.write(json.dumps(parse_dict_json(self.profile), indent=4))

    def end_btnmap(self):
        """
        Helper function to allow the button mapper to quit
        resets the flag and switchs the event generator to
        translation
        """
        self.btnmapping = False
        self.switch()

    def end_gui(self):
        """
        Flag to signal the user has closed the main window
        """
        self.running = 0

    def run_gui(self):
        """
        Used to start the initial visualizer run. Opens the visualizer
        in a new thread and starts event generation in the main thread
        with the eventCall()
        """
        self.event_gen = EventGenerator(self.device)
        self.t1 = threading.Thread(target=self.runVis)
        self.t1.daemon = True
        self.t1.start()
        self.eventCall()

    def runVis(self):
        """
        TODO Fix this. It is a mess and I spent a whole day dancing around
        it and it repeatedly punched me in the face.

        Currently uses the self.translate flag to decide which loop to run
        The translate loop uses a device wioth the sticks and calibration dictionaries
        to produce events by role

        The second loop uses the raw events from the gamepad device.
        """
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
    
    def processEvent(self):
        """
        Checks the queue for events and sends them to the update
        function as they appear.
        """
        while self.queue.qsize():
            event = self.queue.get(0)
            self.update(event)

    def eventCall(self):
        """
        Calls the event processor for any pending events.
        If the user has closed the window saves the profile and exits.
        Otherwise uses the main window to loop itself waiting for events
        """
        self.processEvent()
        if not self.running:
            self.save_profile()
            self.master.destroy()
        else:
            self.master.after(0, self.eventCall)

    def switch(self):
        """
        Swaps the runVis to a translated loop
        """
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
