from functools import partial
import os

import pytest

from gptools.cli import GPTools

DIRNAME = os.path.dirname(__file__)


@pytest.mark.parametrize('test_tab, method', [
    ('test_shift_up.gp5', partial(GPTools.shift, direction='up')),
    ('test_shift_down.gp5', partial(GPTools.shift, direction='down')),
    ('test_shift_percussion.gp5', partial(GPTools.shift, direction='up')),
    ('test_shift_up_5.gp5', partial(GPTools.shift, direction='up', amount=5)),
    ('test_shift_down_5.gp5', partial(GPTools.shift, direction='down', amount=5)),

    ('test_duration_div_2.gp5', partial(GPTools.modify_duration, operation='div', factor=2)),
    ('test_duration_mul_2.gp5', partial(GPTools.modify_duration, operation='mul', factor=2)),
    ('test_duration_div_4.gp5', partial(GPTools.modify_duration, operation='div', factor=4)),

    ('test_brush_down_32.gp5', partial(GPTools.brush, direction='down', duration=32)),

    ('test_pick_stroke_down.gp5', partial(GPTools.pick_stroke, direction='up')),

    ('test_brush_remove.gp5', partial(GPTools.remove, target='brush')),
    ('test_text_remove.gp5', partial(GPTools.remove, target='text')),

    ('test_replace_with_rests.gp5', GPTools.replace_with_rests),
])
def test_tools(test_tab, method):
    gptools = GPTools(os.path.join(DIRNAME, test_tab), None, [1])
    gptools.parse()
    song = gptools.song
    source_track, expected_track = song.tracks

    method(gptools)

    for source_measure, expected_measure in zip(source_track.measures, expected_track.measures):
        source_voice = source_measure.voices[0]
        expected_voice = expected_measure.voices[0]
        for beat_number, (source_beat, expected_beat) in enumerate(zip(source_voice.beats, expected_voice.beats), start=1):
            print('measure', source_measure.number, 'beat', beat_number)
            print(source_beat)
            print(expected_beat)
            assert source_beat == expected_beat
