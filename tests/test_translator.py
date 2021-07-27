import itertools
import time

from smashbox_viewer import poller, translator
from . import consts


def test_translator():
    device = translator.Translator(
        poller.SequentialMockPoller(consts.FRAME_PARSER_FRAMES),
        ["Button1", "Button2", "Button3", "Button4", "ModifierButton"],
        consts.CALIBRATION_DICT,
    )
    assert list(device) == consts.TRANSLATOR_FRAMES
