"""
Constants used in testing. Handy data structures, pollers, etc.
"""

from smashbox_viewer import poller

SIMPLE_BUTTON_FRAMES = [
    *[{"Button0": 0}] * (poller.DEVICE_HZ // 2),
    *[{"Button0": 1}] * (poller.DEVICE_HZ // 2),
]

FAST_BUTTON_FRAMES = [
    *[{"Button0": 0}] * 2,
    *[{"Button0": 1}] * 2,
]

FRAME_PARSER_FRAMES = [
    {"Button0": 0, "Axis1": 0, "Axis2": 0},
    {"Button0": 1, "Axis1": 0.5, "Axis2": 0},
    {"Button0": 1, "Axis1": 1, "Axis2": 1},
]

COMBINE_AXES_DICT = {"Joystick1": ("Axis1", "Axis2")}

CALIBRATION_DICT = {
    "Axis1": {
        0.5: ["ModifierButton", "Button1"],
        1: ["Button1"],
        -0.5: ["ModifierButton", "Button2"],
        -1: ["Button2"],
    },
    "Axis2": {
        0.5: ["ModifierButton", "Button3"],
        1: ["Button3"],
        -0.5: ["ModifierButton", "Button4"],
        -1: ["Button4"],
    },
}

TRANSLATOR_FRAMES = [
    {"Button1": 0, "Button2": 0, "Button3": 0, "Button4": 0, "ModifierButton": 0},
    {"Button1": 1, "Button2": 0, "Button3": 0, "Button4": 0, "ModifierButton": 1},
    {"Button1": 1, "Button2": 0, "Button3": 1, "Button4": 0, "ModifierButton": 0},
]

TRANSLATOR_EVENT_FRAMES = [
    ("Button1", 1),
    ("ModifierButton", 1),
    ("Button3", 1),
    ("ModifierButton", 0),
]
