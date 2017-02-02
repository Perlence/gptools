import os

import attr
import click
import guitarpro
import psutil

INPLACE = object()


def find_clipboard():
    for process in psutil.process_iter():
        if process.name().lower() != 'gp5.exe':
            continue
        break
    else:
        raise click.ClickException('cannot get Guitar Pro 5 clipboard, is the process running?')

    exe_path = process.cmdline()[0]
    clipboard_path = os.path.join(os.path.dirname(exe_path), 'tmp', 'clipboard.tmp')
    return clipboard_path


@click.group()
@click.option('-i', '--input', metavar='FILE',
              default=find_clipboard,
              type=click.Path(exists=True),
              help='File to edit, taken from clipboard by default.')
@click.option('-o', '--output', metavar='FILE',
              type=click.Path(exists=True),
              help='Save edited file here, edit in-place by default.')
@click.pass_context
def cli(ctx, input, output):
    if not output:
        output = input
    ctx.obj = GPTools(input, output)


@cli.command()
@click.argument('direction', type=click.Choice(['up', 'down']))
@click.pass_obj
def shift(gptools, direction):
    gptools.parse()
    gptools.shift(direction)
    gptools.write()


@attr.s
class GPTools:
    input_file = attr.ib()
    output_file = attr.ib()

    song = attr.ib(init=False)

    def parse(self):
        self.song = guitarpro.parse(self.input_file)

    def write(self):
        guitarpro.write(self.song, self.output_file)

    def shift(self, direction):
        for track, _, _, beat in self.copied():
            for note in beat.notes:
                note_string = note.string - 1
                if direction == 'up':
                    if note_string == 0:
                        continue
                    string_interval = track.strings[note_string-1].value - track.strings[note_string].value
                    if note.value < string_interval:
                        continue
                    note.string -= 1
                    note.value -= string_interval
                elif direction == 'down':
                    if note_string == len(track.strings) - 1:
                        continue
                    string_interval = track.strings[note_string].value - track.strings[note_string+1].value
                    if note.value > 30 - string_interval:
                        continue
                    note.string += 1
                    note.value += string_interval

    def copied(self):
        for track in self.copied_tracks():
            for measure in self.copied_measures(track):
                for voice in measure.voices:
                    for beat in self.copied_beats(voice):
                        yield track, measure, voice, beat

    def copied_tracks(self):
        start = self.song.clipboard.startTrack - 1
        stop = self.song.clipboard.stopTrack
        return self.song.tracks[start:stop]

    def copied_measures(self, track):
        start = self.song.clipboard.startMeasure - 1
        stop = self.song.clipboard.stopMeasure
        return track.measures[start:stop]

    def copied_beats(self, voice):
        start = stop = None
        if self.song.clipboard.subBarCopy:
            start = self.song.clipboard.startBeat - 1
            stop = self.song.clipboard.stopBeat
        return voice.beats[start:stop]
