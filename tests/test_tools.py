from functools import partial
import os

import guitarpro
import pytest

from gptools.cli import GPTools

DIRNAME = os.path.dirname(__file__)


@pytest.mark.parametrize('test_tab, method', [
    ('test_shift_up.gp5', partial(GPTools.shift, direction='up')),
    ('test_shift_down.gp5', partial(GPTools.shift, direction='down')),
])
def test_tools(test_tab, method):
    gptools = GPTools(os.path.join(DIRNAME, test_tab), None)
    gptools.parse()
    song = gptools.song
    source_track, expected_track = song.tracks
    song.clipboard = guitarpro.base.Clipboard(1, len(source_track.measures), source_track.number, source_track.number)

    method(gptools)

    for source_measure, expected_measure in zip(source_track.measures, expected_track.measures):
        print('Measure', source_measure.number)
        for source_voice, expected_voice in zip(source_measure.voices, expected_measure.voices):
            for source_beat, expected_beat in zip(source_voice.beats, expected_voice.beats):
                assert source_beat == expected_beat
