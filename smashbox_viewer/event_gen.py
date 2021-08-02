#!/usr/env python3

"""
Library to take a Device and generate an iterable of Events.

Events are tuples that associate a button, axis, or hat with a new state.
"""

import itertools

DEFAULT_AXIS_TOLERANCE = 0.01


class EventGenerator:
    """
    Wrapper around a Device that monitors for differences in frames.
    Any differences in frames will result in an Event.

    This wrapper also produces "heartbeats" which are intended to be ignored.
    These heartbeats are implemented as None. The point of this is to allow
    for the EventGenerator to be iterated over without hanging when there isn't
    any actual output.
    """

    def __init__(self, device, *, axis_tolerance=DEFAULT_AXIS_TOLERANCE):
        self.device = device
        self.axis_tolerance = axis_tolerance

    def __iter__(self):
        return itertools.chain.from_iterable(
            diff_frames(f1, f2, axis_tolerance=self.axis_tolerance)
            for f1, f2 in pairwise(self.device)
        )


def pairwise(iterable):
    """
    Takes an Iterable and returns an iterable of tuples that pair each of the elements
    with its respective successor.
    pairwise(range(5)) becomes [(0, 1), (1, 2), (2, 3), (3, 4)]
    """
    t1, t2 = itertools.tee(iterable, 2)
    next(t2)
    return zip(t1, t2)


def diff_elem(e1, e2, *, axis_tolerance=DEFAULT_AXIS_TOLERANCE):
    """
    Returns True if the difference between e1 and e2 is greater than axis_tolerance.
    This function can work on tuples as well, for the purpose of diffing hat states.
    """
    try:
        return abs(e1 - e2) >= axis_tolerance
    except TypeError:
        return sum(abs(x - y) for x, y in zip(e1, e2)) >= axis_tolerance


def diff_frames(f1, f2, *, axis_tolerance=DEFAULT_AXIS_TOLERANCE):
    """
    Examines each key-value pair in f2 and returns only those whose difference
    from the same elements in f1 is greater than axis_tolerance.

    Note that _all_ elements are compared to axis_tolerance, but things like buttons and hats
    have a difference of 1 or more when they change state.
    """
    return (
        (k, v) if diff_elem(f1[k], v, axis_tolerance=axis_tolerance) else None
        for k, v in f2.items()
    )
