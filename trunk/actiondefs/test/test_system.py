from grail2.actiondefs.system import UnfoundObjectEvent, PermissionDeniedEvent,\
                                     BadSyntaxEvent, BlankLineEvent, blankLine,\
                                     permissionDenied, badSyntax, \
                                     unfoundObject, register
from grail2.test.helper import SetupHelper

def test_registration():
    d = {}
    register(d)
    assert d[''] is blankLine

class TestEvents(SetupHelper):

    def test_bad_syntax_without_argument(self):
        badSyntax(self.obj)
        assert self.obj.listener.received == [BadSyntaxEvent(None)]

    def test_bad_syntax_with_argument(self):
        arg = "foo"
        badSyntax(self.obj, arg)
        assert self.obj.listener.received == [BadSyntaxEvent(arg)]

    def test_blank_line(self):
        blankLine(self.obj, "foo", None)
        assert self.obj.listener.received == [BlankLineEvent()]

    def test_permission_denied(self):
        permissionDenied(self.obj)
        assert self.obj.listener.received == [PermissionDeniedEvent()]
