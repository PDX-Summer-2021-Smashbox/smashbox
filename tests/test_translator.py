import itertools
import time

from smashbox_viewer import poller, translator, event_gen
from . import consts


def test_translator():
    device = translator.RawTranslator(
        poller.SequentialMockPoller(consts.FRAME_PARSER_FRAMES),
        ["Button1", "Button2", "Button3", "Button4", "ModifierButton"],
        consts.CALIBRATION_DICT,
    )
    assert list(device) == consts.TRANSLATOR_FRAMES


def test_translator_event_gen():
    device = event_gen.EventGenerator(
        translator.RawTranslator(
            poller.SequentialMockPoller(consts.FRAME_PARSER_FRAMES),
            ["Button1", "Button2", "Button3", "Button4", "ModifierButton"],
            consts.CALIBRATION_DICT,
        )
    )
    assert list(device) == consts.TRANSLATOR_EVENT_FRAMES
