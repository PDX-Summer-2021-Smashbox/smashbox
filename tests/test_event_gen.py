import itertools

from smashbox import event_gen, poller
from . import consts


def test_time_delay_event_gen():
    """
    Tests a Time Delay Event Gen to make sure that button transitions are
    captured.
    """
    gen = event_gen.EventGenerator(
        poller.TimeDelayMockPoller(consts.SIMPLE_BUTTON_FRAMES, loop=True)
    )
    assert list(itertools.islice(iter(gen), 2)) == [("Button0", 1), ("Button0", 0)]


def test_sequential_event_gen():
    """
    Tests a Sequential Delay Event Gen to make sure that button transitions
    are captured.
    """
    gen = event_gen.EventGenerator(
        poller.SequentialMockPoller(consts.SIMPLE_BUTTON_FRAMES, loop=True)
    )
    assert list(itertools.islice(iter(gen), 4)) == [("Button0", 1), ("Button0", 0)] * 2
