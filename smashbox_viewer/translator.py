"""
Device that performs translation from one set of buttons on a device to another
set of buttons. As always, a Device generates frames, either with a `poll`
method or by iterating over the frames.

A "calibration dictionary" is of the following form:

    {
        control_surface1 : {
            state1: [button1],
            state2: [button2, button3]
            # ...
        },
        control_surface2 : {
            state3: [button3],
            state4: [button4],
            # ...
        }
    }

    A subdict is a singleton dictionary that contains one of these key-value pairs.
"""

import itertools

"""
Given a button list, a calibration dictionary, and a frame, translate the frame into
a translated frame of the buttons in the button list.
"""


def translate_frame(button_lst, calibration_dict, frame):
    pressed_buttons = set(
        itertools.chain.from_iterable(
            calibration_dict[surface].get(frame[surface], [])
            for surface in calibration_dict
        )
    )
    return {button: int(button in pressed_buttons) for button in button_lst}


class Translator:
    def __init__(self, device, button_lst, calibration_dict):
        self.device = device
        self.button_lst = button_lst
        self.calibration_dict = calibration_dict

    def poll(self):
        return translate_frame(
            self.button_lst, self.calibration_dict, self.device.poll()
        )

    def __iter__(self):
        return self

    def __next__(self):
        return self.poll()
