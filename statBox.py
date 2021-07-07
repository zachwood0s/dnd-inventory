import npyscreen
import typing
import character
import resourceManager


class StatSlider(npyscreen.BoxTitle):
    _contained_widget = npyscreen.Slider


class StatBox(npyscreen.BoxTitle):
    pass


class StatGrid(npyscreen.BoxTitle):
    _contained_widget = npyscreen.GridColTitles

    def create(self, row_finder_function: typing.Callable[[], typing.List[str]]):
        self.rows = []
        self.row_finder_function = row_finder_function
        self.entry_widget.select_whole_line = True

    def update_rows(self, packet_):
        new_rows = self.row_finder_function()

        if len(new_rows) == 0:
            self.entry_widget.values = []
        elif resourceManager.has_item(new_rows[0]):
            pass
        elif resourceManager.has_ability(new_rows[0]):
            pass
        elif resourceManager.has_effect(new_rows[0]):
            self.display_effects(new_rows)

        self.display()

    def display_effects(self, effects: typing.List[str]):
        self.entry_widget.columns_requested = 2
        self.entry_widget.columns = 2
        col_titles = ['Name', 'Modifiers']
        rows = [[eff.name, _str_effect_traits(eff.traits)] for eff in map(resourceManager.get_effect, effects)]
        self.entry_widget.values = rows
        self.entry_widget.col_titles = col_titles


def _str_effect_traits(traits: typing.List[character.EffectTrait]):
    ret = ''
    for t in traits:
        front = '+' if t.amt > 0 else '-' if t.amt < 0 else ''
        ret += f'({front}{t.name})'

    return ret
