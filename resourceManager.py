from typing import List, Callable, Dict
from functools import partial
import packet
import character
import threading

ME = 'me'

CharacterHandler = Callable[[packet.Packet], None]
ChatHandler = Callable[[packet.Packet], None]
MessageHandler = Callable[[packet.Packet], None]
ConnectedHandler = Callable[[bool], None]


class _SyncableData:
    def __init__(self) -> None:
        self.players: Dict[str, character.Character] = {}
        self.chat_messages: List[packet.Packet] = []


class _Manager:
    def __init__(self) -> None:
        self.sync = _SyncableData()
        self.my_player: character.Character = None
        self.set_handlers = []
        self.character_update_handlers: List[CharacterHandler] = []
        self.chat_update_handlers: List[ChatHandler] = []
        self.connected_handlers: List[ConnectedHandler] = []
        self.general_msg_handlers: List[MessageHandler] = []
        self.connected = False

    def update_handler(self, handlers, msg):
        for h in handlers:
            h(msg)


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
    new_char.effects.append(character.Effect(name='shid', desc='piss', stats=character.EffectStats()))
    _manager.my_player = new_char
    _manager.sync.players[new_char.get_stat(character.NAME)] = new_char


def get_player(name: str) -> character.Character:
    global _manager
    name = _normalize_name(name)
    return _manager.sync.players[name]


def get_my_player_name() -> str:
    global _manager
    return _manager.my_player.get_stat(character.NAME)


def set_player(packet_: packet.Packet, send_msg=True) -> None:
    global _manager

    assert packet_.type == packet.MessageType.UpdateCharacter, \
        f'Wrong packet type for set_player. Got {packet_.type}'
    assert type(packet_.data) is character.Character, f'Wrong type of data for set_player. Got {type(packet_.data)}'

    new_character: character.Character = packet_.data
    name = _normalize_name(new_character.get_stat(character.NAME))
    _manager.sync.players[name] = new_character

    _manager.update_handler(_manager.character_update_handlers, packet_)

    if send_msg:
        _manager.update_handler(_manager.general_msg_handlers, packet_)


def add_connected_update_handler(handler: ConnectedHandler) -> ConnectedHandler:
    global _manager
    _manager.connected_handlers.append(handler)
    return handler


def add_character_update_handler(handler: CharacterHandler) -> CharacterHandler:
    global _manager
    _manager.character_update_handlers.append(handler)
    return handler


def add_message_handler(handler: MessageHandler) -> MessageHandler:
    global _manager
    _manager.general_msg_handlers.append(handler)
    return handler


def add_chat_message(packet_: packet.Packet, send_msg=True):
    global _manager

    assert packet_.type == packet.MessageType.Message, f'Wrong packet type for chat_message. Got {packet_.type}'
    assert type(packet_.data) is list, f'Wrong type of data for chat_message. Got {type(packet_.data)}'

    _manager.sync.chat_messages.insert(0, packet_)
    _manager.update_handler(_manager.chat_update_handlers, packet_)
    if send_msg:
        _manager.update_handler(_manager.general_msg_handlers, packet_)


def get_chat_messages() -> List[packet.Packet]:
    global _manager
    return _manager.sync.chat_messages


def add_chat_update_handler(handler: ChatHandler) -> ChatHandler:
    global _manager
    _manager.chat_update_handlers.append(handler)
    return handler


def get_players() -> List[character.Character]:
    global _manager
    return list(_manager.sync.players.values())


def set_sync_data(packet_: packet.Packet):
    global _manager

    assert packet_.type == packet.MessageType.SyncDataResponse, \
        f'Wrong packet type for set_sync_data. Got {packet_.type}'
    assert type(packet_.data) is _SyncableData, f'Wrong type of data for set_sync_data. Got {type(packet_.data)}'

    old_sync = _manager.sync
    _manager.sync = packet_.data
    my_player = get_my_player_name()

    if my_player not in _manager.sync.players:
        # set the player back if it wasn't overwritten by the synced data
        _manager.sync.players[my_player] = old_sync.players[my_player]

    _manager.update_handler(_manager.chat_update_handlers, packet_)
    _manager.update_handler(_manager.character_update_handlers, packet_)


def handle_sync_request(packet_: packet.Packet, origin_command=''):
    pkt = packet.make_sync_response_packet(get_my_player_name(), origin_command, _manager.sync)
    _manager.update_handler(_manager.general_msg_handlers, pkt)


incoming_lock = threading.Lock()

_PKT_HANDLERS = {
    packet.MessageType.Message: partial(add_chat_message, send_msg=False),
    packet.MessageType.UpdateCharacter: partial(set_player, send_msg=False),
    packet.MessageType.SyncDataRequest: handle_sync_request,
    packet.MessageType.SyncDataResponse: set_sync_data
}


def handle_incoming(pkt: packet.Packet):
    """
    Handles the incoming messages for this client
    """
    with incoming_lock:
        handler = _PKT_HANDLERS.get(pkt.type)
        print(f'Handling message of type {pkt.type} from {pkt.sender} with data {pkt.data}')
        if handler is not None:
            if pkt.receiver is None or pkt.receiver == get_my_player_name():
                handler(pkt)
