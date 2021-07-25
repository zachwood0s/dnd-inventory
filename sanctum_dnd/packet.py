import typing
from dataclasses import dataclass


class MessageType:
    Action = 1  # data: str representing command
    Message = 2  # data: each line of message in a list
    UpdateCharacter = 3  # data: updated character
    SyncDataResponse = 4  # data: all syncable data
    SyncDataRequest = 5  # data: none
    ShowRequest = 6  # data: str of id to show


@dataclass(frozen=True)
class Packet:
    type: int = 0
    receiver: typing.Optional[str] = ''
    sender: str = ''
    data: typing.Any = ''
    origin_command: str = ''


def make_character_packet(player, me: str, origin_command: str) -> Packet:
    return Packet(MessageType.UpdateCharacter, None, me, player, origin_command)


def make_chat_packet(msg: typing.List[str], me: str, origin_command: str):
    return Packet(MessageType.Message, None, me, msg, origin_command)


def make_sync_request_packet(receiver: str, me: str, origin_command: str):
    return Packet(MessageType.SyncDataRequest, receiver, me, None, origin_command)


def make_sync_response_packet(me: str, origin_command: str, data):
    return Packet(MessageType.SyncDataResponse, None, me, data, origin_command)


def make_show_request_packet(me: str, receiver: str, origin_command: str, data):
    return Packet(MessageType.ShowRequest, receiver, me, data, origin_command)
