import curses
import npyscreen
import commands
import commandHandler
import resourceManager
import character


class _InputBoxInner(npyscreen.Autocomplete):
    def __init__(self, screen, **kwargs):
        self.command_handlers = {
            commands.PLAYER: self.auto_complete_player,
            commands.ITEM_ID: self.auto_complete_item_id,
            commands.ABILITY_ID: self.auto_complete_ability_id,
            commands.EFFECT_ID: self.auto_complete_effect_id,
            commands.PLAYERS_ITEM: self.auto_complete_players_item_id,
            commands.PLAYERS_ABILITY: self.auto_complete_players_ability_id,
            commands.PLAYERS_EFFECT: self.auto_complete_players_effect_id,
            commands.TRAIT: self.auto_complete_trait,
            commands.DICE_FMT: self.auto_complete_dice_fmt,
            commands.ANY_ID: self.auto_complete_any_id,
        }
        super().__init__(screen, **kwargs)

    def set_up_handlers(self):
        super().set_up_handlers()

    def auto_complete(self, input_):
        words = self.value.split()
        if self.value != '' and self.value[-1] == ' ':
            # If the input ends with a space, add an empty word to act like an empty autofill
            words.append('')

        count = len(words)
        possibilities = set()
        if count == 0:
            possibilities = self.auto_complete_commands(words, None, '')
        elif count == 1:
            # Only one command and we're not starting the next
            possibilities = self.auto_complete_commands(words, None, words[-1])
        else:
            # find command then find each piece
            command_list = commandHandler._REGISTERED_COMMANDS.get(words[0], None)
            if command_list is not None:
                for arg_amt, command in command_list.items():
                    if count <= arg_amt + 1:
                        # This command could still be trying to be typed
                        handler_key = command.help_text.split()[count - 1]
                        handler = self.command_handlers.get(handler_key, None)

                        if handler is not None:
                            possibilities.update(handler(words, command, words[-1]))

        # Add space so its ready for the next word
        existing = ' '.join(words[:-1])
        self.use_possibilities(existing, sorted(possibilities))
        self.value += ' '
        self.cursor_position = len(self.value)

    def use_possibilities(self, existing, possibilities):
        count = len(possibilities)
        new_value = ''
        if count == 0:
            # No possibilities
            return
        elif count == 1:
            # found only one, change the value to the only option
            new_value = possibilities[0]
        else:
            new_value = possibilities[self.show_choices(possibilities)]

        if existing != '':
            self.value = f'{existing} {new_value}'
        else:
            self.value = new_value

    @staticmethod
    def find_player(words, command: commandHandler.Command):
        try:
            idx = command.help_text.split().index(commands.PLAYER)
        except ValueError:
            # player not in the command
            return resourceManager.get_player(resourceManager.ME)

        player_id = words[idx]
        try:
            return resourceManager.get_player(player_id)
        except ValueError:
            return None

    @staticmethod
    def auto_complete_dice_fmt(words, command, part_word: str):
        auto_dice = ['d20']
        return [d for d in auto_dice if d.startswith(part_word)]

    @staticmethod
    def auto_complete_trait(words, command, part_word: str):
        p = _InputBoxInner.find_player(words, command)
        if p is None:
            return []
        else:
            return [x for x in p.get_stat_names() if x.startswith(part_word)]

    @staticmethod
    def auto_complete_commands(words, command, part_word: str):
        # autocomplete the command name
        return [x for x in commandHandler._REGISTERED_COMMANDS.keys() if x.startswith(part_word)]

    @staticmethod
    def auto_complete_players_item_id(words, command, part_word: str):
        p = _InputBoxInner.find_player(words, command)
        if p is None:
            return []
        else:
            return [item_id for item_id in p.items if item_id.startswith(part_word)]

    @staticmethod
    def auto_complete_players_effect_id(words, command, part_word: str):
        p = _InputBoxInner.find_player(words, command)
        if p is None:
            return []
        else:
            return [effect_id for effect_id in p.effects if effect_id.startswith(part_word)]

    @staticmethod
    def auto_complete_players_ability_id(words, command, part_word: str):
        p = _InputBoxInner.find_player(words, command)
        if p is None:
            return []
        else:
            return [ability_id for ability_id in p.abilities if ability_id.startswith(part_word)]

    def auto_complete_any_id(self, words, command, part_word: str):
        res = self.auto_complete_item_id(words, command, part_word)
        res += self.auto_complete_ability_id(words, command, part_word)
        res += self.auto_complete_effect_id(words, command, part_word)
        return res

    @staticmethod
    def auto_complete_item_id(words, command, part_word: str):
        return [item_id for item_id in resourceManager.get_items().keys() if item_id.startswith(part_word)]

    @staticmethod
    def auto_complete_ability_id(words, command, part_word: str):
        return [ability_id for ability_id in resourceManager.get_abilities().keys() if ability_id.startswith(part_word)]

    @staticmethod
    def auto_complete_effect_id(words, command, part_word: str):
        return [effect_id for effect_id in resourceManager.get_effects().keys() if effect_id.startswith(part_word)]

    @staticmethod
    def auto_complete_player(words, command, part_word: str):
        players = [p.get_stat(character.NAME) for p in resourceManager.get_players()]
        players.append('me')
        filtered = [name.replace(' ', '_') for name in players if name.startswith(part_word)]
        return filtered

    def show_choices(self, possibilities):
        width = self.width + 8
        height = 10
        print(height, width)
        return self.get_choice(possibilities, x=self.relx - 4, y=self.rely - height - 1, lines=height, columns=width)


class InputBox(npyscreen.BoxTitle):
    _contained_widget = _InputBoxInner

    def create(self):
        new_handlers = {
            curses.KEY_ENTER: self.enter_command,
            curses.ascii.NL: self.enter_command,
            curses.ascii.CR: self.enter_command,
        }

        self.entry_widget.handlers.update(new_handlers)

    def enter_command(self, _input):
        self.parent.event_input_send()

