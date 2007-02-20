__copyright__ = """Copyright 2007 Sam Pointon"""

__licence__ = """
This file is part of grailmud.

grailmud is free software; you can redistribute it and/or modify it under the
terms of the GNU General Public License as published by the Free Software
Foundation; either version 2 of the License, or (at your option) any later
version.

grailmud is distributed in the hope that it will be useful, but WITHOUT ANY
WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
A PARTICULAR PURPOSE.  See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with
grailmud (in the file named LICENSE); if not, write to the Free Software
Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA 02110-1301  USA
"""

from grailmud.actiondefs.targetting import register, TargetSetEvent, TargetClearedEvent, TargetAlreadyClearedEvent, TargetListEvent, target_set_pattern, target_clear_pattern, target_list_pattern, targetDistributor, targetSet, targetList, targetClear
from grailmud.objects import MUDObject
from grailmud.actiondefs.system import BadSyntaxEvent
from grailmud.events import BaseEvent
from pyparsing import ParseException

def test_registering():
    d = {}
    register(d)
    assert d['target'] is targetDistributor

def test_events_are_subclasses_of_BaseEvent():
    for cls in [TargetSetEvent, TargetClearedEvent, TargetAlreadyClearedEvent, TargetListEvent]:
        assert issubclass(cls, BaseEvent)

def shouldraise(exc):
    def funcgetter(func):
        def doerfunc(*args, **kwargs):
            try:
                res = func(*args, **kwargs)
            except exc:
                pass
            else:
                assert False, "got %r returned instead" % res
        return doerfunc
    return funcgetter

class Testtarget_set_pattern(object):

    def test_doesnt_blow_up_on_good_input(self):
        target_set_pattern.parseString("set $foo to bar baz")

    @shouldraise(ParseException)
    def test_blows_up_on_missing_dollar(self):
        target_set_pattern.parseString("set foo to bar")

    def test_two_names_captured(self):
        assert len(target_set_pattern.parseString("set $foo to bar baz")) == 2

class Testtarget_clear_pattern(object):

    def test_doesnt_blow_up_on_good_input(self):
        target_clear_pattern.parseString("clear $foo")

    @shouldraise(ParseException)
    def test_blows_up_on_missing_dollar(self):
        target_clear_pattern.parseString("clear foo")

    def test_one_name_captured(self):
        assert len(target_clear_pattern.parseString("clear $foo")) == 1

class Testtarget_list_pattern(object):

    def test_doesnt_blow_up_on_good_input(self):
        target_list_pattern.parseString("list")

    def test_no_capture(self):
        assert not len(target_list_pattern.parseString("list"))



