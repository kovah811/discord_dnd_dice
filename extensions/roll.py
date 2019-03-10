import re

import discord
from discord.ext import commands


class Roll:
    """The Roll cog.

    :param client: the discord client object
    :type client: discord.ext.commands.Bot

    """

    DICE_PATTERN = re.compile(r"^(\d*)d(\d+)([-+]\d+)?$")
    VALID_DICE = ['4', '6', '8', '10', '12', '20', '100']

    def __init__(self, client):
        self.client = client

    async def on_message_delete(self, message):
        """The on_message_delete method"""

        await self.client.send_message(message.channel, 'Message deleted.')

    def get_valid_dice(self):
        """Return string representation of valid dice types."""

        return ', '.join(['d' + d for d in self.VALID_DICE])

    @staticmethod
    def get_d20_minmax_msg(crit, fumble):
        """Return a message to append to results if d20 roll is 1 or 20.

        :param crit: Whether or not a natural 20 was rolled
        :type crit: bool
        :param fumble: Whether or not a natural 1 was rolled
        :type fumble: bool

        """

        msg = ''

        if crit is True and fumble is True:
            msg = ('  --  Natural 20 and natural 1!\n '
                   'If rolling advantage, Crit!\n '
                   'If rolling disadvantage, Fumble!')
        elif crit is True:
            msg = '  --  Natural 20! (Crit)'
        elif fumble is True:
            msg = '  --  Natural 1! (Fumble)'

        return msg

    @commands.command(pass_context=True)
    async def d20(self, ctx):
        """The d20 command.

        :param ctx: the discord command context object
        :type ctx: discord.ext.commands.Context

        """

        await self.client.say('d20')

    @commands.command(pass_context=True)
    async def roll(self, ctx):
        """The roll command.

        :param ctx: the discord command context object
        :type ctx: discord.ext.commands.Context

        """

        await self.client.say('roll')


def setup(client):
    client.add_cog(Roll(client))
