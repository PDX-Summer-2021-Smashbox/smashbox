class ButtonMapper:
    """
    Used to build a dictonary of button roles to the raw buttons for the controller

    This is performing well and exiting its thread properly
    """

    def __init__(self):
        """
        Contains a list of all possible buttons that could be mapped
        to check against the user mapping.
        """
        self.pos_roles = [
            "Button_A",
            "Button_B",
            "Button_X",
            "Button_Y",
            "Button_Z",
            "Trigger_R",
            "Trigger_L",
            "Button_DPad_Up",
            "Button_DPad_Down",
            "Button_DPad_Left",
            "Button_DPad_Right",
        ]
        self.roles = []
        self.correct = False
        self.event = None

    def wait_event(self):
        """
        Waits for a signal that the gui.py has sent a controller event
        then resets the signal and returns to the waiting function.
        """
        while not self.cal_event.isSet():
            self.cal_event.wait()
        self.cal_event.clear()

    def build_btns(self, profile, mapping, canvas, cal_event, end_btnmap):
        """
        Scans the mapping and the list of all possible buttons to make
        a list of buttons that need to be bound in the dictionary

        Prompts the user to press each button and then confirm.
        If the user presses B or any button that is not assigned properly
        will restart the loop. Upon confirmation updates the dictionary
        and quits.
        """
        self.cal_event = cal_event
        self.canvas = canvas

        for role in self.pos_roles:
            if role in mapping.values():
                self.roles.append(role)

        clean_map = {}
        self.canvas.itemconfig("prompt", text="No buttons bound, Press Button_Start")
        self.wait_event()
        self.add_button(self.event[0], "Button_Start", clean_map)

        while not self.correct:

            tmp_map = clean_map.copy()
            for role in self.roles:
                self.canvas.itemconfig("prompt", text=f"Press {role}")
                self.wait_event()
                self.add_button(self.event[0], role, tmp_map)
            self.canvas.itemconfig("prompt", text="Confirm with A, retry with B")
            while True:
                self.wait_event()
                if self.event[0] not in tmp_map:
                    break
                if "Button_A" in tmp_map[self.event[0]][1][0][0]:
                    self.correct = True
                    profile.update(tmp_map)
                    break
                if "Button_B" in tmp_map[self.event[0]][1][0][0]:
                    break
        print(profile)
        end_btnmap()
        self.close()

    def add_button(self, btn, role, map):
        """
        Helper function to add roles to the dictonary. The elif/else
        are only necesarry if the user is pressing the same button for multiple
        roles.
        """
        if btn not in map:
            map[btn] = {1: [[role]]}
        elif 1 not in map[btn]:
            map[btn][1] = [[role]]
        else:
            map[btn][1].append([role])

    def put_event(self, event):
        """
        Helper function that allows the gui.py to send a raw controller
        event
        """
        if self.event:
            self.event = None
        self.event = event
        self.confirm = True

    def close(self):
        """
        Reset variables to default and remove the prompting text from the screen
        """
        self.roles.clear()
        self.event = None
        self.confirm = False
        self.canvas.delete("prompt")
