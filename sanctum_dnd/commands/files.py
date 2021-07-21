import hjson
import pathlib

from sanctum_dnd import resource_manager, utils
import sanctum_dnd.commands.command_handler as command_handler

from typing import List

from sanctum_dnd.settings import DEFAULT_CAMPAIGN_DB_PATH, DEFAULT_CHARACTER_PATH, DEFAULT_DATA_DIRECTORY


class ObjDecoder(hjson.HjsonDecoder):
    def __init__(self, *args, **kwargs):
        del kwargs['object_pairs_hook']
        hjson.HjsonDecoder.__init__(self, object_hook=self.object_hook, *args, **kwargs)

    def object_hook(self, dct):
        if '__type__' in dct:
            cls = utils.import_string(dct['__type__'])
            new_obj = cls()
            new_obj.__dict__.update(dct)
            return new_obj
        else:
            return dct


class Encoder(hjson.HjsonEncoder):
    def default(self, obj):
        data = obj.__dict__
        data['__type__'] = utils.fullname(obj)
        return data


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
