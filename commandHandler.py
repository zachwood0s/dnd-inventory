# commands: roll <dice>, change <player> <stat> <value>, give <character> <itemname>
import re
import random

import npyscreen

class DiceRoller:
  """
  Handles roll <dice> <player> <ability>
  """
  @staticmethod
  def parse_command(form, input: list):
    argc = len(input)
    if argc != 2 and argc != 4:
      raise ValueError('Roll command malformed! Expected 1 or 3 arguments')

    player = None
    trait = None
    if len(input) > 2:
      player = input[2]
      trait = input[3]

    roll_amt, dice = DiceRoller.get_dice_amt(input[1])

    # Lookup player and trait
    if player is not None:
      print(player)

    roll = random.randrange(1, dice_size+1) 
    print(roll)

    for _ in range(roll_amt):
      DiceRoller.make_roll(dice, player, trait)

  DICE_REGEX = re.compile('([0-9]*)d([0-9]+)')
  @staticmethod
  def get_dice_amt(input: str):
    res = DiceRoller.DICE_REGEX.match(input)

    amt = 1
    if res.group(1) != '':
      amt = int(res.group(1))

    dice = int(res.group(2))

    return amt, dice


class SetHandler:

  @staticmethod
  def parse_command(form, input_: list):
    if len(input_) != 4:
      raise ValueError('set command malformed! Expected 4 arguments')

    (_, name, stat, value, ) = input_
    player = form.find_parent_app().resources.get_player(name)
    player.set_stat(stat, value)

    print(f'changed {name}s {stat} to {value}')

class CommandHandler:

  COMMAND_MAPPING = {
    'roll': DiceRoller,
    'set': SetHandler,
  }

  @staticmethod
  def parse_command(form, input: str):
    input = input.lower()
    print(f'recieved command {input}')
    command = input.split(' ')

    handler = CommandHandler.COMMAND_MAPPING.get(command[0])
    if handler is not None:
      handler.parse_command(form, command)
      form.event_update_main_form(None)



