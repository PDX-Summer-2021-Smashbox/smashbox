import itertools
import time

from smashbox import poller
from . import consts


def test_duration_poller():
    """
    Tests to make sure that the TimeDelayMockPoller's output changes according
    to time after creation.
    """
    p = poller.TimeDelayMockPoller(consts.FAST_BUTTON_FRAMES, loop=True)
    assert next(p) == {"Button0": 0}
    time.sleep(2 / poller.DEVICE_HZ)
    assert next(p) == {"Button0": 1}
    time.sleep(2 / poller.DEVICE_HZ)
    assert next(p) == {"Button0": 0}


def test_sequential_poller():
    """
    Tests to make sure that the SequentialDelayMockPoller's output is every
    single frame that is stored in the object.
    """
    p = poller.SequentialMockPoller(consts.SIMPLE_BUTTON_FRAMES, loop=True)
    assert (
        list(itertools.islice(p, poller.DEVICE_HZ * 2))
        == consts.SIMPLE_BUTTON_FRAMES * 2
    )


def test_parse_frame():
    """
    Tests to make sure that parse_frame can parse a single frame.
    """
    assert poller.parse_frame(
        consts.COMBINE_AXES_DICT, consts.FRAME_PARSER_FRAMES[0]
    ) == {"Button0": 0, "Joystick1": (0, 0)}


def test_frame_parser():
    """
    Tests to make sure that a FrameParser's polling can parse multiple
    frames.
    """
    assert list(
        poller.FrameParser(
            poller.SequentialMockPoller(consts.FRAME_PARSER_FRAMES),
            consts.COMBINE_AXES_DICT,
        )
    ) == [
        {"Button0": 0, "Joystick1": (0, 0)},
        {"Button0": 1, "Joystick1": (0.5, 0)},
        {"Button0": 1, "Joystick1": (1, 1)},
    ]
