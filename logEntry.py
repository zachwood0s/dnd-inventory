import npyscreen
import settings
import character
import resourceManager
import statBox


class TraitGrid(npyscreen.BoxTitle):
    _contained_widget = npyscreen.GridColTitles


class LogEntry(npyscreen.Popup):
    DEFAULT_LINES = settings.POPUP_HEIGHT
    DEFAULT_COLUMNS = settings.POPUP_WIDTH
    SHOW_ATX = settings.POPUP_MARGIN_X
    SHOW_ATY = settings.POPUP_MARGIN_Y

    def __init__(self, log_item: str, **kwargs):
        self.log_item = log_item
        super().__init__(**kwargs)

    def create(self):
        self.name = "Log Entry"

        if resourceManager.has_item(self.log_item):
            self.create_item(resourceManager.get_item(self.log_item))
        elif resourceManager.has_effect(self.log_item):
            self.create_effect(resourceManager.get_effect(self.log_item))
        elif resourceManager.has_ability(self.log_item):
            pass

    def create_item(self, item: character.Item):
        self.name_obj = self.add(npyscreen.BoxTitle, editable=False, name="Name", values=[item.name],
                                 max_height=4, footer=f"ID: {self.log_item}")
        self.desc_obj = self.add(npyscreen.BoxTitle, editable=False, name='Desc', values=item.desc.splitlines(),
                                 max_height=8)

        grid_args = {'column_percents': []}
        self.actives_obj = self.add(statBox.StatGridBox, name='Actives', max_height=10,
                                    contained_widget_arguments=grid_args)
        self.actives_obj.create(lambda: item.actives)
        self.actives_obj.update_rows(None)
        self.actives_obj.resize()

        self.passives_obj = self.add(statBox.StatGridBox, name='Passives', max_height=10,
                                     contained_widget_arguments=grid_args)
        self.passives_obj.create(lambda: item.passives)
        self.passives_obj.update_rows(None)
        self.passives_obj.resize()

    def create_effect(self, effect: character.Effect):
        self.name_obj = self.add(npyscreen.BoxTitle, editable=False, name="Name", values=[effect.name],
                                 max_height=4, footer=f"ID: {self.log_item}")
        self.desc_obj = self.add(npyscreen.BoxTitle, editable=False, name='Desc', values=effect.desc.splitlines(),
                                 max_height=8)

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
