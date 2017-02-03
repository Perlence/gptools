import os

import attr
import click
import guitarpro
import psutil

ALL = object()


@attr.s
class GPTools:
    input_file = attr.ib()
    output_file = attr.ib()
    selected_track_numbers = attr.ib(default=None)
    selected_measure_numbers = attr.ib(default=None)
    selected_beat_numbers = attr.ib(default=None)

    song = None

    def parse(self):
        if self.input_file is None:
            self.input_file = self.find_clipboard()
        if self.output_file is None:
            self.output_file = self.input_file

        self.song = guitarpro.parse(self.input_file)

        if self.selected_track_numbers is None:
            if self.song.clipboard is not None:
                self.selected_track_numbers = list(range(self.song.clipboard.startTrack, self.song.clipboard.stopTrack+1))
            else:
                self.selected_track_numbers = ALL
        if self.selected_measure_numbers is None:
            if self.song.clipboard is not None:
                self.selected_measure_numbers = list(range(self.song.clipboard.startMeasure, self.song.clipboard.stopMeasure+1))
            else:
                self.selected_measure_numbers = ALL
        if self.selected_beat_numbers is None:
            if self.song.clipboard is not None and self.song.clipboard.subBarCopy:
                self.selected_beat_numbers = list(range(self.song.clipboard.startBeat, self.song.clipboard.stopBeat+1))
            else:
                self.selected_beat_numbers = ALL

    def find_clipboard(self):
        for process in psutil.process_iter():
            if process.name().lower() != 'gp5.exe':
                continue
            break
        else:
            raise click.ClickException('cannot get Guitar Pro 5 clipboard, is the process running?')

        exe_path = process.cmdline()[0]
        clipboard_path = os.path.join(os.path.dirname(exe_path), 'tmp', 'clipboard.tmp')
        return clipboard_path

    def write(self):
        format = None if self.song.clipboard is None else 'tmp'
        guitarpro.write(self.song, self.output_file, format=format)

    def selected(self):
        for track in self.selected_tracks():
            for measure in self.selected_measures(track):
                for voice in measure.voices:
                    for beat in self.selected_beats(voice):
                        yield track, measure, voice, beat

    def selected_tracks(self):
        if self.selected_track_numbers is ALL:
            yield from self.song.tracks
            return
        for track in self.song.tracks:
            if track.number in self.selected_track_numbers:
                yield track

    def selected_measures(self, track):
        if self.selected_measure_numbers is ALL:
            yield from track.measures
            return
        for measure in track.measures:
            if measure.number in self.selected_measure_numbers:
                yield measure

    def selected_beats(self, voice):
        if self.selected_beat_numbers is ALL:
            yield from voice.beats
            return
        for number, beat in enumerate(voice.beats, start=1):
            if number in self.selected_beat_numbers:
                yield beat
