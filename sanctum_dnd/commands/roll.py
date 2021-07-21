import random
import re
from typing import List

import sanctum_dnd.commands.command_handler as command_handler
from sanctum_dnd import resource_manager, character
from sanctum_dnd.commands.help_text import *
from sanctum_dnd.packet import make_chat_packet

_DICE_REGEX = re.compile('([0-9]*)d([0-9]+)([+-]?)')


def parse_dice_amt(input_: str):
    res = _DICE_REGEX.match(input_)

    if res is None:
        raise ValueError(f'Dice format not recognized "{input_}"')

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


def perform_rolls(roll_count: int, dice_size: int, adv: int):
    roll1 = [random.randrange(1, dice_size + 1) for _ in range(roll_count)]
    roll2 = []
    if adv != 0:
        roll2 = [random.randrange(1, dice_size + 1) for _ in range(roll_count)]

    roll1_tot = sum(roll1)
    roll2_tot = sum(roll2) if roll2 else 0
    if adv == 0:
        total = roll1_tot
    elif adv < 0:
        # disadvantage
        total = min(roll1_tot, roll2_tot)
    else:
        # advantage
        total = max(roll1_tot, roll2_tot)

    roll1_str = ' + '.join(str(r) for r in roll1) + f' = {roll1_tot}'
    roll2_str = ' + '.join(str(r) for r in roll2) + f' = {roll2_tot}'
    return total, roll1_str, roll2_str


def adv_str(adv: int):
    if adv > 0:
        return '(adv)'
    elif adv < 0:
        return '(dis)'
    else:
        return ''


@command_handler.register_command('roll', n_args=1, help_text=f'roll {TRAIT}')
def roll2_command(command: List[str]):
    (_, trait) = command
    player = resource_manager.get_player(resource_manager.ME)
    # handle 'roll dex' style commands
    if trait[-1] == '+':
        adv = '+'
        trait = trait[:-1:]
    elif trait[-1] == '-':
        adv = '-'
        trait = trait[:-1:]
    else:
        adv = ''

    if trait in player.get_stat_names():
        new_command = [command[0], f'd20{adv}', resource_manager.ME, trait]
        roll3_command(new_command)

    else:
        # handle 'roll d20' style commands
        (_, dice_fmt) = command
        roll_amt, dice, adv = parse_dice_amt(dice_fmt)
        total, roll1, roll2 = perform_rolls(roll_amt, dice, adv)
        msg = [f'Rolling {dice_fmt}:', roll1]
        if adv:
            msg.extend([roll2, f'= {adv_str(adv)} {total}'])

        origin_command = ' '.join(command)
        pkt = make_chat_packet(msg, resource_manager.get_my_player_name(), origin_command)
        resource_manager.add_chat_message(pkt)


@command_handler.register_command('roll', n_args=3, help_text=f'roll {DICE_FMT} {PLAYER} {TRAIT}')
def roll3_command(command: List[str]):
    (_, dice_fmt, player, trait) = command
    p = resource_manager.get_player(player)
    stat = p.get_stat(trait)
    roll_amt, dice, adv = parse_dice_amt(dice_fmt)
    total, roll1, roll2 = perform_rolls(roll_amt, dice, adv)
    overall_total = total + stat
    msg = [f"Rolling {dice_fmt} on {p.get_stat(character.NAME)}'s {trait}:", roll1]
    if adv:
        msg.extend([roll2, f'= {adv_str(adv)} {total} + ({trait}) {stat} '])
    else:
        msg.append(f'= {total} + ({trait}) {stat}')

    msg.append(f'= {overall_total}')

    origin_command = ' '.join(command)
    pkt = make_chat_packet(msg, resource_manager.get_my_player_name(), origin_command)
    resource_manager.add_chat_message(pkt)
