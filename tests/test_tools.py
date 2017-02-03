from functools import partial
import os

import pytest

from gptools.effect import EffectTools
from gptools.note import NoteTools

DIRNAME = os.path.dirname(__file__)


@pytest.mark.parametrize('cls, test_tab, method', [
    (NoteTools, 'test_shift_up.gp5', partial(NoteTools.shift, direction='up')),
    (NoteTools, 'test_shift_down.gp5', partial(NoteTools.shift, direction='down')),
    (NoteTools, 'test_shift_percussion.gp5', partial(NoteTools.shift, direction='up')),
    (NoteTools, 'test_shift_up_5.gp5', partial(NoteTools.shift, direction='up', amount=5)),
    (NoteTools, 'test_shift_down_5.gp5', partial(NoteTools.shift, direction='down', amount=5)),

    (NoteTools, 'test_duration_div_2.gp5', partial(NoteTools.modify_duration, operation='div', factor=2)),
    (NoteTools, 'test_duration_mul_2.gp5', partial(NoteTools.modify_duration, operation='mul', factor=2)),
    (NoteTools, 'test_duration_div_4.gp5', partial(NoteTools.modify_duration, operation='div', factor=4)),

    (NoteTools, 'test_brush_down_32.gp5', partial(NoteTools.brush, direction='down', duration=32)),

    (NoteTools, 'test_pick_stroke_down.gp5', partial(NoteTools.pick_stroke, direction='up')),

    (NoteTools, 'test_brush_remove.gp5', partial(NoteTools.remove, target='brush')),
    (NoteTools, 'test_text_remove.gp5', partial(NoteTools.remove, target='text')),

    (NoteTools, 'test_replace_with_rests.gp5', NoteTools.replace_with_rests),

    (EffectTools, 'test_set_dead.gp5', partial(EffectTools.set, effect='dead')),
])
def test_tools(cls, test_tab, method):
    tools = cls(os.path.join(DIRNAME, test_tab), None, [1])
    tools.parse()
    song = tools.song
    source_track, expected_track = song.tracks

    method(tools)

    for source_measure, expected_measure in zip(source_track.measures, expected_track.measures):
        source_voice = source_measure.voices[0]
        expected_voice = expected_measure.voices[0]
        for beat_number, (source_beat, expected_beat) in enumerate(zip(source_voice.beats, expected_voice.beats), start=1):
            print('measure', source_measure.number, 'beat', beat_number)
            print(source_beat)
            print(expected_beat)
            assert source_beat == expected_beat
