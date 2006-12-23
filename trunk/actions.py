import logging
from multimethods import Multimethod

from grail2.strutils import capitalise, printables, articleise

from grail2.objects import MUDObject, TargettableObject, Player, ExitObject



class WhoHereEvent(BaseEvent):

    def __init__(self, objects):
        self.objects = objects

    def collapseToText(self, state, obj):
        state.forcePrompt()
        state.setColourName("normal")
        state.sendEventLine("You see the following things present:")
        state.setColourName("people list")
        state.sendEventLine(', '.join(obj.sdesc for obj in self.objects))







#-------------------Wrappers-------------------

whoHerePattern = Suppress("here")

def whoHereWrapper(actor, text, info):
    whoHere(actor)



def whoDistributor(actor, text, info):
    try:
        whoHerePattern.parseString(text)
    except ParseException:
        unfoundObject(actor)
    else:
        whoHere(actor)



#-------------------Actual functions-------------------



def whoHere(actor):
    actor.receiveEvent(WhoHereEvent(actor.room.contents))



cmdict = {'qq': quitgame,
          'quit': quitgame,
          'who': whoDistributor,
          'wh': whoHereWrapper,
          'whohere': whoHereWrapper,
          '': blankLine,
          'look': look,
          'l': look,
          'say': speakWrapper,
          '"': speakWrapper,
          "'": speakWrapper,
          "say,": speakToWrapper,
          '",': speakToWrapper,
          "',": speakToWrapper}
