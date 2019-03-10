import discord
from discord.ext import commands


class Roll:
    def __init__(self, client):
        self.client = client

    async def on_message_delete(self, message):
        await self.client.send_message(message.channel, 'Message deleted.')

    @commands.command()
    async def d20(self):
        await self.client.say('d20')

    @commands.command()
    async def roll(self):
        await self.client.say('roll')


def setup(client):
    client.add_cog(Roll(client))
