class MockListener(object):

    def __init__(self):
        self.received = []

    def listenToEvent(self, obj, event):
        self.received.append(event)

    def register(self, obj):
        pass

class SetupHelper(object):

    def setup_for_object(self, obj):
        if hasattr(self, 'room'):
            self.room.add(obj)
        obj.listener = MockListener()
        obj.addListener(obj.listener)
