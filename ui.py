from utils import columns
import stat
import npyscreen
import curses
import messageBox
import inputBox
import statBox
import character
import commandHandler
import resourceManager

MAX_WIDTH = 150
MAX_HEIGHT = 50


class MainForm(npyscreen.FormBaseNew):

    def create(self):
        y, x = self.useable_space()

        log_width = (x // 4)

        # create ui
        self.messageBoxObj = self.add(messageBox.MessageBox, name='Log', rely=2, relx=(x - log_width),
                                      max_height=-5, editable=False)
        self.inputBoxObj = self.add(inputBox.InputBox, footer='Input', rely=-7, relx=(x - log_width), editable=True)
        self.inputBoxObj.create()

        remaining_width = x - log_width

        # STAT BARS
        bar_padding = 2
        bar_width, bar_xs = columns(remaining_width, 2, bar_padding)
        bar_height = 3
        bar_args = {'out_of': 100, 'value': 40, 'color': 'DANGER'}

        self.healthBarObj = self.add(statBox.StatSlider, name='HP', color='DANGER', max_width=bar_width,
                                     max_height=bar_height,
                                     relx=bar_xs[0], rely=2, editable=False,
                                     contained_widget_arguments=bar_args)

        bar_args = {'out_of': 100, 'value': 40, 'color': 'GOOD'}
        self.xpbarObj = self.add(statBox.StatSlider, name='XP', color='GOOD', max_width=bar_width,
                                 max_height=bar_height,
                                 relx=bar_xs[1], rely=2, editable=False,
                                 contained_widget_arguments=bar_args)

        # BATTLE STATS
        stat_padding = 4
        stat_width, stat_xs = columns(remaining_width, len(character.DEFAULT_BATTLE_STATS), stat_padding)
        stat_height = 4
        stat_y = 6

        self.statObjs = {}
        for idx, (stat, val) in enumerate(character.DEFAULT_BATTLE_STATS.items()):
            self.statObjs[stat] = self.add(statBox.StatBox, name=stat.upper(), values=[str(val)], color='NO_EDIT',
                                           editable=False,
                                           max_width=stat_width, max_height=stat_height, relx=stat_xs[idx], rely=stat_y)

        # PERSON STATS
        person_padding = 4
        person_width, person_xs = columns(remaining_width, len(character.DEFAULT_PERSON_STATS), person_padding)
        person_height = 4
        person_y = 11

        self.personObjs = {}
        for idx, (person, val) in enumerate(character.DEFAULT_PERSON_STATS.items()):
            self.personObjs[person] = self.add(statBox.StatBox, name=person.upper(), values=[str(val)], color='NO_EDIT',
                                               editable=False,
                                               max_width=person_width, max_height=person_height, relx=person_xs[idx],
                                               rely=person_y)

        # ITEMS
        remaining_height = y - (person_y + person_height)
        item_padding = 2
        self.itemsObj = self.add(statBox.StatBox, name='Items', max_width=remaining_width - 2 * item_padding,
                                 max_height=(remaining_height // 2))

        # ABILITIES
        self.abilitiesObj = self.add(statBox.StatBox, name='Abilities', max_width=remaining_width - 2 * item_padding)

        # init handlers
        new_handlers = {
            # exit
            '^Q': self.exit_func,
        }

        self.add_handlers(new_handlers)
        resourceManager.add_update_handler(self.character_update_handler)
        # self.messageBoxObj.update_chat(None)

    def event_input_send(self):
        text = self.inputBoxObj.value
        self.inputBoxObj.value = ''
        commandHandler.parse_command(text)

    def afterEditing(self):
        self.parentApp.setNextForm(None)

    def exit_func(self, _input):
        exit(0)

    def character_update_handler(self, _msg, _name, _character):
        self.update_character()
        self.display()
        self.xpbarObj.display()
        self.healthBarObj.display()
        self.itemsObj.display()
        self.abilitiesObj.display()

        for _, obj in self.statObjs.items():
            obj.display()

        for _, obj in self.personObjs.items():
            obj.display()

    def update_character(self):
        player = resourceManager.get_player(resourceManager.ME)

        self.xpbarObj.value = player.xp
        self.xpbarObj.entry_widget.out_of = player.xp
        self.healthBarObj.value = player.health
        self.healthBarObj.entry_widget.out_of = player.max_health

        for stat in player.battle_stats:
            self.statObjs[stat].values = [player.get_stat(stat)]

        for stat in player.person_stats:
            self.personObjs[stat].values = [player.get_stat(stat)]

        print('character sheet updated')


class App(npyscreen.StandardApp):
    def __init__(self):
        super().__init__()

    def onStart(self):
        resourceManager.load_character()
        self.registerForm("MAIN", MainForm(lines=MAX_HEIGHT, columns=MAX_WIDTH))
        self.getForm('MAIN').update_character()


if __name__ == '__main__':
    app = App()
    app.run()
