import os

from flexx import flx

from sanctum_dnd.ui.gui.log_panel import LogPanel

BASE_DIR = os.getcwd()

with open(BASE_DIR + '/static/main.css') as f:
    style = f.read()

url = "https://cdn.jsdelivr.net/npm/bootstrap@5.0.2/dist/css/bootstrap.min.css"
flx.assets.associate_asset(__name__, url)
flx.assets.associate_asset(__name__, 'style.css', style)


class MainPanel(flx.Widget):
    def _create_dom(self):
        return flx.create_element('div')


class Example(flx.Widget):
    persons = flx.TupleProp((), doc=""" People to show cards for""")
    first_name = flx.StringProp('', settable=True)
    last_name = flx.StringProp('', settable=True)

    def _create_dom(self):
        return flx.create_element('main', {'class': 'h-100'})

    def init(self):
        MainPanel()
        LogPanel()

    @flx.action
    def add_person(self, name, info):
        """ Add a person to our stack.
        """
        ppl = list(self.persons)
        ppl.append((name, info))
        self._mutate_persons(ppl)


if __name__ == '__main__':
    m = flx.launch(Example, 'chrome-app')
    flx.run()
