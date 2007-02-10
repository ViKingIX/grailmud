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

import logging
from grail2.actiondefs.core import distributeEvent
from grail2.strutils import capitalise
from grail2.events import SystemEvent, GameEvent
from grail2.utils import promptcolour

class UnfoundObjectEvent(GameEvent):

    @promptcolour()
    def collapseToText(self, state, obj):
        state.sendEventLine("That object is not present.")

class BlankLineEvent(SystemEvent):

    def collapseToText(self, state, obj):
        state.forcePrompt()
        state.sendEventLine('')

class PermissionDeniedEvent(SystemEvent):

    @promptcolour("system")
    def collapseToText(self, state, obj):
        state.sendEventLine("Hey, you can't do that!")

class BadSyntaxEvent(SystemEvent):

    def __init__(self, expl):
        self.expl = expl

    @promptcolour("system")
    def collapseToText(self, state, obj):
        expl = "Couldn't parse that, I'm afraid."
        if self.expl is not None:
            expl = " ".join([expl, self.expl])
        state.sendEventLine(expl)

def blankLine(actor, text, info):
    actor.receiveEvent(BlankLineEvent())

def permissionDenied(actor):
    actor.receiveEvent(PermissionDeniedEvent())

def badSyntax(actor, expl = None):
    actor.receiveEvent(BadSyntaxEvent(expl))

def unfoundObject(actor):
    actor.receiveEvent(UnfoundObjectEvent())

def register(cdict):
    cdict[''] = blankLine
