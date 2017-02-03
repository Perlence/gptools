import os
import math

import attr
import click
import guitarpro
from guitarpro.base import Duration, BeatStroke, BeatStrokeDirection
import psutil

ALL = object()


class Range(click.ParamType):
    def convert(self, value, param, ctx):
        result = []
        parts = value.split(',')
        for part in parts:
            if not part:
                continue
            range_parts = part.split('-', 1)
            if len(range_parts) == 1:
                result.append(int(range_parts[0]))
            else:
                start, stop = map(int, range_parts)
                result.extend(list(range(start, stop+1)))
        return result


def validate_power_of_two(ctx, param, value):
    log2 = math.log(value, 2)
    if math.floor(log2) != log2:
        raise click.BadParameter('must be a power of 2 integer')
    return value


@click.group()
@click.option('-i', '--input', metavar='PATH', type=click.Path(exists=True),
              help='File to edit, edit Guitar Pro clipboard by default.')
@click.option('-o', '--output', metavar='PATH', type=click.Path(exists=True),
              help='Save edited file here, edit in-place by default.')
@click.option('-t', '--tracks', metavar='RANGE', type=Range(),
              help="Range of tracks to edit, e.g '1-4,6-7', default range is taken from clipboard.")
@click.option('-m', '--measures', metavar='RANGE', type=Range(),
              help='Range of measures to edit, default range is taken from clipboard.')
@click.option('-b', '--beats', metavar='RANGE', type=Range(),
              help='Range of beats to edit, default range is taken from clipboard.')
@click.pass_context
def cli(ctx, input, output, tracks, measures, beats):
    ctx.obj = GPTools(input, output, tracks, measures, beats)


@cli.group(help='Shift notes to upper or lower string.')
def shift():
    pass


@shift.command('up')
@click.argument('amount', type=int)
@click.pass_obj
def shift_up(gptools, amount):
    gptools.parse()
    gptools.shift('up', amount)
    gptools.write()


@shift.command('down')
@click.argument('amount', type=int)
@click.pass_obj
def shift_down(gptools, amount):
    gptools.parse()
    gptools.shift('down', amount)
    gptools.write()


@cli.group(help='Multiply or divide duration by given factor.')
def duration():
    pass


@duration.command('mul')
@click.argument('factor', type=int)
@click.pass_obj
def duration_mul(gptools, factor):
    gptools.parse()
    gptools.modify_duration('mul', factor)
    gptools.write()


@duration.command('div')
@click.argument('factor', type=int)
@click.pass_obj
def duration_div(gptools, factor):
    gptools.parse()
    gptools.modify_duration('div', factor)
    gptools.write()


@cli.group(help='Stroke beats up or down with given speed.')
def stroke():
    pass


@stroke.command('up')
@click.argument('duration', type=click.IntRange(4, 128), callback=validate_power_of_two)
@click.pass_obj
def stroke_up(gptools, duration):
    gptools.parse()
    gptools.stroke('up', duration)
    gptools.write()


@stroke.command('down')
@click.argument('duration', type=click.IntRange(4, 128), callback=validate_power_of_two)
@click.pass_obj
def stroke_down(gptools, duration):
    gptools.parse()
    gptools.stroke('down', duration)
    gptools.write()


@cli.command('rm', help='Remove some properties of a beat.')
@click.argument('target', type=click.Choice(['stroke', 'text']))
@click.pass_obj
def remove(gptools, target):
    gptools.parse()
    gptools.remove(target)
    gptools.write()


@attr.s
class GPTools:
    input_file = attr.ib()
    output_file = attr.ib()
    selected_track_numbers = attr.ib(default=None)
    selected_measure_numbers = attr.ib(default=None)
    selected_beat_numbers = attr.ib(default=None)

    song = attr.ib(init=False)

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

    def shift(self, direction, amount=1):
        for track, _, _, beat in self.selected():
            if track.isPercussionTrack:
                continue
            for note in beat.notes:
                if direction == 'up':
                    self.shift_up(track, note, amount)
                elif direction == 'down':
                    self.shift_down(track, note, amount)

    def shift_up(self, track, note, amount):
        for _ in range(amount):
            note_string = note.string - 1
            if note_string == 0:
                return
            string_interval = track.strings[note_string-1].value - track.strings[note_string].value
            if note.value < string_interval:
                return
            note.string -= 1
            note.value -= string_interval

    def shift_down(self, track, note, amount):
        for _ in range(amount):
            note_string = note.string - 1
            if note_string == len(track.strings) - 1:
                return
            string_interval = track.strings[note_string].value - track.strings[note_string+1].value
            if note.value > 30 - string_interval:
                return
            note.string += 1
            note.value += string_interval

    def modify_duration(self, operation, factor):
        def modifier(time):
            if operation == 'mul':
                return time * factor
            elif operation == 'div':
                return time // factor

        for _, _, _, beat in self.selected():
            time = beat.duration.time
            modified_time = modifier(time)
            beat.duration = Duration.fromTime(modified_time, minimum=Duration(Duration.sixtyFourth))

    def stroke(self, direction, duration):
        for _, _, _, beat in self.selected():
            if direction == 'up':
                bd = BeatStrokeDirection.down
            elif direction == 'down':
                bd = BeatStrokeDirection.up
            beat.effect.stroke.direction = bd
            beat.effect.stroke.value = duration

    def remove(self, target):
        for _, _, _, beat in self.selected():
            if target == 'stroke':
                beat.effect.stroke = BeatStroke()
            elif target == 'text':
                beat.text = None

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
