# pylint: disable-msg=C0103,W0613,W0231,R0903,W0611, E0102
#pylint and its finickity names and insistence that every single argument be
#used somewhere and that every single __init__ next-method is called and that
#classes need at least 2 methods...
#oh, and we import the whole of pyparsing for convenience's sake.
#we also redefine multimethods using the same name for emphasis and a lack of
#namespace pollution.
from pyparsing import *
from grail2.actiondefs.core import object_pattern, distributeEvent, \
                                   UnfoundMethod, get_from_rooms
from grail2.events import AudibleEvent
from grail2.actiondefs.system import unfoundObject, badSyntax
from grail2.rooms import UnfoundError
from grail2.strutils import capitalise, printables
from grail2.objects import MUDObject, TargettableObject
from grail2.utils import promptcolour

class SpeakNormalFirstEvent(AudibleEvent):

    def __init__(self, text):
        self.text = text

    @promptcolour("speech")
    def collapseToText(self, state, obj):
        if not self.text:
            state.sendEventLine("You open your mouth, as if to say something, "
                                "and stay like that looking silly for a few "
                                "seconds before you finally realise you have "
                                "nothing to say.")
        else:
            state.sendEventLine('You say, "%s"' % self.text)

class SpeakNormalThirdEvent(AudibleEvent):

    def __init__(self, actor, text):
        self.actor = actor
        self.text = text

    @promptcolour("speech")
    def collapseToText(self, state, obj):
        d = capitalise(self.actor.sdesc)
        if not self.text:
            state.sendEventLine("%s opens their mouth, as if to say something, "
                                "but rescinds after a few seconds of silly "
                                "gaping." % d)
        else:
            state.sendEventLine('%s says, "%s"' % (d, self.text))

class SpeakToFirstEvent(AudibleEvent):

    def __init__(self, target, text):
        self.target = target
        self.text = text

    @promptcolour("speech")
    def collapseToText(self, state, obj):
        d = self.target.sdesc
        if self.text:
            state.sendEventLine("You turn to %s and open your mouth, as if to "
                                "say something, but instead you gawp for a few "
                                "moments until you realise you have nothing to "
                                "say, and prompty close your mouth again."
                                % d)
        else:
            state.sendEventLine('You say to %s, "%s"' % (d, self.text))

class SpeakToSecondEvent(AudibleEvent):

    def __init__(self, actor, text):
        self.actor = actor
        self.text = text

    @promptcolour("speech")
    def collapseToText(self, state, obj):
        d = capitalise(self.actor.sdesc)
        if self.text:
            state.sendEventLine("%s turns to you and opens their mouth, but "
                                "says nothing, as if to catch a fly. Realising "
                                "how silly they look, they promptly clamp "
                                "their jaw shut after a few seconds." % d)
        else:
            state.sendEventLine('%s says to you, "%s"' % (d, self.text))
                                
class SpeakToThirdEvent(AudibleEvent):

    def __init__(self, actor, target, text):
        self.actor = actor
        self.target = target
        self.text = text

    @promptcolour("speech")
    def collapseToText(self, state, obj):
        da = capitalise(self.actor.sdesc)
        dt = capitalise(self.actor.sdesc)
        if self.text:
            state.sendEventLine("%s turns to %s and opens their mouth, but "
                                "says nothing, as if to catch a fly. Realising "
                                "how silly they look, they promptly clamp "
                                "their jaw shut after a few seconds."
                                % (da, dt))
        else:
            state.sendEventLine('%s says to %s, "%s"' % (da, dt, self.text))

speakToPattern = Group(object_pattern) + \
                 ',' + Group(ZeroOrMore(Word(printables)))

def speakToWrapper(actor, text, info):
    try:
        blob, saying = speakToPattern.parseString(text)
    except ParseException:
        badSyntax(actor, "Can't find the end of the target identifier. Use "
                         "',' at its end to specify it.")
        return
    try:
        target = get_from_rooms(blob, [actor.inventory, actor.room], info)
        speakTo(actor, target, saying)
    except UnfoundError:
        unfoundObject(actor)

def speak(actor, text):
    actor.receiveEvent(SpeakNormalFirstEvent(text))
    distributeEvent(actor.room, [actor], SpeakNormalThirdEvent(actor, text))

speakTo = UnfoundMethod()

@speakTo.register(MUDObject, TargettableObject, basestring)
def speakTo(actor, target, text):
    if target not in actor.room and target not in actor.inventory:
        unfoundObject(actor)
    else:
        actor.receiveEvent(SpeakToFirstEvent(target, text))
        target.receiveEvent(SpeakToSecondEvent(actor, text))
        distributeEvent(actor.room, [actor],
                        SpeakToThirdEvent(actor, target, text))

def register(cdict):
    cdict['say'] = cdict['"'] = cdict["'"] = \
                   lambda actor, text, info: speak(actor, text)
    cdict['say,'] = cdict["','"] = cdict['",'] = speakToWrapper
