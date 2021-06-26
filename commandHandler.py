# commands: roll <dice>, change <player> <stat> <value>, give <character> <itemname>
import typing
import re
import random

import npyscreen
import resourceManager

_DICE_REGEX = re.compile('([0-9]*)d([0-9]+)([+-]?)')


def parse_roll_command(command: typing.List[str]):
    def perform_rolls(roll_count, dice_size):
        for _ in range(roll_count):
            yield random.randrange(1, dice_size + 1)

    def parse_dice_amt(input_: str):
        res = _DICE_REGEX.match(input_)

        amt = 1
        if res.group(1) != '':
            amt = int(res.group(1))

        adv_group = res.group(3)
        if adv_group == '+':
            adv = 1
        elif adv_group == '-':
            adv = -1
        else:
            adv = 0

        dice = int(res.group(2))

        return amt, dice, adv

    argc = len(input)
    if argc != 2 and argc != 4:
        raise ValueError('Roll command malformed! Expected 1 or 3 arguments')

    player = None
    trait = None
    if len(input) > 2:
        player = input[2]
        trait = input[3]

    roll_amt, dice, adv = parse_dice_amt(input[1])

    if player is not None:
        # TODO: Lookup player and trait
        pass

    roll1 = list(perform_rolls(roll_amt, dice))

    if adv != 0:
        roll2 = list(perform_rolls(roll_amt, dice))


def parse_set_command(command: typing.List[str]):
    if len(command) != 4:
        raise ValueError('set command malformed! Expected 4 arguments')

    (_, name, stat, value,) = command
    player = resourceManager.get_player(name)
    old_value = player.get_stat(stat)
    player.set_stat(stat, value)
    resourceManager.set_player(name, player, f'Changed {name} {stat} from {old_value} to {value}')


COMMAND_MAPPING = {
    'roll': parse_roll_command,
    'set': parse_set_command,
}


def parse_command(input: str):
    input = input.lower()
    print(f'recieved command {input}')
    command = input.split(' ')

    handler = COMMAND_MAPPING.get(command[0])
    if handler is not None:
        handler(command)
