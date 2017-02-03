import math

import attr
import click
from guitarpro.base import Duration, Beat, BeatStatus, BeatStroke, BeatStrokeDirection

from .tools import GPTools


def mount_note_tools(cli):
    @cli.group(help='Modify selected notes.')
    @click.pass_context
    def note(ctx):
        if isinstance(ctx.obj, GPTools):
            ctx.obj = NoteTools(*attr.astuple(ctx.obj))

    @note.group(help='Shift notes to upper or lower string.')
    def shift():
        pass

    @shift.command('up')
    @click.argument('amount', type=int)
    @click.pass_obj
    def shift_up(tools, amount):
        tools.parse()
        tools.shift('up', amount)
        tools.write()

    @shift.command('down')
    @click.argument('amount', type=int)
    @click.pass_obj
    def shift_down(tools, amount):
        tools.parse()
        tools.shift('down', amount)
        tools.write()

    @note.group(help='Multiply or divide duration by given factor.')
    def duration():
        pass

    @duration.command('mul')
    @click.argument('factor', type=int)
    @click.pass_obj
    def duration_mul(tools, factor):
        tools.parse()
        tools.modify_duration('mul', factor)
        tools.write()

    @duration.command('div')
    @click.argument('factor', type=int)
    @click.pass_obj
    def duration_div(tools, factor):
        tools.parse()
        tools.modify_duration('div', factor)
        tools.write()

    @note.group(help='Set or remove brush stroke.')
    def brush():
        pass

    @brush.command('up', help='Brush up.')
    @click.argument('duration', type=click.IntRange(4, 128), callback=validate_power_of_two)
    @click.pass_obj
    def brush_up(tools, duration):
        tools.parse()
        tools.brush('up', duration)
        tools.write()

    @brush.command('down', help='Brush down.')
    @click.argument('duration', type=click.IntRange(4, 128), callback=validate_power_of_two)
    @click.pass_obj
    def brush_down(tools, duration):
        tools.parse()
        tools.brush('down', duration)
        tools.write()

    @brush.command('rm', help='Remove brush stroke.')
    @click.pass_obj
    def brush_remove(tools, duration):
        tools.parse()
        tools.remove('brush')
        tools.write()

    @note.group('pick-stroke', help='Pick stroke up or down.')
    def pick_stroke():
        pass

    @pick_stroke.command('up')
    @click.pass_obj
    def pick_stroke_up(tools, duration):
        tools.parse()
        tools.pick_stroke('up', duration)
        tools.write()

    @pick_stroke.command('down')
    @click.pass_obj
    def pick_stroke_down(tools, duration):
        tools.parse()
        tools.pick_stroke('down', duration)
        tools.write()

    @pick_stroke.command('rm', help='Remove pick stroke.')
    @click.pass_obj
    def pick_stroke_remove(tools, duration):
        tools.parse()
        tools.remove('pick_stroke')
        tools.write()

    @note.group(help='Manipulate beat text.')
    def text():
        pass

    @text.command('rm', help='Remove text from selected beats.')
    @click.pass_obj
    def text_remove(tools):
        tools.parse()
        tools.remove('text')
        tools.write()

    @note.command(help='Replace all selected notes with rests.')
    @click.pass_obj
    def rest(tools):
        tools.parse()
        tools.replace_with_rests()
        tools.write()


def validate_power_of_two(ctx, param, value):
    log2 = math.log(value, 2)
    if math.floor(log2) != log2:
        raise click.BadParameter('must be a power of 2 integer')
    return value


@attr.s
class NoteTools(GPTools):
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

    def brush(self, direction, duration):
        bd = self.parse_stroke_direction(direction)
        for _, _, _, beat in self.selected():
            beat.effect.stroke.direction = bd
            beat.effect.stroke.value = duration

    def pick_stroke(self, direction):
        bd = self.parse_stroke_direction(direction)
        for _, _, _, beat in self.selected():
            beat.effect.pickStroke = bd

    def parse_stroke_direction(self, direction):
        if direction == 'up':
            return BeatStrokeDirection.down
        elif direction == 'down':
            return BeatStrokeDirection.up

    def remove(self, target):
        for _, _, _, beat in self.selected():
            if target == 'brush':
                beat.effect.stroke = BeatStroke()
            elif target == 'text':
                beat.text = None

    def replace_with_rests(self):
        for _, _, voice, beat in self.selected():
            i = voice.beats.index(beat)
            voice.beats[i] = Beat(duration=beat.duration, status=BeatStatus.rest)
