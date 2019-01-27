import discord
import random
import re

from command_handler import CommandHandler


class DnDDice:
    """DnDDice bot.

    This bot provides a collection of commands to enable DnD dice rolling in a
    Discord channel.

    :param token: Discord bot token to attach to
    :type token: str

    """

    DICE_PATTERN = re.compile(r"^(\d*)d(\d+)([-+]\d+)?$")
    VALID_DICE = ['4', '6', '8', '10', '12', '20', '100']

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
            'description': 'Prints a list of all the commands.'
        })

        self.ch.add_command({
            'trigger': '!d20',
            'function': self.d20_command,
            'args_num': 1,
            'req_args_num': 0,
            'args_name': ['Number of dice to roll'],
            'description': 'Rolls a d20.'
        })

        self.ch.add_command({
            'trigger': '!roll',
            'function': self.roll_command,
            'args_num': 1,
            'req_args_num': 1,
            'args_name': ['Dice to roll'],
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
        """on_ready method."""

        try:
            print(self.client.user.name)
            print(self.client.user.id)
        except Exception as e:
            print(e)

    async def on_message(self, message):
        """on_message method.

        :param message: The discord message object
        :type message: discord.message.Message

        """

        if message.author == self.client.user:
            pass
        else:
            try:
                await self.ch.command_handler(message)
            # message doesn't contain a command trigger
            except TypeError:
                pass
            # generic python error
            except Exception as e:
                print(e)

    def commands_command(self, message, client, args):
        """Displays a list of valid commands."""

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
        """Rolls one (default) or more d20 dice.

        :param message: The discord message object
        :type message: discord.message.Message
        :param args: A list of arguments following the command trigger word
        :type args: list

        """

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
        """Rolls specified dice plus additional modifiers

        :param message: The discord message object
        :type message: discord.message.Message
        :param args: A list of arguments following the command trigger word
        :type args: list

        """

        try:
            results = []

            args = ''.join(args)
            print(args)

            all_dice = []

            for dice in re.split('[,\n]', args):
                all_dice.append(dice)

            print(all_dice)

            for dice in all_dice:
                single_mod = 0
                if dice[0] == '(' and ')' in dice and dice[-1] != ')':
                    dice, single_mod = dice.replace('(', '').split(')')

                    try:
                        single_mod = int(single_mod)
                    except ValueError as e:
                        print(e)
                        return '{} entered an invalid modifier.'.format(
                            message.author.name)

                dice_parts, = re.findall(self.DICE_PATTERN, dice)
                num, sides, mod = dice_parts

                if sides not in self.VALID_DICE:
                    return ('Allowed dice are: {}'.format
                            (', '.join(['d' + d for d in self.VALID_DICE])))

                try:
                    if len(mod) > 0:
                        mod = int(mod)
                except ValueError as e:
                    print(e)
                    return '{} entered an invalid modifier.'.format(
                        message.author.name)

                print(dice_parts, num, sides, mod)

                roll = []
                for i in range(int(num) if num else 1):
                    base = random.randint(1, int(sides))
                    roll.append(base + (mod if mod else 0))

                if single_mod:
                    result = ('{} rolled a {} with a {} modifier! The result '
                              'was:\n {}, Total: {} ({}{:+d})'
                              .format(message.author.name, dice, single_mod,
                                      roll, sum(roll) + single_mod,
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
