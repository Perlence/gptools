from functools import partial
import os

import pytest

from gptools.cli import GPTools

DIRNAME = os.path.dirname(__file__)


@pytest.mark.parametrize('test_tab, method', [
    ('test_shift_up.gp5', partial(GPTools.shift, direction='up')),
    ('test_shift_down.gp5', partial(GPTools.shift, direction='down')),
    ('test_shift_percussion.gp5', partial(GPTools.shift, direction='up')),
])
def test_tools(test_tab, method):
    gptools = GPTools(os.path.join(DIRNAME, test_tab), None, [1])
    gptools.parse()
    song = gptools.song
    source_track, expected_track = song.tracks

    method(gptools)

    for source_measure, expected_measure in zip(source_track.measures, expected_track.measures):
        for source_voice, expected_voice in zip(source_measure.voices, expected_measure.voices):
            for beat_number, (source_beat, expected_beat) in enumerate(zip(source_voice.beats, expected_voice.beats), start=1):
                print('measure', source_measure.number, 'beat', beat_number)
                assert source_beat == expected_beat
