from grail2.objects import MUDObject, TargettableObject, NamedObject, Player
from grail2.events import BaseEvent

class ListenerHelper(object):

    def __init__(self, obj):
        self.received = []
        self.flushed = False
        self.obj = obj
        self.obj.listener = self

    def register(self, obj):
        assert obj is self.obj
        assert self in obj.listeners

    def unregister(self, obj):
        assert obj is self.obj
        assert self not in obj.listeners

    def listenToEvent(self, obj, event):
        assert obj is self.obj
        self.received.append(event)

    def eventListenFlush(self, obj):
        assert obj is self.obj
        self.flushed = True

def test_register():
    obj = MUDObject(None)
    obj.addListener(ListenerHelper(obj))

def test_equality():
    m = MUDObject(None)
    assert m == m
    assert MUDObject(None) != m

def test_hashability():
    s = set([MUDObject(None), MUDObject(None)])
    assert len(s) == 2

class TesterForListening(object):

    def setUp(self):
        self.obj = MUDObject(None)
        self.obj.addListener(ListenerHelper(self.obj))
        
    def test_unregister(self):
        self.obj.removeListener(self.obj.listener)

    def test_event_passing(self):
        self.obj.receiveEvent(BaseEvent())
        assert self.obj.listener.received == [BaseEvent()]

    def test_event_flushing(self):
        self.obj.eventFlush()
        assert self.obj.listener.flushed

    def test_bad_unregister(self):
        self.obj.listeners.remove(self.obj.listener)
        try:
            self.obj.removeListener(self.obj.listener)
        except ValueError:
            pass
        else:
            assert False

    def test_bad_register(self):
        try:
            self.obj.addListener(self.obj.listener)
        except ValueError:
            pass
        else:
            assert False
