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
