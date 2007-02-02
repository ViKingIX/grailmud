from grail2.objects import MUDObject
from grail2.test.helper import SetupHelper
from grail2.actiondefs.more import displayMore, MoreEvent, NoMoreEvent, register
from grail2.morelimiter import MoreLimiter
from grail2.events import BaseEvent

def test_registration():
    d = {}
    register(d)
    assert d['more']

class TestMore(SetupHelper):

    def setUp(self):
        self.obj = MUDObject(None)
        self.obj.more_limiter = MoreLimiter(10)
        self.setup_for_object(self.obj)

    def test_more_event(self):
        data = "foo\n" * 29
        self.obj.chunks = self.obj.more_limiter.chunk(data)
        
        displayMore(self.obj)
        assert self.obj.listener.received == [MoreEvent('foo\n' * 10,
                                                        30, 20)]
        self.obj.listener.received = []
        displayMore(self.obj)
        assert self.obj.listener.received == [MoreEvent('foo\n' * 10,
                                                        30, 10)]
        self.obj.listener.received = []
        displayMore(self.obj)
        assert self.obj.listener.received == [MoreEvent('foo\n' * 9,
                                                        30, 0)]
        self.obj.listener.received = []

    def test_no_more_event(self):
        self.obj.chunks = self.obj.more_limiter.chunk('')

        displayMore(self.obj)
        self.obj.listener.received = []
        
        displayMore(self.obj)
        assert self.obj.listener.received == [NoMoreEvent()]