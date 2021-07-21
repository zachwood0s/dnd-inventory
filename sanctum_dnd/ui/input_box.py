import curses

import npyscreen
import sanctum_dnd.commands as commands
import sanctum_dnd.commands.help_text
from sanctum_dnd import resource_manager, character


class _InputBoxInner(npyscreen.Autocomplete):
    def __init__(self, screen, **kwargs):
        self.command_handlers = {
            commands.help_text.PLAYER: self.auto_complete_player,
            commands.help_text.ITEM_ID: self.auto_complete_item_id,
            commands.help_text.ABILITY_ID: self.auto_complete_ability_id,
            commands.help_text.EFFECT_ID: self.auto_complete_effect_id,
            commands.help_text.PLAYERS_ITEM: self.auto_complete_players_item_id,
            commands.help_text.PLAYERS_ABILITY: self.auto_complete_players_ability_id,
            commands.help_text.PLAYERS_EFFECT: self.auto_complete_players_effect_id,
            commands.help_text.TRAIT: self.auto_complete_trait,
            commands.help_text.DICE_FMT: self.auto_complete_dice_fmt,
            commands.help_text.ANY_ID: self.auto_complete_any_id,
            commands.help_text.OBJ_TYPE: self.auto_complete_obj_type,
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
            command_list = commands.get_command_list(words[0])
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
    def find_player(words, command: commands.command_handler.Command):
        try:
            idx = command.help_text.split().index(commands.help_text.PLAYER)
        except ValueError:
            # player not in the command
            return resource_manager.get_player(resource_manager.ME)

        player_id = words[idx]
        try:
            return resource_manager.get_player(player_id)
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
        return [x for x in commands.get_all_command_names() if x.startswith(part_word)]

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
        return [item_id for item_id in resource_manager.get_items().keys() if item_id.startswith(part_word)]

    @staticmethod
    def auto_complete_ability_id(words, command, part_word: str):
        return [ability_id for ability_id in resource_manager.get_abilities().keys() if
                ability_id.startswith(part_word)]

    @staticmethod
    def auto_complete_effect_id(words, command, part_word: str):
        return [effect_id for effect_id in resource_manager.get_effects().keys() if effect_id.startswith(part_word)]

    @staticmethod
    def auto_complete_player(words, command, part_word: str):
        players = [p.get_stat(character.NAME) for p in resource_manager.get_players()]
        players.append('me')
        filtered = [name.replace(' ', '_') for name in players if name.startswith(part_word)]
        return filtered

    @staticmethod
    def auto_complete_obj_type(words, command, part_word: str):
        auto_obj = ['item', 'ability', 'effect']
        return [d for d in auto_obj if d.startswith(part_word)]

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

