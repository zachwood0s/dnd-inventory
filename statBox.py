import npyscreen
import typing
import character


class StatSlider(npyscreen.BoxTitle):
    _contained_widget = npyscreen.Slider


class StatBox(npyscreen.BoxTitle):
    pass


class StatGrid(npyscreen.BoxTitle):
    _contained_widget = npyscreen.GridColTitles
    default_column_number = 10

    def create(self, row_finder_function: typing.Callable[[], typing.List[character.Effect]]):
        self.column_width = 1
        self.rows = []
        self.row_finder_function = row_finder_function

    def update_rows(self):
        new_rows = self.row_finder_function()
        col_titles = ['Name']

        if len(new_rows) == 0:
            return

        cols = (x[:3] for x in new_rows[0].stats.__dict__.keys())
        col_titles.extend(cols)
        print(len(col_titles))

        self.entry_widget.col_titles = col_titles
