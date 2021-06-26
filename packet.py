import typing
import enum
from dataclasses import dataclass


class MessageType(enum.Enum):
    Action = 1
    Message = 1


@dataclass(frozen=True)
class Packet:
    type: MessageType
    recvr: str
    sender: str
    data: typing.List[str]
