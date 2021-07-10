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
from settings import DEFAULT_CAMPAIGN_DB_PATH, DEFAULT_CHARACTER_PATH, DEFAULT_DATA_DIRECTORY

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


def _update_player_and_chat(command, msg, player):
    origin_command = ' '.join(command)
    me = resourceManager.get_my_player_name()
    chat_pkt = make_chat_packet([msg], me, origin_command)
    character_pkt = make_character_packet(player, me, origin_command)
    resourceManager.set_player(character_pkt)
    resourceManager.add_chat_message(chat_pkt)


@commandHandler.register_command('set', n_args=3, help_text='set <player> <trait> <value>')
def set_command(command: List[str]):
    (_, name, stat, value,) = command
    player = resourceManager.get_player(name)
    old_value = player.get_stat(stat)
    player.set_stat(stat, value)

    msg = f"Changed {player.get_stat(character.NAME)}'s {stat} from {old_value} to {value}"
    if stat == character.NAME:
        if old_value == resourceManager.get_my_player_name():
            resourceManager.set_my_player(player)
        else:
            raise ValueError("Can't change the name of another character")
    _update_player_and_chat(command, msg, player)


# region Item Commands
@commandHandler.register_command('give+', n_args=2, help_text='give+ <player> <item_id>')
def give_command(command: List[str]):
    (_, name, item_id) = command
    player = resourceManager.get_player(name)
    if resourceManager.has_item(item_id):
        if item_id in player.item_qtys:
            # The player already has one, increase the qty
            player.item_qtys[item_id] += 1
        else:
            # Need to add the item to the player
            player.items.append(item_id)
            player.item_qtys[item_id] = 1
    else:
        print("no no no item not exist")
        return

    msg = f"{player.get_stat(character.NAME)} has received {resourceManager.get_item(item_id).name}"
    _update_player_and_chat(command, msg, player)


@commandHandler.register_command('give', n_args=2, help_text='give <player> <item_id>')
def give_command(command: List[str]):
    (_, name, item_id) = command
    player = resourceManager.get_player(name)
    if resourceManager.has_item(item_id):
        if item_id in player.item_qtys:
            # The player already has one, increase the qty
            player.item_qtys[item_id] += 1
        else:
            # Need to add the item to the player
            player.items.append(item_id)
            player.item_qtys[item_id] = 1
    else:
        print("no no no item not exist")
        return

    msg = f"{player.get_stat(character.NAME)} has received {resourceManager.get_item(item_id).name}"
    _update_player_and_chat(command, msg, player)


@commandHandler.register_command('take', n_args=2, help_text='take <player> <item_id>')
def take_command(command: List[str]):
    (_, name, item_id) = command
    player = resourceManager.get_player(name)
    if item_id in player.items:
        if player.item_qtys[item_id] > 1:
            # If the player has more than one then simply decrease the amount
            player.item_qtys[item_id] -= 1
        else:
            # Otherwise we need to completely remove the item
            player.items.remove(item_id)
            del player.item_qtys[item_id]
            if item_id in  player.active_items:
                player.active_items.remove(item_id)
    else:
        print("no no no item not exist in player")
        return

    msg = f"{player.get_stat(character.NAME)} has lost {resourceManager.get_item(item_id).name}"
    _update_player_and_chat(command, msg, player)


@commandHandler.register_command('use', n_args=1, help_text='use <item_id>')
def use_command(command: List[str]):
    (_, item_id) = command
    player = resourceManager.get_player(resourceManager.get_my_player_name())
    if item_id in player.items:
        player.active_items.append(item_id)
    else:
        print("no no no item not exist in player")
        return

    msg = f"{player.get_stat(character.NAME)} has used {resourceManager.get_item(item_id).name}"
    _update_player_and_chat(command, msg, player)


@commandHandler.register_command('unuse', n_args=1, help_text='unuse <item_id>')
def unuse_command(command: List[str]):
    (_, item_id) = command
    player = resourceManager.get_player(resourceManager.get_my_player_name())
    if item_id in player.items:
        player.active_items.remove(item_id)
    else:
        print("no no no item not exist in player")
        return

    msg = f"{player.get_stat(character.NAME)} has stopped using {resourceManager.get_item(item_id).name}"
    _update_player_and_chat(command, msg, player)

# endregion

# region Ability Commands


@commandHandler.register_command('learn', n_args=2, help_text='learn <player> <ability_id>')
def learn_command(command: List[str]):
    (_, name, ability_id) = command
    player = resourceManager.get_player(name)
    if resourceManager.has_ability(ability_id):
        player.abilities.append(ability_id)
    else:
        print("no no no ability not exist")
        return

    msg = f"{player.get_stat(character.NAME)} has learned {resourceManager.get_ability(ability_id).name}"
    _update_player_and_chat(command, msg, player)


@commandHandler.register_command('forget', n_args=2, help_text='forget <player> <ability_id>')
def forget_command(command: List[str]):
    (_, name, ability_id) = command
    player = resourceManager.get_player(name)
    if ability_id in player.abilities:
        player.abilities.remove(ability_id)
    else:
        print("no no no ability not exist in player")
        return

    msg = f"{player.get_stat(character.NAME)} has forgotten {resourceManager.get_ability(ability_id).name}"
    _update_player_and_chat(command, msg, player)
# endregion

# region Effect Commands


@commandHandler.register_command('effect', n_args=2, help_text='effect <player> <effect_id>')
def effect_command(command: List[str]):
    (_, name, effect_id) = command
    player = resourceManager.get_player(name)
    if resourceManager.has_effect(effect_id):
        player.effects.append(effect_id)
    else:
        print("no no no effect not exist")
        print(resourceManager._manager.sync.campaign_db.effects)
        print(effect_id)
        return

    msg = f"{player.get_stat(character.NAME)} is now effected by {resourceManager.get_effect(effect_id).name}"
    _update_player_and_chat(command, msg, player)


@commandHandler.register_command('remedy', n_args=2, help_text='remedy <player> <effect_id>')
def remedy_command(command: List[str]):
    (_, name, effect_id) = command
    player = resourceManager.get_player(name)
    if effect_id in player.effects:
        player.effects.remove(effect_id)
        print(player.effects)
    else:
        print("no no no effect not exist in player")
        return

    msg = f"{player.get_stat(character.NAME)} is no longer effected by {resourceManager.get_effect(effect_id).name}"
    _update_player_and_chat(command, msg, player)


@commandHandler.register_command('show', n_args=2, help_text='show <player> <effect_id>')
def remedy_command(command: List[str]):
    (_, name, id_) = command

    if name.lower() == 'all':
        print('hi')
        recv = None
    else:
        print('by')
        player = resourceManager.get_player(name)
        recv = player.get_stat(character.NAME)

    origin_command = ' '.join(command)

    p = packet.make_show_request_packet(resourceManager.get_my_player_name(), recv, origin_command, id_)
    resourceManager.send_general_packet(p)
    if recv is None or recv == resourceManager.get_my_player_name():
        resourceManager.show_data(p)


# endregion


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
    # Write character
    p = pathlib.Path('./' + DEFAULT_DATA_DIRECTORY) / DEFAULT_CHARACTER_PATH
    with p.open(mode='w') as f:
        player = resourceManager.get_player(resourceManager.get_my_player_name())
        hjson.dump(player, f, cls=Encoder)

    # Write Campaign
    p = pathlib.Path('./' + DEFAULT_DATA_DIRECTORY) / DEFAULT_CAMPAIGN_DB_PATH
    with p.open(mode='w') as f:
        campaign = resourceManager.get_campaign_db()
        hjson.dump(campaign, f, cls=Encoder)


@commandHandler.register_command('load', n_args=1, help_text='load <data_file>')
def load_command(command: List[str]):
    (_, file_name) = command

    p = pathlib.Path('./') / DEFAULT_DATA_DIRECTORY / (file_name + '.hjson')
    with p.open(mode='r') as f:
        data = hjson.load(f, cls=ObjDecoder)
        resourceManager.load_data(data, ' '.join(command))

