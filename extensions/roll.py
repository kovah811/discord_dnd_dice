import random
import re

from dataclasses import dataclass

import discord
from discord.ext import commands


@dataclass()
class Dice:
    """Represents a dice."""

    raw_quantity: str
    raw_sides: str
    raw_modifier: str
    raw_single_mod: str
    VALID_SIDES = [4, 6, 8, 10, 12, 20, 100]

    def __post_init__(self):
        try:
            self.quantity = int(self.raw_quantity) if self.raw_quantity else 1
        except ValueError:
            raise ValueError(
                f'[{self.raw_quantity}] quantity must be a number'
            )

        try:
            self.sides = int(self.raw_sides)
        except ValueError:
            raise ValueError(
                f'[{self.raw_sides}] number of sides must be a number'
            )

        try:
            self.modifier = int(self.raw_modifier) if self.raw_modifier else 0
        except ValueError:
            raise ValueError(f'[{self.raw_modifier}] is not a valid modifier.')

        try:
            self.single_mod = (
                int(self.raw_single_mod) if self.raw_single_mod else 0
            )
        except ValueError:
            raise ValueError(
                f'[{self.raw_single_mod}] is not a valid modifier.'
            )

        if self.quantity < 1:
            raise ValueError(
                f'[{self.quantity}] is not a valid number of dice.'
            )

        if self.sides not in self.VALID_SIDES:
            raise ValueError(
                f'[{self.raw}] Allowed dice are: {self.valid_dice}.'
            )

    @property
    def raw(self):
        """Return raw string representation of the dice."""

        return f'{self.raw_quantity}d{self.raw_sides}{self.raw_modifier or ""}'

    @property
    def valid_dice(self):
        """Return string representation of valid dice types."""

        return ', '.join(['d' + str(d) for d in self.VALID_SIDES])


@dataclass()
class DiceRoll:
    """Represents a dice roll."""

    base: int = 0
    modifier: int = 0
    crit: bool = False
    fumble: bool = False

    @property
    def total(self):
        """Returns the sum of the base roll value plus the modifier."""

        return self.base + self.modifier

    @property
    def raw(self):
        """Returns a breakdown of the roll before being totaled."""

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

    def __init__(self, client):
        self.client = client

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

        rolls = []

        try:
            dice = Dice(num_dice, '20', '', '')
        except ValueError as e:
            await self.client.say(f'{name} made an invalid roll: {e}')
            return

        for i in range(dice.quantity):
            dice_roll = DiceRoll()
            dice_roll.base = random.randint(1, dice.sides)
            if dice_roll.base == 20:
                dice_roll.crit = True
            elif dice_roll.base == 1:
                dice_roll.fumble = True
            rolls.append(dice_roll)

        raw_rolls = [roll.raw for roll in rolls]

        minmax_msg = self.get_d20_minmax_msg(rolls)

        await self.client.say(
            f'{name} rolled a {dice.quantity}d{dice.sides}! The result was:\n '
            f'{raw_rolls} {minmax_msg}'
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
            single_mod = ''
            if re.match('\\(.*\\)', dice_input):
                dice_input, single_mod = dice_input[1:].split(')')
                single_mod = single_mod if single_mod else ''

            try:
                dice_parts, = re.findall(self.DICE_PATTERN, dice_input)
                num, sides, mod = dice_parts
            except ValueError:
                await self.client.say(
                    f'{name} made an invalid roll: [{dice_input}]'
                )
                return

            try:
                dice = Dice(num, sides, mod, single_mod)
            except ValueError as e:
                await self.client.say(f'{name} made an invalid roll: {e}')
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

            raw_rolls = [roll.raw for roll in rolls]
            sum_rolls = sum([roll.total for roll in rolls])

            if dice.single_mod != 0:
                result = (
                    f'{name} rolled a {dice.raw} with a '
                    f'{dice.raw_single_mod} modifier! The result was:\n '
                    f'{raw_rolls}, Total: {sum_rolls + dice.single_mod} '
                    f'({sum_rolls}{dice.raw_single_mod})'
                )
            else:
                result = (
                    f'{name} rolled a {dice.raw}! The result was:\n '
                    f'{raw_rolls}, Total: {sum_rolls}'
                )

            result += self.get_d20_minmax_msg(rolls)

            results.append(result)

        await self.client.say('\n\n'.join(results))


def setup(client):
    client.add_cog(Roll(client))
