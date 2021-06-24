import npyscreen

MAX_WIDTH=100
MAX_HEIGHT=40

class Character:
  def __init__(self):
    self.health = 100
    self.max_health = 100
    self.xp = 100
    self.xp_to_next = 200
    
    self.constitution = 4
    self.intelligence = 4
    self.wisdom = 4
    self.dexterity = 4
    self.strength = 3
    self.charisma = 3

    self.ac = 20
    self.speed = 2
    self.init = 10


class TestApp(npyscreen.NPSAppManaged):

  def onStart(self):
    self.registerForm("MAIN", CharacterForm(lines=MAX_HEIGHT, columns=MAX_WIDTH))

class StatBox(npyscreen.BoxTitle):
  width = 30
  def __init__(self, screen, contained_widget_arguments=None, *args, **kwargs):
    kwargs['max_height'] = 4
    kwargs['max_width'] = StatBox.width
    super().__init__(screen, contained_widget_arguments, *args, editable=False, **kwargs)
    self.editable = False

class StatBar(npyscreen.BoxTitle):
  _contained_widget = npyscreen.Slider
  def __init__(self, screen, contained_widget_arguments=None, *args, **kwargs):
    kwargs['max_height'] = 3
    super().__init__(screen, contained_widget_arguments, *args, editable=False, **kwargs)
    self.editable=False


class CharacterForm(npyscreen.Form):
  def create(self):
    self.character = None
    padding = 4
    self.hp = self.add(StatBar, color='DANGER', max_width=int(MAX_WIDTH/2) - int(1.5*padding), name='HP', relx=padding, rely=2, contained_widget_arguments={'out_of': 100, 'value':40, 'color':'DANGER'})
    self.xp = self.add(StatBar, color='GOOD', max_width=int(MAX_WIDTH/2) - int(1.5*padding), name='XP', relx=int(MAX_WIDTH/2)+int(padding/2),rely=2, contained_widget_arguments={'out_of': 100, 'value':40, 'color':'GOOD'})

    self.ac = self.add(StatBox, color='NO_EDIT', name='AC', values=['40'], relx=padding, rely=6)
    self.speed = self.add(StatBox, color='NO_EDIT', name='SPD', values=['2'], relx=StatBox.width + padding+1, rely=6)
    self.init = self.add(StatBox, color='NO_EDIT', name='INIT', values=['20'], relx=2*StatBox.width + padding+2, rely=6)
    """
    self.xp = self.add(npyscreen.TitleSlider, color='GOOD', name='XP', out_of=100, value=40, max_width=50, max_height=3, relx=50, rely = 2)
    self.xp.editable = False
    self.ac = self.add(npyscreen.BoxTitle, name='AC', max_height=4, max_width=20, values=['40'])
    self.ac.editable = False
    self.speed = self.add(npyscreen.BoxTitle, name='SPEED', max_height=4, relx=22, max_width=20, values=['40'])
    self.speed.editable = False
    self.init = self.add(npyscreen.BoxTitle, name='INIT', max_height=4, relx=42, max_width=20, values=['40'])
    self.init.editable = False
    #self.xp = self.add(npyscreen.TitleSlider, color='SUCCESS', name='XP', out_of=100, value=40, relx=42, rely=2, max_width=50, max_height=3)
    #self.xp = self.add(npyscreen.BoxBasic, name='XP:', rely=2, max_width=30, max_height=3)
    """

  def afterEditing(self):
    self.parentApp.setNextForm(None)

class MainForm(npyscreen.Form):
  def create(self):
    self.name = self.add(npyscreen.TitleText, name='Name')

  def afterEditing(self):
    self.parentApp.setNextForm(None)



if __name__ == '__main__':
  TA = TestApp()
  TA.run()