from typing import List, Callable
import packet
import character

ME = 'me'

CharacterHandler = Callable[[str, str, character.Character], None]
ChatHandler = Callable[[packet.Packet], None]


class _Manager:
    def __init__(self) -> None:
        self.players = {}
        self.my_player_name = None
        self.set_handlers = []
        self.character_update_handlers: List[CharacterHandler] = []
        self.chat_messages: List[packet.Packet] = []
        self.chat_update_handlers: List[ChatHandler] = []


_manager = _Manager()


def _normalize_name(name):
    global _manager
    if name == ME:
        name = _manager.my_player_name
    return name


def load_character():
    global _manager
    new_char = character.Character()
    new_char.name = 'Snapps Simmershell'
    new_char.xp = 40
    _manager.my_player_name = new_char.name
    _manager.players[new_char.name] = new_char


def get_player(name) -> character.Character:
    global _manager
    name = _normalize_name(name)
    return _manager.players[name]


def get_my_player_name() -> str:
    global _manager
    return _manager.my_player_name


def set_player(name, new_character, msg=None) -> None:
    global _manager
    name = _normalize_name(name)
    _manager.players[name] = new_character

    for h in _manager.character_update_handlers:
        h(msg, name, new_character)


def add_update_handler(handler: CharacterHandler):
    global _manager
    _manager.character_update_handlers.append(handler)


def add_chat_message(packet: packet.Packet):
    global _manager
    _manager.chat_messages.insert(0, packet)
    for h in _manager.chat_update_handlers:
        h(packet)


def get_chat_messages() -> List[packet.Packet]:
    global _manager
    return _manager.chat_messages


def add_chat_update_handler(handler: ChatHandler):
    global _manager
    _manager.chat_update_handlers.append(handler)


def get_players() -> List[character.Character]:
    global _manager
    return list(_manager.players.values())

