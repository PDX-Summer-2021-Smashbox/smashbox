import itertools, json

from smashbox_viewer.button_roles import BUTTON_ROLES
from smashbox_viewer.event_gen import diff_frames


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
        button1: {
            1: [["Button_A"]]
        }
    }
    A subdict is a singleton dictionary that contains one of these key-value pairs.
"""


class Calibrator:
    """
    This class works to build a dictionary to translate axis states
    into button roles based on the current controller mapping.

    It prompts the user to press valid modifier combinations and records the
    resulting axis outputs with the button roles.

    #TODO - The exiting of this needs to be fixed so it it stops running,
    it currently keeps the thread open indefinetly 

    """

    def __init__(self):
        self.calibration = {}
        self.running = False
        self.confirm = False
        self.frame = {}
        self.zeros = {}
        self.sticknames = ["A", "C"]
        self.sticks = {}

        """
        Below is a temporary storage for the mapped modifier buttons.
        
        Then there are the directional dictionaries that store the 3 sets
        of calibration direction based on which modifiers are active. 
        """
        self.temps_mod = [[], []]
        self.all_dirs = {
            "LEFT": {"A": ["Analog_Stick_Left"], "C": ["C_Stick_Left"]},
            "UP & LEFT": {
                "A": ["Analog_Stick_Up", "Analog_Stick_Left"],
                "C": ["C_Stick_Up", "C_Stick_Left"],
            },
            "UP": {"A": ["Analog_Stick_Up"], "C": ["C_Stick_Up"]},
            "UP & RIGHT": {
                "A": ["Analog_Stick_Up", "Analog_Stick_Right"],
                "C": ["C_Stick_Up", "C_Stick_Right"],
            },
            "RIGHT": {"A": ["Analog_Stick_Right"], "C": ["C_Stick_Right"]},
            "DOWN & RIGHT": {
                "A": ["Analog_Stick_Down", "Analog_Stick_Right"],
                "C": ["C_Stick_Down", "C_Stick_Right"],
            },
            "DOWN": {"A": ["Analog_Stick_Down"], "C": ["C_Stick_Down"]},
            "DOWN & LEFT": {
                "A": ["Analog_Stick_Down", "Analog_Stick_Left"],
                "C": ["C_Stick_Down", "C_Stick_Left"],
            },
        }
        self.y_dirs = {
            "UP & LEFT": {
                "A": ["Analog_Stick_Up", "Analog_Stick_Left"],
                "C": ["C_Stick_Up", "C_Stick_Left"],
            },
            "UP": {"A": ["Analog_Stick_Up"], "C": ["C_Stick_Up"]},
            "UP & RIGHT": {
                "A": ["Analog_Stick_Up", "Analog_Stick_Right"],
                "C": ["C_Stick_Up", "C_Stick_Right"],
            },
            "DOWN & RIGHT": {
                "A": ["Analog_Stick_Down", "Analog_Stick_Right"],
                "C": ["C_Stick_Down", "C_Stick_Right"],
            },
            "DOWN": {"A": ["Analog_Stick_Down"], "C": ["C_Stick_Down"]},
            "DOWN & LEFT": {
                "A": ["Analog_Stick_Down", "Analog_Stick_Left"],
                "C": ["C_Stick_Down", "C_Stick_Left"],
            },
        }
        self.x_dirs = {
            "LEFT": {"A": ["Analog_Stick_Left"], "C": ["C_Stick_Left"]},
            "UP & LEFT": {
                "A": ["Analog_Stick_Up", "Analog_Stick_Left"],
                "C": ["C_Stick_Up", "C_Stick_Left"],
            },
            "UP & RIGHT": {
                "A": ["Analog_Stick_Up", "Analog_Stick_Right"],
                "C": ["C_Stick_Up", "C_Stick_Right"],
            },
            "RIGHT": {"A": ["Analog_Stick_Right"], "C": ["C_Stick_Right"]},
            "DOWN & RIGHT": {
                "A": ["Analog_Stick_Down", "Analog_Stick_Right"],
                "C": ["C_Stick_Down", "C_Stick_Right"],
            },
            "DOWN & LEFT": {
                "A": ["Analog_Stick_Down", "Analog_Stick_Left"],
                "C": ["C_Stick_Down", "C_Stick_Left"],
            },
        }

    def gui(self, canvas, mapping, cal_event):
        """
        This depends on the gui.py to run.  It takes in the active canvas
        and prompts the user with text across the top of the canvas.

        Based on the mapping provided it will decide with calibration
        modifiers to prompt the user for

        The cal_event is a thread flag that allows this thread to wait 
        for a frame from the gui.py
        """
        self.running = True
        self.canvas = canvas
        self.mapping = mapping
        self.cal_event = cal_event

        """
        Grabbing a zero state frame to reference. Then finding the active
        light shield button combinations, and prompting and building the calibration
        for the light sheld
        """
        self.get_zero()
        self.btns_lshield()
        self.get_lshield()

        """
        Gets the frame states for the joysticks, associates the joysticks with the 
        proper 2 axis for each stick. Build the calibration for full press in 
        all directions for each joystick
        """
        for name in self.sticknames:
            frames = self.build_frames(list(self.all_dirs.keys()), name)
            self.build_stick(name, frames)
            self.build_states(name, frames, self.all_dirs)

        """
        Gets the joystick modifiers then prompt and build them all
        """
        self.btns_sticks()
        self.build_mod()

        """
        If the user has any 'Mode' role button prompt calibration for them
        with all modifiers
        """
        mode = self.get_mode()
        if mode:
            self.build_mod(mode)

        """
        Exit
        """
        #print(self.calibration)
        self.close_gui()

    def get_mode(self):
        """
        Detect the presence of ANY mode role button in
        the user's mapping
        """
        for role in self.mapping.values():
            if "Mode" in role:
                return role
        return None

    def build_mod(self, mode=None):
        """
        Checks if this is a 'Mode' calibration loop and gets the Mode
        calibration for all sticks.

        Checks the list of modifiers for this runto see with set of 
        directions to prompt and build calibration values.

        If this is the 'Mode' run it will append the user's 'Mode' 
        button before prompting.
        """
        name = self.sticknames[0]
        if mode:
            for stick in self.sticknames:
                frames = self.build_frames(
                    list(self.all_dirs.keys()), self.sticknames[1], ["Mode"]
                )
                self.build_states(stick, frames, self.all_dirs, [mode])

        for mod in self.temps_mod[0]:
            dirs = {}
            dirs.clear()
            x_y_t = {"X": False, "Y": False, "Tilt": False}
            for btn in mod:
                if "Tilt" in btn.split("_"):
                    x_y_t["Tilt"] = True
                elif "X" in btn.split("_"):
                    x_y_t["X"] = True
                elif "Y" in btn.split("_"):
                    x_y_t["Y"] = True
            if x_y_t["Tilt"] or (x_y_t["X"] and x_y_t["Y"]):
                dirs = self.all_dirs
            elif x_y_t["X"]:
                dirs = self.x_dirs
            else:
                dirs = self.y_dirs

            if mode:
                mod.append(mode)
            frames = self.build_frames(list(dirs.keys()), name, mod)
            self.build_states(name, frames, dirs, mod)

    def build_states(self, name, frames, directions, modifiers=None):
        """
        Adds the calibration states to the self.calibration dictionary

        Using the stick name provided as the outer key, the tuple of axis
        values for the inner key, and the list of modifiers for the values
        to append to the list of lists since values can be ambiguous.

        Checks for the existence of the outer key, inner key, and the state
        to decide how to add the list
        """
        key = f"{name}stick"
        x_axis, y_axis = self.sticks[f"{name}stick"]
        for frame, dir in zip(frames, directions.values()):
            state = (frame[x_axis], frame[y_axis])
            buttons = dir[name].copy()
            if modifiers:
                buttons += modifiers
            if key not in self.calibration:
                self.calibration[key] = {state: [buttons]}
            elif state not in self.calibration[key]:
                self.calibration[key][state] = [buttons]
            else:
                self.calibration[key][state] += [buttons]

    def build_stick(self, stick, frames):
        """
        Associates axis with thier joysticks based the difference
        between the zero frame and the first 2 frames of full press
        for each stick.

        Builds a dictionary in the formL:
        {'Astick': ('Axis0', 'Axis1'), 'Cstick': ('Axis3', 'Axis4')}
        """
        diff_x = dict(diff_frames(self.zeros, frames[0]))
        diff_y = dict(diff_frames(frames[0], frames[1]))
        self.sticks[f"{stick}stick"] = (list(diff_x)[0], list(diff_y)[0])

    def build_frames(self, dirs, stick, modifiers=None):
        """
        Using one stick, a list of directions, and modifiers, prompts
        the user to press the buttons to build one frame for each direction

        Loops through all the directions with the modifiers and waits for the
        gui.py to send a frame and signal to proceed.  Appends the new frame.

        If the user confirms they did all the directions correct returns
        all the frames.
        """
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
        """
        Prompts the user to only press A. Waits for the frame and signal from
        the gui.py. Starts over if the user does not confirm.
        """
        while self.running and not self.confirm:
            self.canvas.itemconfig("prompt", text="Getting baseline only press A")
            self.wait_frame()
            if not self.running:
                return
            self.zeros = self.frame.copy()
            self.canvas.itemconfig("prompt", text="Confirm with A, retry with B")
            self.wait_frame()
        self.confirm = False

    def btns_sticks(self):
        """
        Builds a list of list of modifiers based on the user mapping.

        Using the dictionaries of boolean flags scans through the mapping
        and and changed the appropriate flags.

        First appends all individual modifiers.

        Then using the product from each set of active modifers appends
        all possible combinations.
        """
        self.temps_mod = [[]]
        x_flags = {"X_1": False, "X_2": False, "X_3": False}
        y_flags = {"Y_1": False, "Y_2": False, "Y_3": False}
        t_flags = {"Tilt": False, "Tilt_2": False, "Tilt_3": False}

        x_flags["X_1"] = self.in_map(0, ["Modifier_X_1"])
        x_flags["X_2"] = self.in_map(0, ["Modifier_X_2"])
        x_flags["X_3"] = self.in_map(0, ["Modifier_X_3"])

        if not x_flags["X_3"]:
            self.in_map(0, ["Modifier_X_1", "Modifier_X_2"])

        y_flags["Y_1"] = self.in_map(0, ["Modifier_Y_1"])
        y_flags["Y_2"] = self.in_map(0, ["Modifier_Y_2"])
        y_flags["Y_3"] = self.in_map(0, ["Modifier_Y_3"])

        if not y_flags["Y_3"]:
            self.in_map(0, ["Modifier_Y_1", "Modifier_Y_2"])

        t_flags["Tilt"] = self.in_map(0, ["Modifier_Tilt"])
        t_flags["Tilt_2"] = self.in_map(0, ["Modifier_Tilt_2"])
        t_flags["Tilt_3"] = self.in_map(0, ["Modifier_Tilt_3"])

        if not t_flags["Tilt_3"]:
            self.in_map(0, ["Modifier_Tilt", "Modifier_Tilt_2"])

        btn_combos = []
        btn_combos += [
            [x, y]
            for x, y in list(
                itertools.product(
                    [x for x in x_flags.keys() if x_flags[x]],
                    [y for y in y_flags.keys() if y_flags[y]],
                )
            )
        ]
        btn_combos += [
            [x, y]
            for x, y in list(
                itertools.product(
                    [x for x in x_flags.keys() if x_flags[x]],
                    [t for t in t_flags.keys() if t_flags[t]],
                )
            )
        ]
        btn_combos += [
            [x, y]
            for x, y in list(
                itertools.product(
                    [y for y in y_flags.keys() if y_flags[y]],
                    [t for t in t_flags.keys() if t_flags[t]],
                )
            )
        ]
        btn_combos = [x for x in btn_combos if x]

        self.temps_mod[0] += btn_combos

        self.in_map(0, ["Modifier_Analog_Stick_Becomes_C_Stick"])

        # TODO - Special cases
        """
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

    def btns_lshield(self):
        """
        Checks the user mapping for all possible combinations that could 
        produce a light sheild value.

        Adds values for left in the 0 index of self.temp_mods, right values 
        are put in the 1 index.
        """
        self.temps_mod = [[], []]
        self.in_map(0, ["Trigger_Light_L"])

        self.in_map(0, ["Modifier_Shield_Toggle", "Trigger_L"])

        self.in_map(1, ["Trigger_Light_R"])

        self.in_map(1, ["Modifier_Shield_Toggle", "Trigger_R"])

        self.in_map(0, ["Modifier_Mode", "Trigger_Light_L"])

        self.in_map(1, ["Modifier_Mode", "Trigger_Light_R"])

        self.in_map(0, ["Modifier_Mode", "Modifier_Shield_Toggle", "Trigger_L"])

        self.in_map(1, ["Modifier_Mode", "Modifier_Shield_Toggle", "Trigger_R"])

        self.in_map(0, ["Modifier_Mode_With_C_Stick_Rotate", "Trigger_Light_L"])

        self.in_map(1, ["Modifier_Mode_With_C_Stick_Rotate", "Trigger_Light_R"])

        self.in_map(
            0,
            [
                "Modifier_Mode_With_C_Stick_Rotate",
                "Modifier_Shield_Toggle",
                "Trigger_L",
            ],
        )

        self.in_map(
            1,
            [
                "Modifier_Mode_With_C_Stick_Rotate",
                "Modifier_Shield_Toggle",
                "Trigger_R",
            ],
        )

        self.in_map(0, ["Modifier_Mode_With_Shield_Toggle", "Trigger_L"])

        self.in_map(1, ["Modifier_Mode_With_Shield_Toggle", "Trigger_R"])

        self.in_map(
            0,
            [
                "Modifier_Mode_With_Shield_Toggle",
                "Modifier_Shield_Toggle",
                "Trigger_Light_L",
            ],
        )

        self.in_map(
            1,
            [
                "Modifier_Mode_With_Shield_Toggle",
                "Modifier_Shield_Toggle",
                "Trigger_Light_R",
            ],
        )

        self.in_map(
            0, ["Modifier_Mode_With_Shield_Toggle_With_C_Stick_Rotate", "Trigger_L"]
        )

        self.in_map(
            1, ["Modifier_Mode_With_Shield_Toggle_With_C_Stick_Rotate", "Trigger_R"]
        )

        self.in_map(
            0,
            [
                "Modifier_Mode_With_Shield_Toggle_With_C_Stick_Rotate",
                "Modifier_Shield_Toggle",
                "Trigger_Light_L",
            ],
        )

        self.in_map(
            1,
            [
                "Modifier_Mode_With_Shield_Toggle_With_C_Stick_Rotate",
                "Modifier_Shield_Toggle",
                "Trigger_Light_R",
            ],
        )

    def in_map(self, idx, buttons):
        """
        Checks the mapping for the list of buttons provided.
        If all of the buttons list is present appends the list
        to the index provided in self.temp_mods
        """
        flag = True
        for btn in buttons:
            if btn not in self.mapping.values():
                flag = False
                break
        if flag:
            self.temps_mod[idx].append(buttons)
        return flag

    def get_lshield(self):
        """
        TODO - Needs to get light shield values of left and right for
        both cases

        Checks the self.temp_mods lists for the presence of a 'Mode'
        role,  If the first case is 'Mode' there is no normal case.
        If there is no 'Mode' in any list there is only the normal case.

        Prompts the user for each case, waits for the frame and signal from gui.py
        
        Finds the axis with the greatest change from the zero frame and saves the
        axis and the value

        Builds a temporary dictionary with both cases then updates the calibration
        dictionary with it.
        """
        cases = ["Normal", "Mode"]
        btns = []
        f_mode = -1
        for dir in self.temps_mod:
            for i in range(len(dir)):
                if "Mode" in dir[i][0].split("_"):
                    f_mode = i
                    btns.append(dir[i])
                    if f_mode == 0 and "Normal" in cases:
                        cases.remove("Normal")
                    break
                elif i == 0:
                    btns.append(dir[i])
        if f_mode == -1:
            cases.remove("Mode")

        s_axis = []
        s_values = []

        while self.running and not self.confirm:
            s_axis.clear()
            s_values.clear()
            for case in cases:
                self.canvas.itemconfig(
                    "prompt", text=f"Hold {case} light shield and press A"
                )
                self.wait_frame()
                if not self.running:
                    return
                diff = dict(diff_frames(self.zeros, self.frame))
                max = 0.0
                axis = ""
                for key, val in diff.items():
                    if abs(val) > abs(max):
                        max = val
                        axis = key
                s_axis.append(axis)
                s_values.append(self.frame[axis])
            self.canvas.itemconfig("prompt", text="Confirm with A, retry with B")
            self.wait_frame()

        dic = {}
        for ax, val, btn in zip(s_axis, s_values, btns):
            dic.update({ax: {val: [btn]}})
        self.calibration.update(dic)

        self.confirm = False

    def get_calibration(self):
        """
        Returns the calibration dictionary
        """
        return self.calibration

    def get_sticks(self):
        """
        Returns the stick/axis association dictionary
        """
        return self.sticks

    def wait_frame(self):
        """
        Waits for a signal from another thread to keep from
        consuming CPU resources.

        When the signal is recieved, resets the signal flag
        and returns to the function that called this.
        """
        while not self.cal_event.isSet():
            self.cal_event.wait()
        self.cal_event.clear()

    def put_frame(self, frame):
        """
        Helper function that allows the gui.py to send a frame
        of the joystick device
        """
        if self.frame:
            self.frame.clear()
        self.frame = frame
        self.confirm = True

    def redo(self):
        """
        Clears the frame if the user does not confirm
        the correct input of buttons
        """
        self.frame.clear()
        self.confirm = False

    def close_gui(self):
        """
        Reset the calibration values to default
        and remove the prompt and exit text from the canvas
        """
        self.running = False
        self.temps_mod.clear()
        self.frame.clear()
        self.zeros.clear()
        self.canvas.delete("bot_text")
        self.canvas.delete("prompt")
