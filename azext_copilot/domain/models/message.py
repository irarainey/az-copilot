class Message:
    def __init__(self, role, message=None, message_type=None):
        self._role = role
        self._message = message
        self._message_type = message_type

    @property
    def length(self):
        return len(self._message)

    @property
    def message(self):
        return self._message

    @message.setter
    def message(self, message):
        self._message = message

    @property
    def message_type(self):
        return self._message_type

    @message_type.setter
    def message_type(self, message_type):
        self._message_type = message_type

    def to_dict(self):
        return {
            "role": self._role.value,
            "content": self._message,
        }
