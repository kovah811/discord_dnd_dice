import discord
from discord.ext import commands


class Manage:
    """The management cog.

    :param client: the discord client object
    :type client: discord.ext.commands.Bot

    """

    def __init__(self, client):
        self.client = client

    async def on_ready(self):
        """The on_ready event."""
        
        print('Bot online.')

    async def on_message_delete(self, message):
        """The on_message_delete event."""

        await self.client.send_message(message.channel, 'Message deleted.')

    @commands.command(pass_context=True)
    async def load(self, ctx, extension):
        """Loads an extension/cog.

        :param ctx: the discord command context object
        :type ctx: discord.ext.commands.Context
        :param extension: extension/cog to load
        :type extension: str

        """

        author = ctx.message.author.display_name

        try:
            self.client.load_extension('.'.join(['extensions', extension]))
            print(f'{author} loaded {extension}.')
        except Exception as error:
            print(f'{author} tried to load {extension}, but {extension} '
                  f'could not be loaded. [{error}]')

    @commands.command(pass_context=True)
    async def unload(self, ctx, extension):
        """Unloads an extension/cog.

        Note: The 'manage' cog is not allowed to be unloaded.

        :param ctx: the discord command context object
        :type ctx: discord.ext.commands.Context
        :param extension: extension/cog to unload
        :type extension: str

        """

        author = ctx.message.author.display_name

        if extension == 'manage':
            print(f'{author} tried to unload management cog')
            await self.client.say('Can\'t remove management cog...')
            return

        try:
            self.client.unload_extension(extension)
            print(f'{author} unloaded {extension}.')
        except Exception as error:
            print(f'{author} tried to unload {extension}, but {extension} '
                  f'could not be unloaded. [{error}]')


def setup(client):
    """The setup function."""
    client.add_cog(Manage(client))
