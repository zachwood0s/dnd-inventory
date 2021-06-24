import curses
import npyscreen

class InputBox(npyscreen.BoxTitle):
  _contained_widget = npyscreen.Textfield

  def create(self):
    new_handlers = {
      curses.KEY_ENTER: self.enter_command,
      curses.ascii.NL: self.enter_command,
      curses.ascii.CR: self.enter_command,
    }

    self.entry_widget.handlers.update(new_handlers)

  def enter_command(self, _input):
    self.parent.event_input_send()
