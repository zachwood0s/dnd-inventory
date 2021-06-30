from typing import List, Callable, Dict
import packet
import character
import threading

ME = 'me'

CharacterHandler = Callable[[packet.Packet], None]
ChatHandler = Callable[[packet.Packet], None]
ConnectedHandler = Callable[[bool], None]


class _Manager:
    def __init__(self) -> None:
        self.players: Dict[str, character.Character] = {}
        self.my_player: character.Character = None
        self.set_handlers = []
        self.character_update_handlers: List[CharacterHandler] = []
        self.chat_messages: List[packet.Packet] = []
        self.chat_update_handlers: List[ChatHandler] = []
        self.connected_handlers: List[ConnectedHandler] = []
        self.connected = False


_manager = _Manager()


def set_is_connected(connected: bool):
    global _manager
    _manager.connected = connected
    print('Connected: ', connected)
    for h in _manager.connected_handlers:
        h(connected)


def get_is_connected() -> bool:
    return _manager.connected


def _normalize_name(name: str):
    global _manager
    if name == ME:
        name = _manager.my_player.get_stat(character.NAME)
    return name


def load_character():
    import uuid
    global _manager
    new_char = character.Character()
    new_char.set_stat(character.NAME, 'Snapps Simmershell' + str(uuid.uuid4()))
    _manager.my_player = new_char
    _manager.players[new_char.get_stat(character.NAME)] = new_char


def get_player(name: str) -> character.Character:
    global _manager
    name = _normalize_name(name)
    return _manager.players[name]


def get_my_player_name() -> str:
    global _manager
    return _manager.my_player.get_stat(character.NAME)


def set_player(packet_: packet.Packet) -> None:
    global _manager

    assert packet_.type == packet.MessageType.UpdateCharacter, \
        f'Wrong packet type for set_player. Got {packet_.type}'
    assert type(packet_.data) is character.Character, f'Wrong type of data for set_player. Got {type(packet_.data)}'

    new_character: character.Character = packet_.data
    name = _normalize_name(new_character.get_stat(character.NAME))
    _manager.players[name] = new_character

    for h in _manager.character_update_handlers:
        h(packet_)


def add_connected_update_handler(handler: ConnectedHandler) -> ConnectedHandler:
    global _manager
    _manager.connected_handlers.append(handler)
    return handler


def add_character_update_handler(handler: CharacterHandler) -> CharacterHandler:
    global _manager
    _manager.character_update_handlers.append(handler)
    return handler


def add_chat_message(packet_: packet.Packet):
    global _manager

    assert packet_.type == packet.MessageType.Message, f'Wrong packet type for chat_message. Got {packet_.type}'
    assert type(packet_.data) is list, f'Wrong type of data for chat_message. Got {type(packet_.data)}'

    _manager.chat_messages.insert(0, packet_)
    for h in _manager.chat_update_handlers:
        h(packet_)


def get_chat_messages() -> List[packet.Packet]:
    global _manager
    return _manager.chat_messages


def add_chat_update_handler(handler: ChatHandler) -> ChatHandler:
    global _manager
    _manager.chat_update_handlers.append(handler)
    return handler


def get_players() -> List[character.Character]:
    global _manager
    return list(_manager.players.values())


incoming_lock = threading.Lock()

_PKT_HANDLERS = {
    packet.MessageType.Message: add_chat_message,
    packet.MessageType.UpdateCharacter: set_player,
}


def handle_incoming(pkt: packet.Packet):
    """
    Handles the incoming messages for this client
    """
    with incoming_lock:
        handler = _PKT_HANDLERS.get(pkt.type)
        if handler is not None:
            handler(pkt)
