from collections import defaultdict
from typing import Callable, List, Optional, Dict
from dataclasses import dataclass

from sanctum_dnd import resource_manager, packet

_REGISTERED_COMMANDS = defaultdict(dict)
_VAR_ARG_COMMANDS = defaultdict(list)


@dataclass
class Command:
    func: Callable[[List[str]], None]
    help_text: str
    var_args: bool
    arg_cnt: int


def get_command_list(name: str) -> Optional[Dict[int, Command]]:
    return _REGISTERED_COMMANDS.get(name, None)


def get_all_command_names() -> List[str]:
    return list(_REGISTERED_COMMANDS.keys())


def register_command(cmd_name: str, n_args: int, help_text: str, var_args: bool = False):
    def wrapper(func: Callable[[List[str]], None]):
        commands = _REGISTERED_COMMANDS[cmd_name]
        assert n_args not in commands, f"Command with same name and n_args already registered: {cmd_name} {n_args}"
        cmd = Command(func, help_text, var_args, n_args)
        commands[n_args] = cmd
        if var_args:
            _VAR_ARG_COMMANDS[cmd_name].append(cmd)
            _VAR_ARG_COMMANDS[cmd_name].sort(key=lambda x: x.arg_cnt, reverse=True)
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
                handler.func(command)
            elif command[0] in _VAR_ARG_COMMANDS:
                var_args_commands = _VAR_ARG_COMMANDS[command[0]]
                # Find the command with a required arg count less than the one provided
                cmd = next((x for x in var_args_commands if x.arg_cnt <= arg_cnt), None)
                if cmd is not None:
                    cmd.func(command)
                else:
                    msg = f'No var arg command "{command[0]}" that takes {arg_cnt} arg(s) found\n'
                    msg += 'Options:\n'
                    for cmd in var_args_commands:
                        msg += cmd.help_text + '\n'

                    raise ValueError(msg)
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
        resource_manager.error(p)
