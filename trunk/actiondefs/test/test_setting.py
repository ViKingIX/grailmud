from grail2.test.helper import SetupHelper
from grail2.actiondefs.setting import LDescSetEvent, setDistribute, setLDesc, \
                                      register
from grail2.objects import TargettableObject
from grail2.actiondefs.system import BadSyntaxEvent

def test_registration():
    assert cdict['set'] is setDistribute

def test_default_ldesc():
    assert TargettableObject("a fat elf", set(), None).ldesc == \
           "a fat elf. Nothing more."

def test_ldesc_setting():
    obj = TargettableObject("a fat elf", set(), None)
    desc = "A really really fat elf."
    setLDesc(obj, desc)
    assert obj.ldesc == desc

class TestEvents(SetupHelper):

    def setUp(self):
        self.obj = TargettableObject("a fat elf", set(), None)
        self.setup_for_object(self.obj)

    def test_ldesc_event(self):
        desc = "foo bar"
        setLDesc(self.obj, desc)
        assert self.obj.listener.received == [LDescSetEvent(desc)]

    def test_parsing_ldesc(self):
        desc = "foo bar"
        setDistribute(self.obj, "ldesc %s" % desc, None)
        assert self.obj.listener.received == [LDescSetEvent(desc)]

    def test_bad_syntaxes(self):
        for evilbad in ["foo", "bar baz", "quuux"]:
            setDistribute(self.obj, evilbad, None)
            assert self.obj.listener.received == \
                                     [BadSyntaxEvent(syntax_message % evilbad)]
            
