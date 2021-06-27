import itertools
import time

from smashbox import poller
from . import consts


def test_duration_poller():
    """
    Tests to make sure that the TimeDelayMockPoller's output changes according
    to time after creation.
    """
    p = poller.TimeDelayMockPoller(consts.SIMPLE_BUTTON_FRAMES, loop=True)
    assert next(p) == {"Button0": 0}
    time.sleep(0.6)
    assert next(p) == {"Button0": 1}
    time.sleep(0.6)
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
