"""This class contains my very first NPC. It chats back!
"""

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

from grail2.multimethod import Multimethod
from grail2.events import BaseEvent
from grail2.actiondefs.system import UnfoundObjectEvent
from grail2.actiondefs.emote import yanked_emotes, emote
from grail2.actiondefs.says import SpeakToSecondEvent, speakTo
from grail2.objects import MUDObject
from grail2.listeners import Listener
from grail2.npcs.elizaimpl import Therapist

class ChattyListener(Listener):
    """An NPC that psychoanalyses you.

    In communist Russia, you psychoanalyse an NPC!
    (or is that debugging?)
    """

    def __init__(self, avatar):
        self.avatar = avatar
        Listener.__init__(self)
        #ideally, each individual object would be given its own therapist on
        #demand, but that would require some way of keeping referential
        #integrity intact if they're removed from the gameworld.
        self.lastchatted = None
        self.therapist = None

    listenToEvent = Multimethod()

@ChattyListener.listenToEvent.register(ChattyListener, MUDObject, BaseEvent)
def listenToEvent(self, obj, event):
    """Events we don't care about will come down to here, so just ignore them.
    """
    pass

@ChattyListener.listenToEvent.register(ChattyListener, MUDObject,
                                       SpeakToSecondEvent)
def listenToEvent(self, obj, event):
    '''Someone has said something to us. It's only polite to respond!'''
    text = event.text
    actor = event.actor
    if not text:
        yanked_emotes['lookup'](self.avatar, actor)
        return
    if self.lastchatted is not actor:
        self.therapist = Therapist()
        self.lastchatted = actor
    speakTo(self.avatar, actor, self.therapist.chat(text))

@ChattyListener.listenToEvent.register(ChattyListener, MUDObject,
                                       UnfoundObjectEvent)
def listenToEvent(self, obj, event):
    '''Someone we tried to do something to wasn't there.'''
    emote(self.avatar,
          "You look up and around, as if searching for someone, but look down "
          "again soon after, not finding your quarry.",
          "~ looks up and around, as if searching for someone, but looks down "
          "again soon after, not finding their quarry.")

