import discord
import random
import re

from command_handler import CommandHandler


class DnDDice:
    def __init__(self, token):
        self.dice_pattern = re.compile(r"^(\d*)d(\d+)([-+]\d+)?$")
        self.valid_dice = ['4', '6', '8', '10', '12', '20', '100']
        self.modifiers = ['+', '-']
        self.numbers = ['1', '2', '3', '4', '5', '6', '7', '8', '9']

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

        self.ch.add_command({
            'trigger': '!roll',
            'function': self.roll_command,
            'args_num': 1,
            'req_args_num': 1,
            'args_name': ['Dice to roll, e.g. 2d6+1'],
            'description': 'Rolls the dice. Some examples:\n\n'
                           '\t\t!roll d6 \t(one d6)\n\n'
                           '\t\t!roll 2d8 \t(two d8s)\n\n'
                           '\t\t!roll 3d10-1 \t(three d10s with a -1 on each '
                           'roll)\n\n'
                           '\t\t!roll (3d8)+3 \t(three d8s with a +3 to the '
                           'total)\n\n'
                           '\t\t!roll 2d8, 2d6 \t(comma-separated: two d8s '
                           'and 2 '
                           'd6s)\n\n'
                           '\t\t!roll d20\n'
                           '\t\t1d8 \t\t(multiline: one d20 and one d8)\n'
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

            return ('{} rolled a {}d20! The result was: {}'.format(
                message.author.name, int(args[0]) if args else '', result))

        except Exception as e:
            print(e)
            return '{} made an invalid roll.'.format(message.author.name)

    def roll_command(self, message, client, args):
        try:
            results = []

            args = ''.join(args)
            print(args)

            all_dice = []

            for dice in re.split(',|\n', args):
                all_dice.append(dice)

            print(all_dice)

            for dice in all_dice:
                single_mod = 0
                if dice[0] == '(' and ')' in dice and dice[-1] != ')':
                    dice, single_mod = dice.replace('(', '').split(')')

                    if (single_mod[0] not in self.modifiers
                            or single_mod[1] not in self.numbers):
                        return '{} made an invalid roll.'.format(
                            message.author.name)

                dice_parts, = re.findall(self.dice_pattern, dice)
                num, sides, mod = dice_parts

                if sides not in self.valid_dice:
                    return ('Allowed dice are: {}'.format
                            (', '.join(['d' + d for d in self.valid_dice])))

                print(dice_parts, num, sides, mod)

                roll = []
                for i in range(int(num) if num else 1):
                    base = random.randint(1, int(sides))
                    roll.append(base + (int(mod) if mod else 0))

                if single_mod:
                    result = ('{} rolled a {} with a {} modifier! The result '
                              'was:\n {}, Total: {} ({}{})'
                              .format(message.author.name, dice, single_mod,
                                      roll, sum(roll) + int(single_mod),
                                      sum(roll), single_mod))
                else:
                    result = ('{} rolled a {}! The result was:\n'
                              '{}, Total: {}'.format(message.author.name,
                                                     dice, roll, sum(roll)))

                results.append(result)

            return '\n\n'.join(results)

        except Exception as e:
            print(e)
            return '{} made an invalid roll.'.format(message.author.name)
