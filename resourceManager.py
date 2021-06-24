import character

ME = 'me'

class ResourceManager:

  def __init__(self) -> None:
    self.my_player_name = None
    self.players = {}

  def get_player(self, name) -> character.Character:
    if name == ME:
      name = self.my_player_name
    return self.players[name]

  def load_character(self):
    new_char = character.Character()
    new_char.xp= 40
    self.my_player_name = new_char.name
    self.players[new_char.name] = new_char

