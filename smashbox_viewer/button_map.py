class ButtonMapper:
    def __init__(self):
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
        self.btn_map = {}

    def wait_event(self):
        while not self.cal_event.isSet():
            self.cal_event.wait()
        self.cal_event.clear()

    def build_btns(self, mapping, canvas, cal_event, running):
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
                    self.btn_map.update(tmp_map)
                    break
                if "Button_B" in tmp_map[self.event[0]][1][0][0]:
                    break
        print(self.btn_map)
        running[0] = False
        self.close()

    def add_button(self, btn, role, map):
        if btn not in map:
            map[btn] = {1: [[role]]}
        elif 1 not in map[btn]:
            map[btn][1] = [[role]]
        else:
            map[btn][1].append([role])

    def put_event(self, event):
        if self.event:
            self.event = None
        self.event = event
        self.confirm = True

    def close(self):
        self.roles.clear()
        self.event = None
        self.confirm = False
        self.btn_map.clear()
        self.canvas.delete("prompt")
