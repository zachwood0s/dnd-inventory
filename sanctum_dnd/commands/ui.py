from typing import List

import sanctum_dnd.commands.command_handler as command_handler
from sanctum_dnd import resource_manager, packet, character
from sanctum_dnd.commands.help_text import *
from sanctum_dnd.packet import make_chat_packet


@command_handler.register_command('chat', n_args=1, help_text=f'chat <msg>', var_args=True)
def chat_command(command: List[str]):
    origin_command = ' '.join(command)
    (_, *words) = command
    pkt = make_chat_packet([' '.join(words)], resource_manager.get_my_player_name(), origin_command)
    resource_manager.add_chat_message(pkt)


@command_handler.register_command('show', n_args=2, help_text=f'show {PLAYER} {ANY_ID}')
def remedy_command(command: List[str]):
    (_, name, id_) = command

    if name.lower() == 'all':
        recv = None
    else:
        player = resource_manager.get_player(name)
        recv = player.get_stat(character.NAME)

    origin_command = ' '.join(command)

    p = packet.make_show_request_packet(resource_manager.get_my_player_name(), recv, origin_command, id_)
    resource_manager.send_general_packet(p)
    if recv is None or recv == resource_manager.get_my_player_name():
        resource_manager.show_data(p)


@command_handler.register_command('view', n_args=1, help_text=f'show {PLAYER}')
def remedy_command(command: List[str]):
    (_, name) = command

    if resource_manager.has_player(name):
        resource_manager.set_viewed_player(name)
