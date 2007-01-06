# pylint: disable-msg=E0102,W0613,C0103
#we redefine listenToEvent several times to reinforce that it's a multimethod.
#we also have a lot of mandatory parameters flying about that we don't care
#about.
#also, it complains about the names a lot.
"""This class contains my very first NPC. It chats back!
"""
from grail2.multimethod import Multimethod
from grail2.events import BaseEvent
from grail2.actiondefs.system import UnfoundObjectEvent
from grail2.actiondefs.emote import lookUpAt, emote
from grail2.actiondefs.says import SpeakToSecondEvent, speakTo
from grail2.objects import MUDObject
from grail2.telnet import Listener
from twisted.internet.base import DelayedCall
from random import randrange

class ChattyNPC(Listener):
    """An NPC that chats back. I want to turn this into an Eliza clone someday.
    """

    def __init__(self, avatar):
        self.avatar = avatar
        Listener.__init__(self)

    listenToEvent = Multimethod()

@ChattyNPC.listenToEvent.register(ChattyNPC, BaseEvent, MUDObject)
def listenToEvent(self, obj, event):
    """Events we don't care about will come down to here, so just ignore them.
    """
    pass

def doafter(time, func, *args, **kwargs):
    """Do an action after a given amount of time. Convenience function.
    """
    return DelayedCall(time, func, args, kwargs,
                       lambda _: None, lambda _: None)

@ChattyNPC.listenToEvent.register(ChattyNPC, SpeakToSecondEvent, MUDObject)
def listenToEvent(self, obj, event):
    '''Someone has said something to us. It's only polite to respond!'''
    text = event.text
    if not text:
        doafter(randrange(2, 4), lookUpAt, self.avatar, event.actor)
        return
    doafter(randrange(2, 4), speakTo, self.avatar, event.actor,
            "Very interesting!")

@ChattyNPC.listenToEvent.register(ChattyNPC, UnfoundObjectEvent, MUDObject)
def listenToEvent(self, obj, event):
    '''Someone we tried to do something to wasn't there.'''
    emote(self.avatar,
          "You look up and around, as if searching for someone, but look down "
          "again soon after, not finding your quarry.",
          "~ looks up and around, as if searching for someone, but looks down "
          "again soon after, not finding their quarry.")
