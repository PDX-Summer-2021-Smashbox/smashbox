#!/bin/env python3

"""
Simple utility to record the state of a device for an interval of time,
returning a JSON object representing its frames.
"""

import json
import os
import time

# To avoid spam from this package, we set an environment variable.
os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "hide"
import pygame

from . import poller


def create_recording(device, filename, *, max_time=None):
    """
    Records a device and stores the results into a JSON file named filename.
    Frames are accumulated at the rate of `poller.DEVICE_HZ` per second.
    If max_time is None, then it records indefinitely (which is likely a bad
    thing, as you'll run out of memory).
    You will probably want to cancel it with a KeyboardInterrupt, which it is
    listening for.
    """
    result = []
    creation_time = time.monotonic()
    while True:
        try:
            current_time = time.monotonic()
            if max_time and current_time - creation_time >= max_time:
                break
            current_index = int((current_time - creation_time) * poller.DEVICE_HZ)
            if current_index > len(result):
                result.append(device.poll())
        except KeyboardInterrupt:
            print("stopped")
            break
    with open(filename, "w") as f:
        json.dump(result, f)


def main():
    pygame.display.init()
    pygame.joystick.init()
    device = poller.JoystickPoller(pygame.joystick.Joystick(0))
    device.joystick.init()
    create_recording(device, "recording.json", max_time=3)


if __name__ == "__main__":
    main()
