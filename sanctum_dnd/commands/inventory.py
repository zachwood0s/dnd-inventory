from typing import List

import sanctum_dnd.commands.command_handler as command_handler
from sanctum_dnd import resource_manager, character
from sanctum_dnd.commands.help_text import *
from sanctum_dnd.packet import make_character_packet, make_chat_packet


def _update_player_and_chat(command, msg, player):
    origin_command = ' '.join(command)
    me = resource_manager.get_my_player_name()
    chat_pkt = make_chat_packet([msg], me, origin_command)
    character_pkt = make_character_packet(player, me, origin_command)
    resource_manager.set_player(character_pkt)
    resource_manager.add_chat_message(chat_pkt)


@command_handler.register_command('set', n_args=3, help_text=f'set {PLAYER} {TRAIT} {VALUE}')
def set_command(command: List[str]):
    (_, name, stat, value,) = command
    player = resource_manager.get_player(name)
    old_value = player.get_stat(stat)
    if stat == character.NAME:
        value = value.replace('_', ' ')
    player.set_stat(stat, value)

    msg = f"Changed {player.get_stat(character.NAME)}'s {stat} from {old_value} to {value}"
    if stat == character.NAME:
        if old_value == resource_manager.get_my_player_name():
            resource_manager.set_my_player(player)
        else:
            raise ValueError("Can't change the name of another character")
    _update_player_and_chat(command, msg, player)


@command_handler.register_command('create', n_args=2,
                                  help_text=f'create {OBJ_TYPE} <name> <description>', var_args=True)
def create_command(command: List[str]):
    (_, obj_type, name, *description) = command

    obj_id = name.lower()
    obj_name = name.replace('_', ' ')

    obj_class = {
        'item': character.Item,
        'ability': character.Ability,
        'effect': character.Effect
    }.get(obj_type)

    if obj_class is None:
        raise ValueError(f'Object type "{obj_type}" does not exist!')

    new_obj = obj_class(name=obj_name, desc=' '.join(description))

    campaign = resource_manager.get_campaign_db()
    if obj_type == 'item':
        campaign.items[obj_id] = new_obj
    elif obj_type == 'ability':
        campaign.abilities[obj_id] = new_obj
    else:
        campaign.effects[obj_id] = new_obj

    resource_manager.set_campaign_db(campaign)


# region Item Commands


@command_handler.register_command('give', n_args=2, help_text=f'give {PLAYER} {ITEM_ID}')
def give_command(command: List[str]):
    (_, name, item_id) = command
    player = resource_manager.get_player(name)
    if resource_manager.has_item(item_id):
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

    msg = f"{player.get_stat(character.NAME)} has received {resource_manager.get_item(item_id).name}"
    _update_player_and_chat(command, msg, player)


@command_handler.register_command('take', n_args=2, help_text=f'take {PLAYER} {PLAYERS_ITEM}')
def take_command(command: List[str]):
    (_, name, item_id) = command
    player = resource_manager.get_player(name)
    if item_id in player.items:
        if player.item_qtys[item_id] > 1:
            # If the player has more than one then simply decrease the amount
            player.item_qtys[item_id] -= 1
        else:
            # Otherwise we need to completely remove the item
            player.items.remove(item_id)
            del player.item_qtys[item_id]
            if item_id in player.active_items:
                player.active_items.remove(item_id)
    else:
        print("no no no item not exist in player")
        return

    msg = f"{player.get_stat(character.NAME)} has lost {resource_manager.get_item(item_id).name}"
    _update_player_and_chat(command, msg, player)


@command_handler.register_command('use', n_args=1, help_text=f'use {PLAYERS_ITEM}')
def use_command(command: List[str]):
    (_, item_id) = command
    player = resource_manager.get_player(resource_manager.get_my_player_name())
    if item_id in player.items:
        player.active_items.append(item_id)
    else:
        print("no no no item not exist in player")
        return

    msg = f"{player.get_stat(character.NAME)} has used {resource_manager.get_item(item_id).name}"
    _update_player_and_chat(command, msg, player)


@command_handler.register_command('unuse', n_args=1, help_text=f'unuse {PLAYERS_ITEM}')
def unuse_command(command: List[str]):
    (_, item_id) = command
    player = resource_manager.get_player(resource_manager.get_my_player_name())
    if item_id in player.items:
        try:
            player.active_items.remove(item_id)
        except ValueError:
            pass
    else:
        print("no no no item not exist in player")
        return

    msg = f"{player.get_stat(character.NAME)} has stopped using {resource_manager.get_item(item_id).name}"
    _update_player_and_chat(command, msg, player)


# endregion
# region Ability Commands


@command_handler.register_command('learn', n_args=2, help_text=f'learn {PLAYER} {ABILITY_ID}')
def learn_command(command: List[str]):
    (_, name, ability_id) = command
    player = resource_manager.get_player(name)
    if resource_manager.has_ability(ability_id):
        player.abilities.append(ability_id)
    else:
        print("no no no ability not exist")
        return

    msg = f"{player.get_stat(character.NAME)} has learned {resource_manager.get_ability(ability_id).name}"
    _update_player_and_chat(command, msg, player)


@command_handler.register_command('forget', n_args=2, help_text=f'forget {PLAYER} {PLAYERS_ABILITY}')
def forget_command(command: List[str]):
    (_, name, ability_id) = command
    player = resource_manager.get_player(name)
    if ability_id in player.abilities:
        player.abilities.remove(ability_id)
    else:
        print("no no no ability not exist in player")
        return

    msg = f"{player.get_stat(character.NAME)} has forgotten {resource_manager.get_ability(ability_id).name}"
    _update_player_and_chat(command, msg, player)


# endregion
# region Effect Commands


@command_handler.register_command('effect', n_args=2, help_text=f'effect {PLAYER} {EFFECT_ID}')
def effect_command(command: List[str]):
    (_, name, effect_id) = command
    player = resource_manager.get_player(name)
    if resource_manager.has_effect(effect_id):
        player.effects.append(effect_id)
    else:
        print("no no no effect not exist")
        print(resource_manager._manager.sync.campaign_db.effects)
        print(effect_id)
        return

    msg = f"{player.get_stat(character.NAME)} is now effected by {resource_manager.get_effect(effect_id).name}"
    _update_player_and_chat(command, msg, player)


@command_handler.register_command('remedy', n_args=2, help_text=f'remedy {PLAYER} {PLAYERS_EFFECT}')
def remedy_command(command: List[str]):
    (_, name, effect_id) = command
    player = resource_manager.get_player(name)
    if effect_id in player.effects:
        player.effects.remove(effect_id)
        print(player.effects)
    else:
        print("no no no effect not exist in player")
        return

    msg = f"{player.get_stat(character.NAME)} is no longer effected by {resource_manager.get_effect(effect_id).name}"
    _update_player_and_chat(command, msg, player)

# endregion
