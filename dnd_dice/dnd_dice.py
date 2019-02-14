import discord
import random
import re

from dnd_dice.command_handler import CommandHandler


class DnDDice:
    """DnDDice bot.

    This bot provides a collection of commands to enable DnD dice rolling in a
    Discord channel.

    :param token: discord bot token to attach to
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
            'description': 'Rolls a d20. \n'
                           '\t\t!d20 <number of dice to roll> (default 1)'
        })

        self.ch.add_command({
            'trigger': '!roll',
            'function': self.roll_command,
            'args_num': 1,
            'req_args_num': 1,
            'args_name': ['Dice to roll'],
            'description': 'Rolls the dice.\n'
                           '\t\tExamples:\n'
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

    def get_valid_dice(self):
        """Return string representation of valid dice types."""

        return ', '.join(['d' + d for d in self.VALID_DICE])

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
        """Displays a list of valid commands.

        :param message: The discord message object
        :type message: discord.message.Message
        :param client: The discord client object
        :type client: discord.client.Client
        :param args: A list of arguments following the command trigger word
        :type args: list of str

        """

        try:
            count = 1
            commands = '**Commands List**\n'
            for command in self.ch.commands:
                commands += (f"{count}.) {command['trigger']} : "
                             f"{command['description']}\n")
                count += 1
            return commands
        except Exception as e:
            print(e)

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

    def d20_command(self, message, client, args):
        """Rolls one (default) or more d20 dice.

        :param message: The discord message object
        :type message: discord.message.Message
        :param client: The discord client object
        :type client: discord.client.Client
        :param args: A list of arguments following the command trigger word
        :type args: list of str

        """

        name = message.author.name

        result = []
        crit = False
        fumble = False

        try:
            num_dice = int(args[0]) if args else 1
        except ValueError:
            return (f'{name} made an invalid roll: '
                    f'[{args[0]}] is not a valid number of dice.')

        for i in range(num_dice):
            roll = random.randint(1, 20)
            if roll == 20:
                crit = True
            elif roll == 1:
                fumble = True
            result.append(roll)

        minmax_msg = self.get_d20_minmax_msg(crit, fumble)

        return (f'{name} rolled a {num_dice}d20!\n '
                f'The result was: {result} {minmax_msg}')

    def roll_command(self, message, client, args):
        """Rolls specified dice plus additional modifiers

        :param message: The discord message object
        :type message: discord.message.Message
        :param client: The discord client object
        :type client: discord.client.Client
        :param args: A list of arguments following the command trigger word
        :type args: list of str

        """

        name = message.author.name
        args = ''.join(args)
        results = []
        all_dice = []

        for dice in re.split('[,\n]', args):
            all_dice.append(dice)

        for dice in all_dice:
            single_mod = 0
            if re.match('\\(.*\\)', dice):
                dice, single_mod = dice[1:].split(')')

                try:
                    single_mod = int(single_mod) if single_mod else 0
                except ValueError:
                    return f'{name} used an invalid modifier: [{single_mod}]'

            try:
                dice_parts, = re.findall(self.DICE_PATTERN, dice)
                num, sides, mod = dice_parts
            except ValueError:
                return f'{name} made an invalid roll: [{dice}]'

            if sides not in self.VALID_DICE:
                return f'Allowed dice are: {self.get_valid_dice()}'

            mod = int(mod) if mod else 0

            roll = []
            crit = False
            fumble = False
            for i in range(int(num) if num else 1):
                base = random.randint(1, int(sides))
                if sides == '20' and base == 20:
                    crit = True
                elif sides == '20' and base == 1:
                    fumble = True
                roll.append(base + mod)

            if single_mod != 0:
                result = (f'{name} rolled a {dice} with a '
                          f'{single_mod:+d} modifier! The result was:\n'
                          f'{roll}, Total: {sum(roll) + single_mod} '
                          f'({sum(roll)}{single_mod:+d})')
            else:
                result = (f'{name} rolled a {dice}! The result was:\n'
                          f'{roll}, Total: {sum(roll)}')

            result += self.get_d20_minmax_msg(crit, fumble)

            results.append(result)

        return '\n\n'.join(results)
