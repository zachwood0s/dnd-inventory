from flexx import flx

from sanctum_dnd.ui.gui.html_helper import Html

url = "https://cdn.jsdelivr.net/npm/bootstrap@5.0.2/dist/css/bootstrap.min.css"
flx.assets.associate_asset(__name__, url)


class LogPanel(flx.Widget):

    def _render_dom(self):
        doc, tag, text = Html().tagtext()

        with tag('div', klass='d-flex flex-column align-items-stretch p-3 flex-shrink-0 bg-dark text-white h-100 '
                              'col-3',
                 style='width: 380px;'):
            with tag('div', klass='list-group list-group-flush border-bottom scrollarea'):
                for i in range(10):
                    with tag('a', href='#', klass='list-group-item list-group-item-action py-3 lh-tight bg-dark '
                                                  'text-white border-light'):
                        with tag('div', klass='d-flex w-100 align-items-center justify-content-between'):
                            with tag('strong', klass='mb-1'):
                                text('List group item heading')
                            with tag('small'):
                                text('Wed')
                        with tag('div', klass='col-10 mb-1 small'):
                            text('Some placeholder content in a paragraph below the heading and date.')

        return doc.finalize()
