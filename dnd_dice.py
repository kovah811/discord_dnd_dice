import discord
import random

from command_handler import CommandHandler


class DnDDice:
    def __init__(self, token):
        self.token = token
        self.client = discord.Client()
        self.ch = CommandHandler(self.client)
        self.on_ready = self.client.event(self.on_ready)
        self.on_message = self.client.event(self.on_message)

        self.ch.add_command({
            'trigger': '!commands',
            'function': self.commands_command,
            'args_num': 0,
            'req_args_num': 0,
            'args_name': [],
            'description': 'Prints a list of all the commands!'
        })

        self.ch.add_command({
            'trigger': '!d20',
            'function': self.d20_command,
            'args_num': 1,
            'req_args_num': 0,
            'args_name': ['Number of dice to roll'],
            'description': 'Rolls a d20!'
        })

        self.client.run(self.token)

    async def on_ready(self):
        try:
            print(self.client.user.name)
            print(self.client.user.id)
        except Exception as e:
            print(e)

    async def on_message(self, message):
        if message.author == self.client.user:
            pass
        else:
            try:
                await self.ch.command_handler(message)
            # message doesn't contain a command trigger
            except TypeError as e:
                pass
            # generic python error
            except Exception as e:
                print(e)

    def commands_command(self, message, client, args):
        try:
            count = 1
            coms = '**Commands List**\n'
            for command in self.ch.commands:
                coms += '{}.) {} : {}\n'.format(count,
                                                command['trigger'],
                                                command['description'])
                count += 1
            return coms
        except Exception as e:
            print(e)

    def d20_command(self, message, client, args):
        try:
            result = []
            for i in range(int(args[0]) if args else 1):
                result.append(random.randint(1, 20))
            return result
        except Exception as e:
            print(e)
