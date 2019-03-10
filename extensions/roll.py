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
