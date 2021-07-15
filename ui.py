from utils import columns
import textwrap
import npyscreen
import curses
import messageBox
import inputBox
import statBox
import character
import commandHandler
import resourceManager
import logEntry
from settings import MAX_HEIGHT, MAX_WIDTH
import commands


class MainForm(npyscreen.FormBaseNew):

    def create(self):
        self.footer = ' Connected '
        self.name = 'DND Inventory'
        y, x = self.useable_space()

        log_width = (x // 4)

        # create ui
        self.messageBoxObj = self.add(messageBox.MessageBox, name='Log', rely=2, relx=(x - log_width),
                                      max_height=-15, editable=False, custom_highlighting=True,
                                      highlighting_arr_color_data=[0])

        # create ui
        self.logBoxObj = self.add(npyscreen.BoxTitle, name='Console', relx=(x - log_width),
                                  max_height=10, editable=False)

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
        num_cols = len(character.DEFAULT_BATTLE_STATS) + 2 # add two for the two empty columns for the name
        stat_width, stat_xs = columns(remaining_width, num_cols, stat_padding)
        stat_height = 4
        stat_y = 6

        self.nameObj = self.add(statBox.StatBox, name='NAME', values=[''], color='WARNING', editable=False,
                                max_width=stat_width*2 + stat_padding, max_height=stat_height,
                                relx=stat_xs[0], rely=stat_y)

        self.statObjs = {}
        for idx, (stat, val) in enumerate(character.DEFAULT_BATTLE_STATS.items()):
            self.statObjs[stat] = self.add(statBox.StatBox, name=stat.upper(), values=[str(val)], color='VERYGOOD',
                                           editable=False,
                                           max_width=stat_width, max_height=stat_height, relx=stat_xs[idx+2], rely=stat_y)

        # PERSON STATS
        person_padding = 4
        person_width, person_xs = columns(remaining_width, len(character.DEFAULT_PERSON_STATS), person_padding)
        person_height = 4
        person_y = 11

        self.personObjs = {}
        for idx, (person, val) in enumerate(character.DEFAULT_PERSON_STATS.items()):
            self.personObjs[person] = self.add(statBox.StatBox, name=person.upper(), values=[str(val)], color='VERYGOOD',
                                               editable=False,
                                               max_width=person_width, max_height=person_height, relx=person_xs[idx],
                                               rely=person_y)

        # ITEMS
        remaining_height = y - (person_y + person_height)
        item_padding = 2

        # ABILITIES
        grid_args = {'column_percents': []}
        self.effects = self.add(statBox.StatGridBox, name='Effects', max_width=remaining_width - 2 * item_padding,
                                max_height=(remaining_height // 3), contained_widget_arguments=grid_args)

        self.effects.create(
            lambda: resourceManager.get_player(resourceManager.get_viewed_player_name()).get_effects(), 'effects')
        self.effects.update_rows(None)

        grid_args = {'column_percents': []}
        self.itemsObj = self.add(statBox.StatGridBox, name='Items', max_width=remaining_width - 2 * item_padding,
                                 max_height=(remaining_height // 3), contained_widget_arguments=grid_args)
        self.itemsObj.create(
            lambda: resourceManager.get_player(resourceManager.get_viewed_player_name()).items, 'items')
        self.itemsObj.update_rows(None)

        # ABILITIES
        grid_args = {'column_percents': []}
        self.abilitiesObj = self.add(statBox.StatGridBox, name='Weapons & Abilities', max_width=remaining_width - 2 * item_padding,
                                     contained_widget_arguments=grid_args)
        self.abilitiesObj.create(
            lambda: resourceManager.get_player(resourceManager.get_viewed_player_name()).get_abilities(), 'abilities')
        self.abilitiesObj.update_rows(None)

        # init handlers
        new_handlers = {
            # exit
            '^Q': self.exit_func,
        }

        self.add_handlers(new_handlers)
        resourceManager.add_character_update_handler(self.character_update_handler)
        resourceManager.add_character_update_handler(self.effects.update_rows)
        resourceManager.add_character_update_handler(self.itemsObj.update_rows)
        resourceManager.add_character_update_handler(self.abilitiesObj.update_rows)
        resourceManager.add_chat_update_handler(lambda _: self.messageBoxObj.update_messages())
        resourceManager.add_error_update_handler(self.error_update_handler)
        resourceManager.add_connected_update_handler(self.connected_update_handler)
        resourceManager.add_event_handler(self.queue_event)
        self.connected_update_handler(False)
        self.add_event_hander("SHOWEVENT", self.handle_show_event)

    def event_input_send(self):
        text = self.inputBoxObj.value
        self.inputBoxObj.value = ''
        commandHandler.parse_command(text)

    def afterEditing(self):
        self.parentApp.setNextForm(None)

    def exit_func(self, _input):
        self.parentApp.switchForm(None)

    def error_update_handler(self, packet_):
        self.logBoxObj.entry_widget.values = [x for t in packet_.data.splitlines()
                                              for x in textwrap.wrap(t, self.logBoxObj.entry_widget.width)]
        self.logBoxObj.display()

    def connected_update_handler(self, connected: bool):
        if resourceManager.get_is_connected():
            self.footer = ' Connected '
        else:
            self.footer = ' Disconnected '

        self.display()

    def character_update_handler(self, _packet):
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
        player = resourceManager.get_player(resourceManager.get_viewed_player_name())

        self.xpbarObj.value = player.get_stat(character.XP)
        self.xpbarObj.entry_widget.out_of = player.get_stat(character.MAX_XP)
        self.healthBarObj.value = player.get_stat(character.HP)
        self.healthBarObj.entry_widget.out_of = player.get_stat(character.MAX_HP)

        front = '(NOT YOU) ' if player.get_stat(character.NAME) != resourceManager.get_my_player_name() else ''
        self.nameObj.values = [front + player.get_stat(character.NAME)]

        for stat in player.battle_stats:
            self.statObjs[stat].values = player.fmt_stat(stat).splitlines()

        for stat in player.person_stats:
            self.personObjs[stat].values = player.fmt_stat(stat).splitlines()

        print('character sheet updated')

    def draw_title_and_help(self):
        super().draw_title_and_help()

        self.add_line(self.lines - 1, 5, self.footer, self.make_attributes_list(self.footer, curses.A_NORMAL), self.columns - 4)

    def handle_show_event(self, event):
        data = event.payload
        logEntry.LogEntry(data).edit()
        self.display()

    def queue_event(self, event: npyscreen.Event):
        self.parentApp.queue_event(event)


class App(npyscreen.StandardApp):
    def __init__(self):
        super().__init__()

    def onStart(self):
        resourceManager.default_character()
        self.registerForm("MAIN", MainForm(lines=MAX_HEIGHT, columns=MAX_WIDTH, parentApp=self))
        self.getForm('MAIN').update_character()
        resourceManager.load_character()


if __name__ == '__main__':
    app = App()
    app.run()
