from grail2.actiondefs.deaf import DeafnessOnEvent, DeafnessOnAlreadyEvent, \
                                   DeafnessOffEvent, DeafnessOffAlreadyEvent, \
                                   deafDistributor, deafOn, deafOff, register, \
                                   syntaxmessage
from grail2.actiondefs.system import BadSyntaxEvent
from grail2.objects import MUDObject
from grail2.events import AudibleEvent
from grail2.test.helper import SetupHelper

def test_registration():
    d = {}
    register(d)
    assert d['deaf'] is deafDistributor

def test_deafness_turning_on():
    obj = MUDObject(None)
    deafOn(obj)
    assert obj.deaf

def test_deafness_turning_off():
    obj = MUDObject(None)
    obj.deaf = True
    deafOff(obj)
    assert not obj.deaf

def test_default_deafness():
    assert not MUDObject(None).deaf

class TestActionsAndEvents(SetupHelper):
        
    def test_deaf_on_success(self):
        deafOn(self.obj)

        assert self.listener.received == [DeafnessOnEvent()], \
               "self.listener.received is %r" % self.listener.received

    def test_deaf_on_failure(self):
        self.obj.deaf = True
        deafOn(self.obj)

        assert self.listener.received == [DeafnessOnAlreadyEvent()], \
               "self.listener.received is %r" % self.listener.received

    def test_deaf_off_failure(self):
        deafOff(self.obj)

        assert self.listener.received == [DeafnessOffAlreadyEvent()], \
               "self.listener.received is %r" % self.listener.received

    def test_deaf_off_success(self):
        self.obj.deaf = True
        deafOff(self.obj)

        assert self.listener.received == [DeafnessOffEvent()], \
               "self.listener.received is %r" % self.listener.received

    def test_deaf_on_success_with_parsing(self):
        deafDistributor(self.obj, 'on', None)

        assert self.listener.received == [DeafnessOnEvent()], \
               "self.listener.received is %r" % self.listener.received

    def test_deaf_on_failure_with_parsing(self):
        self.obj.deaf = True
        deafDistributor(self.obj, 'on', None)

        assert self.listener.received == [DeafnessOnAlreadyEvent()], \
               "self.listener.received is %r" % self.listener.received

    def test_deaf_off_failure_with_parsing(self):
        deafDistributor(self.obj, 'off', None)

        assert self.listener.received == [DeafnessOffAlreadyEvent()], \
               "self.listener.received is %r" % self.listener.received

    def test_deaf_off_success_with_parsing(self):
        self.obj.deaf = True
        deafDistributor(self.obj, 'off', None)

        assert self.listener.received == [DeafnessOffEvent()], \
               "self.listener.received is %r" % self.listener.received

    def test_interesting_but_correct_syntaxes(self):
        for cmd in ["  %s", "%s ", "\t%s  ", "%s\t", "\t %s", "\r\t%s",
                    "%s\r ", "%s \r   ", "%s", "%s \t", "%s foo",
                    "%sbar"]:
            
            deafDistributor(self.obj, cmd % 'on', None)
            deafDistributor(self.obj, cmd % 'off', None)
            assert self.listener.received == [DeafnessOnEvent(),
                                              DeafnessOffEvent()], \
                   "Failed on %r, self.listener.received is %r" % \
                   (cmd, self.listener.received)
            self.listener.received = []
            
            deafDistributor(self.obj, cmd % 'ON', None)
            deafDistributor(self.obj, cmd % 'OFF', None)
            assert self.listener.received == [DeafnessOnEvent(),
                                              DeafnessOffEvent()], \
                   "Failed on %r, self.listener.received is %r" % \
                   (cmd, self.listener.received)
            self.listener.received = []

    def test_wrong_syntax(self):
        for cmd in ['this', 'is', 'all wrong', 'and', 'should', 'not', 'turn',
                    'it on', 'or off']:
            deafDistributor(self.obj, cmd, None)
            assert self.listener.received == [BadSyntaxEvent(syntaxmessage)],\
                   "Failed on %r, self.listener.received is %r" % \
                   (cmd, self.listener.received)
            self.listener.received = []
