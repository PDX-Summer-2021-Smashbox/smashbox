import tkinter as tk
import threading, json

from smashbox_viewer.button_roles import BUTTON_ROLES
from smashbox_viewer.event_gen import diff_frames
from tkinter.constants import BOTH, CENTER, END, LEFT, RIGHT, VERTICAL

"""
A "calibration dictionary" is of the following form:
    {
        control_surface1 : {
            state1: [[button1]],
            state2: [[button2, button3], [button4, button5]]
            state: [[mode, ]]
            # ...
        },
        control_surface2 : {
            state3: [[button3]],
            state4: [[button4]],
            # ...
        }
    }
    A subdict is a singleton dictionary that contains one of these key-value pairs.
"""

class Calibrator:
    def __init__(self):
        self.calibration = {}
        self.running = False
        self.confirm = False
        self.frame = {}
        self.zeros = {}
        self.sticknames = ["D", "C"]
        self.sticks = {}
        self.all_dirs = [
            "LEFT",
            "UP & LEFT",
            "UP",
            "UP & RIGHT",
            "RIGHT",
            "DOWN & RIGHT",
            "DOWN",
            "DOWN & LEFT",
        ]
        self.no_x_dirs = [
            "UP & LEFT",
            "UP",
            "UP & RIGHT",
            "DOWN & RIGHT",
            "DOWN",
            "DOWN & LEFT",
        ]
        self.no_y_dirs = [
            "LEFT",
            "UP & LEFT",
            "UP & RIGHT",
            "RIGHT",
            "DOWN & RIGHT",
            "DOWN & LEFT",
        ]

    def gui(self, canvas, mapping, cal_event):
        self.running = True
        self.canvas = canvas
        self.mapping = mapping
        self.cal_event = cal_event

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

        # Grabbing joystick zeros
        self.get_zero()
        
        # Find axes, build sticks, assign dictionary values for full press
        for stick in self.sticknames:
            frames = self.build_frames(self.all_dirs, stick)
            self.build_stick(stick, frames)
        print(self.sticks)

    

    def build_stick(self, stick, frames):
        diffs = dict(diff_frames(frames[0], frames[1]))
        max = 0.0
        x_axis, y_axis = "", ""
        for key, value in diffs.items():
            if "Axis" in key:
                if abs(value) > abs(max):
                    max = value
                    x_axis = y_axis
                    y_axis = key
                else:
                    x_axis = key
        self.sticks[f"{stick}stick"] = (x_axis, y_axis)

    def build_frames(self, dirs, stick, modifiers=None):
        frames = []
        mods = ""
        if modifiers:
            for mod in modifiers:
                mods += f" + {mod}"
        while self.running and not self.confirm:
            for dir in dirs:
                self.canvas.itemconfig(
                    "prompt", text=f"Hold {stick}-Stick {dir}{mods} and press A"
                )
                self.wait_frame()
                if not self.running:
                    return
                frames.append(self.frame.copy())
            self.canvas.itemconfig("prompt", text="Confirm with A, retry with B")
            self.wait_frame()
        self.confirm = False
        return frames

    def get_zero(self):
        while self.running and not self.confirm:
            self.canvas.itemconfig("prompt", text="Getting baseline only press A")
            self.wait_frame()
            if not self.running:
                return
            for key, value in self.frame.items():
                if "Axis" in key:
                    self.zeros[key] = value
            self.canvas.itemconfig("prompt", text="Confirm with A, retry with B")
            self.wait_frame()
        self.confirm = False

    def wait_frame(self):
        while not self.cal_event.isSet():
            self.cal_event.wait()
        self.cal_event.clear()

        """
        # mapping check
        if "Modifier_X_3" in self.mapping.values or (
            "Modifier_X_1" in self.mapping.values
            and "Modifier_X_2" in self.mapping.values
        ):
            pass

        if "Modifier_Y_3" in self.mapping.values or (
            "Modifier_Y_1" in self.mapping.values
            and "Modifier_Y_2" in self.mapping.values
        ):
            pass

        if "Modifier_Tilt_3" in self.mapping.values or (
            "Modifier_Tilt" in self.mapping.values
            and "Modifier_Tilt_2" in self.mapping.values
        ):
            pass

        if "Modifier_Mode" in self.mapping.values:
            pass

        if (
            "C_Stick_Up" not in self.mapping.values
            or "C_Stick_Down" not in self.mapping.values
            or "C_Stick_Left" not in self.mapping.values
            or "C_Stick_Right" not in self.mapping.values
            and "Modifier_Analog_Stick_Becomes_C_Stick" in self.mapping.values
        ):
            pass

        # TODO - Special cases
        
        if "Modifier_Mode_With_Shield_Toggle" in self.mapping.values:
            pass
        if (
            "Button_DPad_Up" not in self.mapping.values
            or "Button_DPad_Down" not in self.mapping.values
            or "Button_DPad_Left" not in self.mapping.values
            or "Button_DPad_Right" not in self.mapping.values
            and "Modifier_Analog_Stick_Becomes_Dpad" in self.mapping.values
        ):
            pass
        """

    def put_frame(self, frame):
        self.frame.clear()
        self.frame = frame
        self.confirm = True

    def redo(self):
        self.frame.clear()
        self.confirm = False

    def close_gui(self):
        self.running = False
        self.canvas.delete("bot_text")
        self.canvas.delete("prompt")
