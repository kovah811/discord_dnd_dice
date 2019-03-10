from os import listdir
from os.path import isfile, join

import discord
from discord.ext import commands

TOKEN = ''
client = commands.Bot(command_prefix=['!', '.'])


def get_extensions(extensions_dir):
    extensions = []
    for file in listdir(extensions_dir):
        if isfile(join(extensions_dir, file)):
            extensions.append('.'.join([extensions_dir,
                                        file.replace('.py', '')]))
    return extensions


@client.event
async def on_ready():
    print('Bot online.')


if __name__ == '__main__':
    for extension in get_extensions('extensions'):
        try:
            client.load_extension(extension)
        except Exception as error:
            print(f'{extension} cannot be loaded. [{error}]')

    client.run(TOKEN)
