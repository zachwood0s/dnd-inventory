import textwrap

import npyscreen
from sanctum_dnd import resource_manager, character, settings
from sanctum_dnd.ui import stat_box
from sanctum_dnd.utils import columns


class TraitGrid(npyscreen.BoxTitle):
    _contained_widget = npyscreen.GridColTitles


class LogEntry(npyscreen.Popup):
    DEFAULT_LINES = settings.POPUP_HEIGHT
    DEFAULT_COLUMNS = settings.POPUP_WIDTH
    SHOW_ATX = settings.POPUP_MARGIN_X
    SHOW_ATY = settings.POPUP_MARGIN_Y
    DESC_HEIGHT = 12

    def __init__(self, log_item: str, **kwargs):
        self.log_item = log_item
        super().__init__(**kwargs)

    def create(self):
        self.name = "Log Entry"

        if resource_manager.has_item(self.log_item):
            self.create_item(resource_manager.get_item(self.log_item))
        elif resource_manager.has_effect(self.log_item):
            self.create_effect(resource_manager.get_effect(self.log_item))
        elif resource_manager.has_ability(self.log_item):
            self.create_ability(resource_manager.get_ability(self.log_item))

    def create_item(self, item: character.Item):
        y, x = self.useable_space()
        self.name_obj = self.add(npyscreen.BoxTitle, editable=False, name="Name", values=[item.name],
                                 max_height=4, footer=f"ID: {self.log_item}")
        desc_lines = [s for line in textwrap.wrap(item.desc, self.name_obj.width - 10) for s in line.splitlines()]
        self.desc_obj = self.add(npyscreen.BoxTitle, editable=False, name='Desc', values=desc_lines,
                                 max_height=self.DESC_HEIGHT)

        grid_args = {'column_percents': []}
        self.actives_obj = self.add(stat_box.StatGridBox, name='Actives', max_height=10,
                                    contained_widget_arguments=grid_args)
        self.actives_obj.create(character.active_selector(item), 'effects')
        self.actives_obj.update_rows(None)
        self.actives_obj.resize()

        self.passives_obj = self.add(stat_box.StatGridBox, name='Passives', max_height=10,
                                     contained_widget_arguments=grid_args)
        self.passives_obj.create(lambda: item.passives, 'effects')
        self.passives_obj.update_rows(None)
        self.passives_obj.resize()

    def create_effect(self, effect: character.Effect):
        y, x = self.useable_space()
        self.name_obj = self.add(npyscreen.BoxTitle, editable=False, name="Name", values=[effect.name],
                                 max_height=4, footer=f"ID: {self.log_item}")
        desc_lines = [s for line in textwrap.wrap(effect.desc, self.name_obj.width - 10) for s in line.splitlines()]
        self.desc_obj = self.add(npyscreen.BoxTitle, editable=False, name='Desc', values=desc_lines,
                                 max_height=self.DESC_HEIGHT)

        grid_args = {'col_titles': ['Trait', 'Value'],
                     'columns': 2,
                     'values': []}
        self.traits_obj = self.add(TraitGrid, editable=False, name='Traits',
                                   contained_widget_arguments=grid_args)
        self.traits_obj.entry_widget.values = []
        for t in effect.traits:
            front = '+' if t.amt > 0 else ''
            self.traits_obj.entry_widget.values.append([t.name, f'{front}{t.amt}'])

        self.traits_obj.resize()

    def create_ability(self, ability: character.Ability):
        y, x = self.useable_space()
        self.name_obj = self.add(npyscreen.BoxTitle, editable=False, name="Name", values=[ability.name],
                                 max_height=4, footer=f"ID: {self.log_item}")
        desc_lines = [s for line in textwrap.wrap(ability.desc, self.name_obj.width - 10) for s in line.splitlines()]
        self.desc_obj = self.add(npyscreen.BoxTitle, editable=False, name='Desc', values=desc_lines,
                                 max_height=self.DESC_HEIGHT)

        self.statObjs = {}
        stat_padding = 3
        stat_width, stat_xs = columns(x, len(ability.stats), stat_padding)
        stat_y = 18
        stat_height = 4
        for idx, (stat, val) in enumerate(ability.stats.items()):
            word = ' '.join(map(str.capitalize, stat.split('_')))
            self.statObjs[stat] = self.add(stat_box.StatBox, name=word, values=[str(val)], color='VERYGOOD',
                                           editable=False,
                                           max_width=stat_width, max_height=stat_height, relx=stat_xs[idx], rely=stat_y)

        grid_args = {'column_percents': []}
        self.actives_obj = self.add(stat_box.StatGridBox, name='Actives', max_height=10,
                                    contained_widget_arguments=grid_args)
        self.actives_obj.create(lambda: ability.actives, 'effects')
        self.actives_obj.update_rows(None)
        self.actives_obj.resize()

        self.passives_obj = self.add(stat_box.StatGridBox, name='Passives', max_height=10,
                                     contained_widget_arguments=grid_args)
        self.passives_obj.create(lambda: ability.passives, 'effects')
        self.passives_obj.update_rows(None)
        self.passives_obj.resize()
