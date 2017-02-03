import attr
import click
from guitarpro.base import NoteType, NaturalHarmonic

from .tools import GPTools


def mount_effect_tools(cli):
    @cli.group(help='Modify effects of selected notes.')
    @click.pass_context
    def effect(ctx):
        if isinstance(ctx.obj, GPTools):
            ctx.obj = EffectTools(*attr.astuple(ctx.obj))

    @effect.group(help='Dead note.')
    def dead():
        pass

    @dead.command('set', help='Make selected notes dead.')
    @click.pass_obj
    def dead_set(tools):
        tools.parse()
        tools.set('dead')
        tools.write()

    @effect.group(help='Natural harmonic.')
    def harmonic():
        pass

    @harmonic.command('set', help='Make selected notes natural harmonics.')
    @click.pass_obj
    def harmonic_set(tools):
        tools.parse()
        tools.set('harmonic')
        tools.write()


class EffectTools(GPTools):
    def set(self, effect):
        for _, _, _, beat in self.selected():
            for note in beat.notes:
                if effect == 'dead':
                    note.type = NoteType.dead
                elif effect == 'harmonic':
                    note.type.effect.harmonic = NaturalHarmonic()
