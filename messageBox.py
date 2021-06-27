import npyscreen
import textwrap
import resourceManager

MY_COLOR = 'VERYGOOD'
OTHER_COLOR = 'WARNING'

class MessageBox(npyscreen.BoxTitle):

    # like a __init__
    def create(self, **kwargs):
        self.buff_messages = []
        self.entry_widget.highlighting_arr_color_data = []

    def update_messages(self):
        messages = self.get_messages_info()

        color_data = []
        data = []
        for i in range(len(messages) - 1, -1, -1):
            # replace empty char
            messages[i].message = messages[i].message.replace(chr(8203), '')

            data.append(messages[i].name + " " + messages[i].message)
            color_data.append(messages[i].color)

        self.entry_widget.highlighting_arr_color_data = color_data

        self.values = data

        if len(messages) > self.height - 3:
            self.entry_widget.start_display_at = len(messages) - self.height + 3
        else:
            self.entry_widget.start_display_at = 0

        self.entry_widget.cursor_line = len(messages)

        self.display()

    def get_messages_info(self):
        messages = resourceManager.get_chat_messages()

        # get user info
        users = resourceManager.get_players()
        max_name_len = max(len(textwrap.wrap(u.name, self.width // 5)[0]) for u in users)

        out = []
        for msg in messages:

            # if chat or interlocutor
            user_name = msg.sender
            if len(user_name) != 0:
                user_name = textwrap.wrap(user_name, self.width // 5)[0]

            offset = " " * (max_name_len - (len(user_name)))
            name = user_name + ":" + offset
            color_name = MY_COLOR if msg.sender == resourceManager.get_my_player_name() else OTHER_COLOR
            color_val = self.parent.theme_manager.findPair(self, color_name)
            color = (len(user_name)) * [color_val]
            mess = "\n".join(msg.data)

            # add message to out []
            self.prepare_message(out, mess, name, color)

        # update buffer
        self.buff_messages = out

        # return Message obj
        return out

    # structure for out message
    class Messages:
        def __init__(self, name, color, message):
            self.name = name
            self.color = color
            self.message = message

    # add message to Message structure
    def prepare_message(self, out, mess, name, color):

        # add message to return
        if mess is not None and mess != "":
            if mess.find("\n") == -1:
                if len(mess) + len(name) > self.width - 10:
                    max_char = self.width - len(name) - 10
                    arr = textwrap.wrap(mess, max_char)

                    for k in range(len(arr) - 1, 0, -1):
                        out.append(self.Messages(len(name) * " ", color, arr[k]))

                    out.append(self.Messages(name, color, arr[0]))
                else:
                    out.append(self.Messages(name, color, mess))
            # multiline message
            else:
                mess = mess.split("\n")
                for j in range(len(mess) - 1, 0, -1):
                    if len(mess[j]) + len(name) > self.width - 10:
                        max_char = self.width - len(name) - 10
                        arr = textwrap.wrap(mess[j], max_char)

                        for k in range(len(arr) - 1, -1, -1):
                            out.append(self.Messages(len(name) * " ", color, mess[j]))
                    else:
                        out.append(self.Messages(len(name) * " ", color, mess[j]))

                if len(mess[0]) + len(name) > self.width - 10:
                    max_char = self.width - len(name) - 10
                    arr = textwrap.wrap(mess[0], max_char)

                    for k in range(len(arr) - 1, 0, -1):
                        out.append(self.Messages(len(name) * " ", color, arr[k]))

                    out.append(self.Messages(name, color, arr[0]))
                else:
                    out.append(self.Messages(name, color, mess[0]))
