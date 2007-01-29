"""This class contains my very first NPC. It chats back!
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

