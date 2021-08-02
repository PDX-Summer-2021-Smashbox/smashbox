import importlib.resources
from os import read

from smashbox_viewer.mapper import Mapper
import tkinter as tk

from PIL import ImageTk, Image
import threading, queue, pygame


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

    def __init__(self, master, device):
        self.master = master
        self.device = device
        self.running = True
        self.queue = queue.Queue()
        self.buttons = []

        self.master.title("Smashbox Viewer")
        self.master.geometry()
        self.master.resizable(False, False)

        self.master.protocol("WM_DELETE_WINDOW", self.end)

        self.menu_frame = tk.Frame(master=self.master)
        self.menu_frame.pack()

        self.map_btn = tk.Button(self.menu_frame, text='Mapping', command=self.insert_map)
        self.map_btn.pack(side=tk.LEFT)

        self.menu = tk.StringVar(self.menu_frame)
        self.menu.set("Skin")
        self.select = tk.OptionMenu(self.menu_frame, self.menu, "one", "two")
        self.select.pack(side=tk.LEFT)

        self.btn_frame = tk.Frame(master=self.master)
        self.btn_frame.pack()
        self.canvas = tk.Canvas(self.btn_frame, width=1219, height=624)
        self.canvas.pack()

        with get_resource("base-unmapped.png") as img_fh:
            self.background = ImageTk.PhotoImage(Image.open(img_fh))

        with get_resource("A-2.png") as img_fh:
            self.button = ImageTk.PhotoImage(Image.open(img_fh))

        with get_resource("A.png") as img_fh:
            self.pressed = ImageTk.PhotoImage(Image.open(img_fh))

        self.vis_thread()

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

    def insert_map(self):
        map_event = "mapper"
        print("injecting mapper")
        self.queue.put(map_event) 

    def open_map(self):
        #map_event = "mapper"
        #self.queue.put(map_event)
        self.mapper = Mapper()
        root = tk.Tk()
        #root.geometry(f"1219x624+{self.master.winfo_x()}+{self.master.winfo_y()}")
        self.mapper.gui(root, root.winfo_x(), root.winfo_y())
        while(True):
            root.update_idletasks()
            root.update()
            if self.mapper.done:
                print(self.mapper.done)
                self.mapper.reset_done()
                break
        print("open map ended")
        
    """
    Takes tuple events from the Eventgenerator and changes images
    for button changes, moves joystick and trigger shapes on axis
    events.

    TODO: once mapping is handled will need to handle buttons individually
    to get proper images
    """

    def vis_update(self, diff):
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

        self.canvas.update()

    # Right click context menu
    def show_menu(self, event):
        try:
            self.menu.post(event.x_root, event.y_root)
        finally:
            self.menu.grab_release()
  
    def process_event(self):
        while self.queue.qsize():
            event = self.queue.get(0)
            print(event) 
            if isinstance(event, str): # if the event is "mapper"
                self.open_map()
                #while(True):
                #    if self.mapper.is_done:
                #        break
                #self.mapper.reset_done
                #print("reset done")

            self.vis_update(event)

    def vis_thread(self):
        self.t1 = threading.Thread(target=self.run_vis)
        self.t1.setDaemon(True)
        self.t1.start()

    def event_call(self):
        self.process_event()
        if not self.running:
            self.master.destroy()
        else:
            self.master.after(1//DEVICE_HZ, self.event_call)

    def run_vis(self):
        self.event_call()
        for event in EventGenerator(self.device):
            if event:
                self.queue.put(event)
                print(event)

    def end(self):
        self.running = False


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
