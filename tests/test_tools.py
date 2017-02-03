from functools import partial
import os

import pytest

from gptools.cli import GPTools

DIRNAME = os.path.dirname(__file__)


@pytest.mark.parametrize('test_tab, method', [
    ('test_shift_up.gp5', partial(GPTools.shift, direction='up')),
    ('test_shift_down.gp5', partial(GPTools.shift, direction='down')),
    ('test_shift_percussion.gp5', partial(GPTools.shift, direction='up')),
    ('test_shift_up_5.gp5', partial(GPTools.shift, direction='up', times=5)),
    ('test_shift_down_5.gp5', partial(GPTools.shift, direction='down', times=5)),

    ('test_duration_div_2.gp5', partial(GPTools.modify_duration, operation='div', factor=2)),
    ('test_duration_mul_2.gp5', partial(GPTools.modify_duration, operation='mul', factor=2)),
    ('test_duration_div_4.gp5', partial(GPTools.modify_duration, operation='div', factor=4)),

    ('test_stroke_down_32.gp5', partial(GPTools.stroke, direction='down', duration=32)),

    ('test_remove_stroke.gp5', partial(GPTools.remove, target='stroke')),
    ('test_remove_text.gp5', partial(GPTools.remove, target='text')),
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
