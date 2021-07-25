import pathlib
from typing import List

import hjson

import sanctum_dnd.commands.command_handler as command_handler
from sanctum_dnd import resource_manager
from sanctum_dnd.settings import DEFAULT_CAMPAIGN_DB_PATH, DEFAULT_CHARACTER_PATH, DEFAULT_DATA_DIRECTORY
from sanctum_dnd.utils import ObjDecoder, Encoder


@command_handler.register_command('save', n_args=0, help_text='save')
def save_command(command_: List[str]):
    p = pathlib.Path('./' + DEFAULT_DATA_DIRECTORY)
    p.mkdir(parents=True, exist_ok=True)

    # Write character
    p = pathlib.Path('./' + DEFAULT_DATA_DIRECTORY) / DEFAULT_CHARACTER_PATH
    with p.open(mode='w') as f:
        player = resource_manager.get_player(resource_manager.get_my_player_name())
        hjson.dump(player, f, cls=Encoder)

    # Write Campaign
    p = pathlib.Path('./' + DEFAULT_DATA_DIRECTORY) / DEFAULT_CAMPAIGN_DB_PATH
    with p.open(mode='w') as f:
        campaign = resource_manager.get_campaign_db()
        hjson.dump(campaign, f, cls=Encoder)


@command_handler.register_command('load', n_args=1, help_text='load <data_file>')
def load_command(command: List[str]):
    (_, file_name) = command

    p = pathlib.Path('./') / DEFAULT_DATA_DIRECTORY / (file_name + '.hjson')
    with p.open(mode='r') as f:
        data = hjson.load(f, cls=ObjDecoder)
        resource_manager.load_data(data, ' '.join(command))
