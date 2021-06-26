#!/bin/env python3

"""
Wrapper class that polls frames from devices.

A frame is a dictionary that associates buttons, axes, and hats with integer
values.

A device is a source that generates frames.
"""

import itertools
import json
import os
import time

os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "hide"
import pygame


# All classes must implement the Poller interface. The Poller interface has a
# single method: `poll`, which returns a frame. Pollers are also iterable,
# meaning that a `for` loop can iterate over them if so desired.


DEVICE_HZ = 30


class JoystickPoller:
    """
    Wrapper around a PyGame joystick. Implements the Poller interface.
    """

    def __init__(self, joystick):
        self.joystick = joystick

    def poll(self):
        pygame.event.pump()
        button_states = {
            f"Button{i}": self.joystick.get_button(i)
            for i in range(self.joystick.get_numbuttons())
        }
        axis_states = {
            f"Axis{i}": self.joystick.get_axis(i)
            for i in range(self.joystick.get_numaxes())
        }
        hat_states = {
            f"Hat{i}": self.joystick.get_hat(i)
            for i in range(self.joystick.get_numhats())
        }
        return {**button_states, **axis_states, **hat_states}

    def __iter__(self):
        return self

    def __next__(self):
        return self.poll()


class TimeDelayMockPoller:
    """
    Wrapper around a mocked Smashbox controller. Implements the Poller interface.
    Contains a data structure that numbers frames at `DEVICE_HZ` Hz. When
    polled, it examines the difference between the current time and the time
    that it was created and returns that frame. So, Frame 0 will be returned at
    the instant that the object was created, and Frame (`DEVICE_HZ-1`) will be returned 1
    second later.

    If the device is created with the `loop` argument being `True`, polling it will
    repeat endlessly. Otherwise, polling it will return an IndexError.
    """

    def __init__(self, frames, *, loop=False):
        self.frames = frames
        self.loop = loop
        self.creation_time = time.monotonic()

    def poll(self):
        frame_index = int((time.monotonic() - self.creation_time) * DEVICE_HZ)
        if self.loop:
            frame_index %= len(self.frames)
        return self.frames[frame_index]

    def __iter__(self):
        return self

    def __next__(self):
        return self.poll()


class SequentialMockPoller:
    """
    Wrapper around a mocked Smashbox controller. Implements the Poller interface.
    Contains a data structure that contains frames. Unlike the TimeDelay object,
    this class returns each frame in sequence. This is intended for instant unit
    testing of a sequence of frames instead of implementing time delays and waiting
    intervals of time for the correct frames.

    If the device is created with the `loop` argument being `True`, polling it will
    repeat endlessly. Otherwise, polling it will return a StopIterator.
    """

    def __init__(self, frames, *, loop=False):
        self.frames = itertools.cycle(frames) if loop else iter(frames)

    def poll(self):
        return next(self.frames)

    def __iter__(self):
        return self

    def __next__(self):
        return self.poll()


def create_time_delay_mock_poller(filename, *, loop=False):
    """Creates a TimeDelayMockPoller from a JSON object."""
    with open(filename) as f:
        return TimeDelayMockPoller(json.load(f), loop=loop)


def create_sequential_mock_poller(filename, *, loop=False):
    """Creates a SequentialMockPoller from a JSON object."""
    with open(filename) as f:
        return SequentialMockPoller(json.load(f), loop=loop)
