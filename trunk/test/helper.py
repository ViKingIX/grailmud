from grail2.objects import MUDObject

class MockListener(object):

    def __init__(self):
        self.received = []

    def listenToEvent(self, obj, event):
        self.received.append(event)

    def register(self, obj):
        pass

class SetupHelper(object):

    constructor = lambda: MUDObject(None)

    def setUp(self):
        self.obj = self.constructor
        self.listener = MockListener()
        self.obj.addListener(self.listener)
