import click

from .effect import mount_effect_tools
from .note import mount_note_tools
from .tools import GPTools


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


mount_note_tools(cli)
mount_effect_tools(cli)
