import npyscreen
import textwrap
import resourceManager


class MessageBox(npyscreen.BoxTitle):

    # like a __init__
    def create(self, **kwargs):
        self.buff_messages = []
        self.entry_widget.highlighting_arr_color_data = []

    def update_messages(self, current_user):
        messages = self.get_messages_info(current_user)

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

    def get_messages_info(self, current_user):
        messages = resourceManager.get_messages(current_user)

        # get user info
        users = resourceManager.get_players()
        max_name_len = max(len(u.name) for u in users)

        # # check buffer
        # buff = self.buff_messages[current_user]
        # if buff is not None and messages is not None and \
        #         len(buff) != 0 and len(messages) != 0 and \
        #         len(messages) != len(buff) and \
        #         buff[0].id == messages[0].id and max_read_mess == self.buf_max_read_mess:
        #     return buff

        out = []
        for i in range(len(messages)):
            date = messages[i].date
            mess_id = messages[i].id

            # get name if message is forwarding
            prepare_forward_message = self.prepare_forward_messages(messages[i])

            # if chat or interlocutor
            if dialog_type == 1 or dialog_type == 2:
                user_name = users[messages[i].sender.id].name
                user_name = user_name if prepare_forward_message is False else prepare_forward_message
                if (len(user_name) != 0):
                    user_name = textwrap.wrap(user_name, self.width // 5)[0]
                else:
                    user_name = "Deleted Account"
                offset = " " * (max_name_len - (len(user_name)))
                name = read + user_name + ":" + offset
                color = (len(read) + len(user_name)) * [users[messages[i].sender.id].color]

            # if channel
            elif dialog_type == 3:
                user_name = client.dialogs[current_user].name
                user_name = user_name if prepare_forward_message is False else prepare_forward_message
                user_name = textwrap.wrap(user_name, self.width // 5)[0]

                name = user_name + ": "
                color = len(user_name) * [self.parent.theme_manager.findPair(self, 'WARNING')]

            else:
                name = ""
                color = [0]

            media = messages[i].media if hasattr(messages[i], 'media') else None
            mess = messages[i].message if hasattr(messages[i], 'message') \
                                          and isinstance(messages[i].message, str) else None

            image_name = ""
            if self.aalib and media is not None and hasattr(media, 'photo'):
                image_name = name
                name = len(name) * " "

            # add message to out []
            self.prepare_message(out, mess, name, read, mess_id, color, date)

            # add media to out []
            self.prepare_media(out, media, name, image_name, read, mess_id, color, date)

        # update buffer
        self.buff_messages[current_user] = out

        # return Message obj
        return out

    # structure for out message
    class Messages:
        def __init__(self, name, date, color, message, id, read):
            self.name = name
            self.color = color
            self.message = message

    # add message to Message structure
    def prepare_message(self, out, mess, name, read, mess_id, color, date):

        # add message to return
        if mess is not None and mess != "":
            if mess.find("\n") == -1:
                if len(mess) + len(name) + len(read) > self.width - 10:
                    max_char = self.width - len(name) - 10
                    arr = textwrap.wrap(mess, max_char)

                    for k in range(len(arr) - 1, 0, -1):
                        out.append(self.Messages(len(name) * " ", date, color, arr[k], mess_id, read))

                    out.append(self.Messages(name, date, color, arr[0], mess_id, read))
                else:
                    out.append(self.Messages(name, date, color, mess, mess_id, read))
            # multiline message
            else:
                mess = mess.split("\n")
                for j in range(len(mess) - 1, 0, -1):
                    if len(mess[j]) + len(name) + len(read) > self.width - 10:
                        max_char = self.width - len(name) - 10
                        arr = textwrap.wrap(mess[j], max_char)

                        for k in range(len(arr) - 1, -1, -1):
                            out.append(self.Messages(len(name) * " ", date, color, arr[k], mess_id, read))
                    else:
                        out.append(self.Messages(len(name) * " ", date, color, mess[j], mess_id, read))

                if len(mess[0]) + len(name) + len(read) > self.width - 10:
                    max_char = self.width - len(name) - 10
                    arr = textwrap.wrap(mess[0], max_char)

                    for k in range(len(arr) - 1, 0, -1):
                        out.append(self.Messages(len(name) * " ", date, color, arr[k], mess_id, read))

                    out.append(self.Messages(name, date, color, arr[0], mess_id, read))
                else:
                    out.append(self.Messages(name, date, color, mess[0], mess_id, read))
