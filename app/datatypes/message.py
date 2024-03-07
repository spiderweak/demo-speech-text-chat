import uuid

class Message:
    def __init__(self, emitter: str, content: str = "") -> None:
        self.id = uuid.uuid4()
        self.emitter = emitter
        self.content = content

    @property
    def emitter(self):
        return self._emitter

    @emitter.setter
    def emitter(self, emitter):
        self._emitter = emitter

    @property
    def content(self):
        return self._content

    @content.setter
    def content(self, content):
        self._content = content
