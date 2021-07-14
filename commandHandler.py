from collections import defaultdict
from typing import Callable, List
from dataclasses import dataclass

import resourceManager
import packet
_REGISTERED_COMMANDS = defaultdict(dict)


@dataclass
class Command:
    func: Callable[[List[str]], None]
    help_text: str


def register_command(cmd_name: str, n_args: int, help_text: str):
    def wrapper(func: Callable[[List[str]], None]):
        commands = _REGISTERED_COMMANDS[cmd_name]
        assert n_args not in commands, f"Command with same name and n_args already registered: {cmd_name} {n_args}"
        commands[n_args] = Command(func, help_text)
        return func
    return wrapper


def parse_command(input_str: str):
    try:
        print(f'Received command {input_str}')
        input_str = input_str.strip()
        command = input_str.split(' ')

        commands = _REGISTERED_COMMANDS.get(command[0].lower())
        arg_cnt = len(command) - 1
        if commands is not None:
            handler = commands.get(arg_cnt)
            if handler is not None:
                try:
                    handler.func(command)
                except Exception as e:
                    print(e)
                    raise e
            else:
                msg = f'No command "{command[0]}" that takes {arg_cnt} arg(s) found\n'
                msg += 'Options:\n'
                for cmd in commands.values():
                    msg += cmd.help_text + '\n'

                raise ValueError(msg)
        else:
            raise ValueError(f'Command "{command[0]}" not found')

    except Exception as e:
        print(e)
        p = packet.Packet(packet.MessageType.Message, None, '', str(e))
        resourceManager.error(p)
