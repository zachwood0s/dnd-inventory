from typing import List
import random
import re
import hjson
import pathlib

import commandHandler
import resourceManager
import packet
import utils
import character

from packet import MessageType, make_character_packet, make_chat_packet

_DICE_REGEX = re.compile('([0-9]*)d([0-9]+)([+-]?)')


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


@commandHandler.register_command('roll', n_args=1, help_text='roll <dice_fmt>')
def roll2_command(command: List[str]):
    (_, dice_fmt) = command
    roll_amt, dice, adv = parse_dice_amt(dice_fmt)
    total, roll1, roll2 = perform_rolls(roll_amt, dice, adv)
    msg = [f'Rolling {dice_fmt}:', roll1]
    if adv:
        msg.extend([roll2, f'= {adv_str(adv)} {total}'])

    origin_command = ' '.join(command)
    pkt = make_chat_packet(msg, resourceManager.get_my_player_name(), origin_command)
    resourceManager.add_chat_message(pkt)


@commandHandler.register_command('roll', n_args=2, help_text='roll <player> <trait>')
def roll2_command(command: List[str]):
    (_, player, trait) = command
    if trait[-1] == '+':
        adv = '+'
        trait = trait[:-1:]
    elif trait[-1] == '-':
        adv = '-'
        trait = trait[:-1:]
    else:
        adv = ''
    new_command = [command[0], f'd20{adv}', player, trait]
    roll3_command(new_command)


@commandHandler.register_command('roll', n_args=3, help_text='roll <dice_fmt> <player> <trait>')
def roll3_command(command: List[str]):
    (_, dice_fmt, player, trait) = command
    p = resourceManager.get_player(player)
    stat = p.get_stat(trait)
    roll_amt, dice, adv = parse_dice_amt(dice_fmt)
    total, roll1, roll2 = perform_rolls(roll_amt, dice, adv)
    overall_total = total + stat
    msg = [f"Rolling {dice_fmt} on {player}'s {trait}:", roll1]
    if adv:
        msg.extend([roll2, f'= {adv_str(adv)} {total} + ({trait}) {stat} '])
    else:
        msg.append(f'= {total} + ({trait}) {stat}')

    msg.append(f'= {overall_total}')

    origin_command = ' '.join(command)
    pkt = make_chat_packet(msg, resourceManager.get_my_player_name(), origin_command)
    resourceManager.add_chat_message(pkt)


@commandHandler.register_command('set', n_args=3, help_text='set <player> <trait> <value>')
def set_command(command: List[str]):
    (_, name, stat, value,) = command
    player = resourceManager.get_player(name)
    old_value = player.get_stat(stat)
    player.set_stat(stat, value)

    msg = f"Changed {player.get_stat(character.NAME)}'s {stat} from {old_value} to {value}"
    me = resourceManager.get_my_player_name()
    origin_command = ' '.join(command)
    chat_pkt = make_chat_packet([msg], me, origin_command)
    character_pkt = make_character_packet(player, me, origin_command)

    resourceManager.set_player(character_pkt)
    resourceManager.add_chat_message(chat_pkt)


_DEFAULT_DATA_DIRECTORY = 'data'
_DEFAULT_CHARACTER_PATH = 'character.hjson'


class ObjDecoder(hjson.HjsonDecoder):
    def __init__(self, *args, **kwargs):
        del kwargs['object_pairs_hook']
        hjson.HjsonDecoder.__init__(self, object_hook=self.object_hook, *args, **kwargs)

    def object_hook(self, dct):
        if '__type__' in dct:
            cls = utils.import_string(dct['__type__'])
            new_obj = cls.__new__(cls)
            new_obj.__dict__ = dct
            return new_obj
        else:
            return dct


class Encoder(hjson.HjsonEncoder):
    def default(self, obj):
        data = obj.__dict__
        data['__type__'] = utils.fullname(obj)
        return data


@commandHandler.register_command('save', n_args=0, help_text='save')
def save_command(command_: List[str]):
    p = pathlib.Path('./' + _DEFAULT_DATA_DIRECTORY) / _DEFAULT_CHARACTER_PATH
    with p.open(mode='w') as f:
        player = resourceManager.get_player(resourceManager.get_my_player_name())
        hjson.dump(player, f, cls=Encoder)


@commandHandler.register_command('load', n_args=1, help_text='load <data_file>')
def load_command(command: List[str]):
    (_, file_name) = command

    p = pathlib.Path('./') / _DEFAULT_DATA_DIRECTORY / (file_name + '.hjson')
    with p.open(mode='r') as f:
        data = hjson.load(f, cls=ObjDecoder)

        if type(data) is character.Character:
            data: character.Character
            origin_command = ' '.join(command)
            pkt = make_character_packet(data, resourceManager.get_my_player_name(), origin_command)
            resourceManager.set_player(pkt)

