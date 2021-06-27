"""
Constants used in testing. Handy data structures, pollers, etc.
"""

from smashbox import poller

SIMPLE_BUTTON_FRAMES = [
    *[{"Button0": 0}] * (poller.DEVICE_HZ // 2),
    *[{"Button0": 1}] * (poller.DEVICE_HZ // 2),
]

FAST_BUTTON_FRAMES = [
    *[{"Button0": 0}] * 2,
    *[{"Button0": 1}] * 2,
]
