from .message import Message
import json


class MessageEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Message):
            # Convert the Message object to a dictionary
            return obj.__repr__()

        # Call the base class implementation which handles other types
        return super().default(obj)


class Conversation:

    def __init__(self, messages: list[Message] = None):
        self._messages = []

        if messages is not None:
            for message in messages:
                self.add_message(message)

    def add_message(self, message: Message):

        if self._messages is None:
            self._messages = []

        self._messages.append(message)

    @property
    def messages(self):
        return [
            message.to_dict() for message in self._messages
        ]

