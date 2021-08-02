import itertools

from smashbox_viewer import event_gen, poller
from . import consts


def test_time_delay_event_gen():
    """
    Tests a Time Delay Event Gen to make sure that button transitions are
    captured.
    """
    gen = event_gen.EventGenerator(
        poller.TimeDelayMockPoller(consts.FAST_BUTTON_FRAMES, loop=True)
    )
    assert list(itertools.islice(filter(bool, gen), 2)) == [
        ("Button0", 1),
        ("Button0", 0),
    ]


def test_sequential_event_gen():
    """
    Tests a Sequential Delay Event Gen to make sure that button transitions
    are captured.
    """
    gen = event_gen.EventGenerator(
        poller.SequentialMockPoller(consts.SIMPLE_BUTTON_FRAMES, loop=True)
    )
    assert (
        list(itertools.islice(filter(bool, iter(gen)), 4))
        == [("Button0", 1), ("Button0", 0)] * 2
    )


def test_frame_parser_event_gen():
    """
    Tests to make sure that an EventGenerator based on a FrameParser produces
    the appropriate events.
    """
    gen = event_gen.EventGenerator(
        poller.FrameParser(
            poller.SequentialMockPoller(consts.FRAME_PARSER_FRAMES),
            consts.COMBINE_AXES_DICT,
        )
    )
    assert list(filter(bool, iter(gen))) == [
        ("Joystick1", (0.5, 0)),
        ("Button0", 1),
        ("Joystick1", (1, 1)),
    ]
