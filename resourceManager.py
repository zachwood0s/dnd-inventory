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


class CampaignDB:
    def __init__(self) -> None:
        self.items: Dict[str, character.Item] = {}
        self.abilities: Dict[str, character.Ability] = {}
        self.effects: Dict[str, character.Effect] = {}


class _SyncableData:
    def __init__(self) -> None:
        self.players: List[character.Character] = []
        self.chat_messages: List[packet.Packet] = []
        self.campaign_db: CampaignDB = CampaignDB()


class _Manager:
    def __init__(self) -> None:
        self.sync = _SyncableData()
        self.my_player_name: str = ''
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
        name = _manager.my_player_name
    return name


def get_campaign_db() -> CampaignDB:
    return _manager.sync.campaign_db


def set_campaign_db(db: CampaignDB):
    global _manager
    _manager.sync.campaign_db = db

    for h in _manager.character_update_handlers:
        h(None)


def has_ability(ability_id: str) -> bool:
    return ability_id in _manager.sync.campaign_db.abilities


def get_ability(ability_id: str) -> character.Ability:
    return _manager.sync.campaign_db.abilities[ability_id]


def has_item(item_id: str) -> bool:
    return item_id in _manager.sync.campaign_db.items


def get_item(item_id: str) -> character.Item:
    return _manager.sync.campaign_db.items[item_id]


def has_effect(effect_id: str) -> bool:
    return effect_id in _manager.sync.campaign_db.effects


def get_effect(effect_id: str) -> character.Effect:
    return _manager.sync.campaign_db.effects[effect_id]


def load_data(data, command: str):
    if type(data) is character.Character:
        data: character.Character
        set_my_player(data)

    elif type(data) is CampaignDB:
        data: CampaignDB
        set_campaign_db(data)


def load_character():
    import commandHandler
    global _manager
    new_char = character.DEFAULT_CHARACTER
    set_my_player(new_char)

    commandHandler.parse_command('load campaign')
    commandHandler.parse_command('load character')


def get_player(name: str) -> character.Character:
    global _manager
    name = _normalize_name(name)
    for p in _manager.sync.players:
        if p.get_stat(character.NAME) == name:
            return p

    raise ValueError(f"Character {name} does not exist")


def has_player(name: str) -> bool:
    try:
        get_player(name)
        return True
    except ValueError:
        return False


def get_my_player_name() -> str:
    global _manager
    return _manager.my_player_name


def set_player(packet_: packet.Packet, send_msg=True) -> None:
    global _manager

    assert packet_.type == packet.MessageType.UpdateCharacter, \
        f'Wrong packet type for set_player. Got {packet_.type}'
    assert type(packet_.data) is character.Character, f'Wrong type of data for set_player. Got {type(packet_.data)}'

    new_character: character.Character = packet_.data
    name = _normalize_name(new_character.get_stat(character.NAME))
    if not has_player(name):
        _manager.sync.players.append(new_character)
    else:
        for i in range(len(_manager.sync.players)):
            if _manager.sync.players[i].get_stat(character.NAME) == name:
                _manager.sync.players[i] = new_character

    _manager.update_handler(_manager.character_update_handlers, packet_)

    if send_msg:
        _manager.update_handler(_manager.general_msg_handlers, packet_)


def set_my_player(c: character.Character) -> None:
    global _manager
    _manager.my_player_name = c.get_stat(character.NAME)
    pkt = packet.make_character_packet(c, ME, '')
    set_player(pkt, send_msg=False)


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
    return list(_manager.sync.players)


def set_sync_data(packet_: packet.Packet):
    global _manager

    assert packet_.type == packet.MessageType.SyncDataResponse, \
        f'Wrong packet type for set_sync_data. Got {packet_.type}'
    assert type(packet_.data) is _SyncableData, f'Wrong type of data for set_sync_data. Got {type(packet_.data)}'

    old_sync = _manager.sync
    my_player = get_player(get_my_player_name())
    _manager.sync = packet_.data
    set_my_player(my_player)

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
