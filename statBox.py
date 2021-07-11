import npyscreen
import curses
import math
import typing
import character
import resourceManager


class StatSlider(npyscreen.BoxTitle):
    _contained_widget = npyscreen.Slider


class StatBox(npyscreen.BoxTitle):
    pass


class StatGrid(npyscreen.GridColTitles):
    def __init__(self, screen, column_percents=None, **kwargs):
        self.column_percents = column_percents
        super().__init__(screen, **kwargs)
        assert column_percents is not None, "column_widths cannot be none"

    def display(self):
        if hasattr(self.parent_widget, 'update_footer'):
            self.parent_widget.update_footer()
            self.parent_widget.display()

        super().display()

    def page_information(self):
        per_page = len(self._my_widgets)
        current_page = self.begin_row_display_at // per_page + 1
        return per_page, current_page

    def make_contained_widgets(self):

        self.columns = len(self.column_percents)
        self._my_widgets = []
        out_of = sum(self.column_percents)
        total_usable = (self.width + self.col_margin - self.additional_x_offset)
        # column_width = (self.width + self.col_margin - self.additional_x_offset) // self.columns
        column_widths = [int((p / out_of) * total_usable - self.col_margin) for p in self.column_percents]
        if any(c < 1 for c in column_widths): raise Exception("Too many columns for space available")

        self._my_col_titles = []
        cur_pos = 0
        for w in column_widths:
            x_offset = cur_pos
            self._my_col_titles.append(self._col_widgets(self.parent, rely=self.rely, relx=self.relx + x_offset,
                                                         width=w, height=1))
            cur_pos += w + self.col_margin

        self._my_widgets = []
        for h in range( (self.height - self.additional_y_offset) // self.row_height ):
            h_coord = h * self.row_height
            row = []
            cur_pos = 0
            for w in column_widths:
                x_offset = cur_pos
                row.append(self._contained_widgets(self.parent, rely=h_coord+self.rely + self.additional_y_offset,
                                                   relx=self.relx + x_offset + self.additional_x_offset, width=w,
                                                   height=self.row_height))
                cur_pos += w + self.col_margin
            self._my_widgets.append(row)

    def set_up_handlers(self):
        super().set_up_handlers()
        self.handlers.update({
            curses.KEY_ENTER: self.enter_command,
            curses.ascii.NL: self.enter_command,
            curses.ascii.CR: self.enter_command,
        })

    def enter_command(self, event_):
        import logEntry
        idx = self.edit_cell[0]
        if idx < len(self.parent_widget.ids):
            id = self.parent_widget.ids[idx]
            logEntry.LogEntry(id).edit()


class StatGridBox(npyscreen.BoxTitle):
    _contained_widget = StatGrid

    def create(self, row_finder_function: typing.Callable[[], typing.List[str]], obj_type: str):
        self.ids = []
        self.rows = []
        self.row_finder_function = row_finder_function
        self.entry_widget.select_whole_line = True
        self.entry_widget.values = []
        self.obj_type = obj_type

    def update_rows(self, packet_):
        new_rows = self.row_finder_function()

        if len(new_rows) == 0:
            self.entry_widget.values = []
        if self.obj_type == 'items':
            self.display_items(new_rows)
        elif self.obj_type == 'abilities':
            self.display_abilities(new_rows)
        elif self.obj_type == 'effects':
            self.display_effects(new_rows)

        self.display()

    def display(self):
        self.update_footer()
        super().display()

    def update_footer(self):
        per_page, current_page = self.entry_widget.page_information()
        page_count = math.ceil(len(self.rows) / per_page)
        self.footer = f'<Page {current_page}/{page_count}>'

    def display_effects(self, effects: typing.List[str]):
        self.entry_widget.columns_requested = 2
        self.entry_widget.columns = 2
        self.entry_widget.column_percents = [2, 11]
        col_titles = ['Name', 'Modifiers']
        rows = [[eff.name, _str_effect_traits(eff.traits)] for eff in map(resourceManager.get_effect, effects)]
        self.entry_widget.values = rows
        self.entry_widget.col_titles = col_titles
        self.rows = rows
        self.ids = effects

    def display_items(self, items: typing.List[str]):
        self.entry_widget.columns_requested = 4
        self.entry_widget.columns = 4
        col_titles = ['Name', 'Passives', 'Actives', 'Qty']
        self.entry_widget.column_percents = [2, 5, 5, 1]
        me = resourceManager.get_player(resourceManager.get_viewed_player_name())
        rows = []
        for item in items:
            i = resourceManager.get_item(item)
            front = '(Using) ' if item in me.active_items else ''
            rows.append([front + i.name, _str_item_traits(i.passives),
                         _str_item_traits(character.active_selector(i)()), me.item_qtys[item]])

        self.entry_widget.values = rows
        self.entry_widget.col_titles = col_titles
        self.rows = rows
        self.ids = items

    def display_abilities(self, abilities: typing.List[str]):
        self.entry_widget.columns_requested = 7
        self.entry_widget.columns = 7
        col_titles = ['Name', 'Range', 'To Hit', 'Dice', 'Type', 'Passives', 'Actives']
        self.entry_widget.column_percents = [2, 1, 1, 1, 1, 2, 2]

        rows = [[eff.name, eff.stats[character.RANGE], eff.stats[character.TO_HIT],
                 eff.stats[character.DICE], eff.stats[character.DAMAGE_TYPE], _str_ability_traits(eff.passives),
                 _str_ability_traits(eff.actives)]
                for eff in map(resourceManager.get_ability, abilities)]

        self.entry_widget.values = rows
        self.entry_widget.col_titles = col_titles
        self.rows = rows
        self.ids = abilities


def _str_ability_traits(effects: typing.List[str]):
    return ''.join(_str_effect_traits(resourceManager.get_effect(e).traits) for e in effects)


def _str_item_traits(effects: typing.List[str]):
    return ''.join(_str_effect_traits(resourceManager.get_effect(e).traits) for e in effects)


def _str_effect_traits(traits: typing.List[character.EffectTrait]):
    ret = ''
    for t in traits:
        front = '+' if t.amt > 0 else '-' if t.amt < 0 else ''
        ret += f'({front}{t.name})'

    return ret
