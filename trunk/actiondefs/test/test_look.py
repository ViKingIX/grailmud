from grail2.actiondefs import LookAtEvent, LookRoomEvent, lookDistributor, \
                              lookAt, lookRoom, register
from grail2.test.helper import SetupHelper
from grail2.objects import TargettableObject, ExitObject, NamedObject
from grail2.rooms import Room
from grail2.actiondefs.system import UnfoundEvent

def test_registration():
    d = {}
    register(d)
    assert d['l'] is lookDistributor
    assert d['look'] is lookDistributor

class TestEventSending(SetupHelper):

    def setUp(self):
        self.room = Room("Just outside a dark cave.", "")
        self.actor = TargettableObject("a decapitated knight",
                                       set('shiny', 'dead'),
                                       self.room)
        self.roomtarget = TargettableObject("a killer rabbit",
                                            set('bunny', 'fluffy', 'murderous'),
                                            self.room)
        self.invtarget = NamedObject("a surprised-looking decapitated head",
                                     "Boris", set("head", "dead"),
                                     self.actor.inventory)
        self.otherroom = Room("Just inside a dark cave.", "")
        self.exit = ExitObject(self.room, self.otherroom)

        self.setup_for_object(self.actor)

    def test_look_at_room_TargettableObject(self):
        lookAt(self.actor, self.roomtarget)

        assert self.actor.listener.received == [LookAtEvent(self.roomtarget)]

    def test_look_at_inventory_TargettableObject(self):
        lookAt(self.actor, self.invtarget)

        assert self.actor.listener.received == [LookAtEvent(self.invtarget)]

    def test_look_at_nowhere(self):
        lookAt(self.actor, MUDObject(None))

        assert self.actor.listener.received == [UnfoundEvent()]
    
