import random
import re

from dataclasses import dataclass

import discord
from discord.ext import commands


@dataclass()
class Dice:
    raw_quantity: str
    raw_sides: str
    raw_modifier: str

    def __post_init__(self):
        self.quantity = int(self.raw_quantity) if self.raw_quantity else 1
        self.sides = int(self.raw_sides)
        self.modifier = int(self.raw_modifier) if self.raw_modifier else 0


@dataclass()
class DiceRoll:
    base: int = 0
    modifier: int = 0
    crit: bool = False
    fumble: bool = False

    def total(self):
        return self.base + self.modifier

    def raw(self):
        if self.modifier != 0:
            mod = f'{self.modifier:+d}'
        else:
            mod = ''
        return f'{str(self.base)}{mod}'


class Roll:
    """The Roll cog.

    :param client: the discord client object
    :type client: discord.ext.commands.Bot

    """

    DICE_PATTERN = re.compile(r"^(\d*)d(\d+)([-+]\d+)?$")
    VALID_DICE = [4, 6, 8, 10, 12, 20, 100]

    def __init__(self, client):
        self.client = client

    def get_valid_dice(self):
        """Return string representation of valid dice types."""

        return ', '.join(['d' + str(d) for d in self.VALID_DICE])

    @staticmethod
    def get_d20_minmax_msg(rolls):
        """Return a message to append to results if a d20 roll is 1 or 20.

        :param rolls: list of dice rolls
        :type rolls: list of DiceRoll

        """

        msg = ''
        crit = False
        fumble = False

        for roll in rolls:
            if roll.crit is True:
                crit = True
            elif roll.fumble is True:
                fumble = True

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
        all_dice_input = []

        for dice_input in re.split('[,\n]', args):
            if len(dice_input) > 0:
                all_dice_input.append(dice_input)

        for dice_input in all_dice_input:
            single_mod = 0
            if re.match('\\(.*\\)', dice_input):
                dice_input, single_mod = dice_input[1:].split(')')

                try:
                    single_mod = int(single_mod) if single_mod else 0
                except ValueError:
                    await self.client.say(
                        f'{name} used an invalid modifier: [{single_mod}]'
                    )
                    return

            try:
                dice_parts, = re.findall(self.DICE_PATTERN, dice_input)
                num, sides, mod = dice_parts
                dice = Dice(num, sides, mod)
            except ValueError:
                await self.client.say(
                    f'{name} made an invalid roll: [{dice_input}]'
                )
                return

            if dice.sides not in self.VALID_DICE:
                await self.client.say(
                    f'{name} made an invalid roll: [{dice_input}]\n'
                    f'Allowed dice are: {self.get_valid_dice()}'
                )
                return

            rolls = []

            for i in range(dice.quantity):
                dice_roll = DiceRoll(modifier=dice.modifier)
                dice_roll.base = random.randint(1, dice.sides)
                if dice.sides == 20 and dice_roll.base == 20:
                    dice_roll.crit = True
                elif dice.sides == 20 and dice_roll.base == 1:
                    dice_roll.fumble = True
                rolls.append(dice_roll)

            raw_rolls = [roll.raw() for roll in rolls]
            sum_rolls = sum([roll.total() for roll in rolls])

            if single_mod != 0:
                result = (
                    f'{name} rolled a {dice_input} with a '
                    f'{single_mod:+d} modifier! The result was:\n '
                    f'{raw_rolls}, Total: {sum_rolls + single_mod} '
                    f'({sum_rolls}{single_mod:+d})'
                )
            else:
                result = (
                    f'{name} rolled a {dice_input}! The result was:\n '
                    f'{raw_rolls}, Total: {sum_rolls}'
                )

            result += self.get_d20_minmax_msg(rolls)

            results.append(result)

        await self.client.say('\n\n'.join(results))


def setup(client):
    client.add_cog(Roll(client))
