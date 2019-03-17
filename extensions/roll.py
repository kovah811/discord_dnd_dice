import random
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
            msg = (
                '  --  Natural 20 and natural 1!\n '
                'If rolling advantage, Crit!\n '
                'If rolling disadvantage, Fumble!'
            )
        elif crit is True:
            msg = '  --  Natural 20! (Crit)'
        elif fumble is True:
            msg = '  --  Natural 1! (Fumble)'

        return msg

    @commands.command(pass_context=True)
    async def d20(self, ctx, num_dice='1'):
        """Roll one (default) or more d20 dice.

        Examples:

           !d20             (1d20)
           !d20 2           (2d20)
           !d20 3           (3d20)

        :param ctx: the discord command context object
        :type ctx: discord.ext.commands.Context
        :param num_dice: Number of dice; 1 by default
        :type num_dice: str

        """

        name = ctx.message.author.display_name

        result = []
        crit = False
        fumble = False

        try:
            num_dice = int(num_dice)
        except ValueError:
            await self.client.say(
                f'{name} made an invalid roll: [{num_dice}] '
                f'is not a valid number of dice.'
            )
            return

        for i in range(num_dice):
            roll = random.randint(1, 20)
            if roll == 20:
                crit = True
            elif roll == 1:
                fumble = True
            result.append(roll)

        minmax_msg = self.get_d20_minmax_msg(crit, fumble)

        await self.client.say(
            f'{name} rolled a {num_dice}d20! The result was:\n '
            f'{result} {minmax_msg}'
        )

    @commands.command(pass_context=True)
    async def roll(self, ctx, *, args=None):
        """Roll the specified dice plus optional modifiers

        Examples:

           !roll d6            (one d6)
           !roll 2d8           (two d8s)
           !roll 3d10-1        (three d10s with a -1 on each roll)
           !roll (3d8)+3       (three d8s with a +3 to the total)
           !roll 2d8, 2d6      (comma-separated: two d8s and two d6s)
           !roll d20
           1d8                 (multi-line: one d20 and one d8)

        :param ctx: the discord command context object
        :type ctx: discord.ext.commands.Context
        :param args: Dice and modifiers to roll
        :type args: str

        """

        name = ctx.message.author.display_name

        if args is None:
            return

        args = args.replace(' ', '')
        results = []
        all_dice = []

        for dice in re.split('[,\n]', args):
            if len(dice) > 0:
                all_dice.append(dice)

        for dice in all_dice:
            single_mod = 0
            if re.match('\\(.*\\)', dice):
                dice, single_mod = dice[1:].split(')')

                try:
                    single_mod = int(single_mod) if single_mod else 0
                except ValueError:
                    await self.client.say(
                        f'{name} used an invalid modifier: [{single_mod}]'
                    )
                    return

            try:
                dice_parts, = re.findall(self.DICE_PATTERN, dice)
                num, sides, mod = dice_parts
            except ValueError:
                await self.client.say(f'{name} made an invalid roll: [{dice}]')
                return

            if sides not in self.VALID_DICE:
                await self.client.say(
                    f'Allowed dice are: {self.get_valid_dice()}'
                )
                return

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
                result = (
                    f'{name} rolled a {dice} with a '
                    f'{single_mod:+d} modifier! The result was:\n '
                    f'{roll}, Total: {sum(roll) + single_mod} '
                    f'({sum(roll)}{single_mod:+d})'
                )
            else:
                result = (
                    f'{name} rolled a {dice}! The result was:\n '
                    f'{roll}, Total: {sum(roll)}'
                )

            result += self.get_d20_minmax_msg(crit, fumble)

            results.append(result)

        await self.client.say('\n\n'.join(results))


def setup(client):
    client.add_cog(Roll(client))
