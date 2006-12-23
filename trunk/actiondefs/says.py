from pyparsing import *
from grail2.actiondefs.core import BaseEvent, object_pattern, distributeEvent
from grail2.strutils import capitalise, articleise, printables
from grail2.objects import MUDObject, TargettableObject

class SpeakNormalFirstEvent(BaseEvent):

    def __init__(self, text):
        self.text = text

    def collapseToText(self, state, obj):
        state.forcePrompt()
        state.setColourName("speech")
        if self.text:
            state.sendEventLine("You open your mouth, as if to say something, "
                                "and stay like that looking silly for a few "
                                "seconds before you finally realise you have "
                                "nothing to say.")
        else:
            state.sendEventLine('You say, "%s"' % self.text)

class SpeakNormalThirdEvent(BaseEvent):

    def __init__(self, actor, text):
        self.text = text

    def collapseToText(self, state, obj):
        d = capitalise(articleise(self.actor.sdesc))
        state.forcePrompt()
        state.setColourName("speech")
        if self.text:
            state.sendEventLine("%s opens their mouth, as if to say something, "
                                "but rescinds after a few seconds of silly "
                                "gaping." % d)
        else:
            state.sendEventLine('%s says, "%s"' % (d, self.text))

speakToPattern = Group(object_pattern) + \
                 ',' + Group(ZeroOrMore(Word(printables)))

def speakToWrapper(actor, text, info):
    try:
        raw_an, saying = speakToPattern.parseString(text)
    except ParseException:
        badSyntax(actor, "Can't find the end of the target identifier. Use "
                         "',' at its end to specify it.")
        return
    adjs, number = adjs_num_parse(raw_an)
    try:
        target = actor.room.matchContent(acjs, number)
        speakTo(actor, target, saying)
    except UnfoundError:
        unfoundObject(actor)

def speak(actor, text):
    actor.receiveEvent(SpeakNormalFirstEvent(text))
    distributeEvent(actor.room, [actor], SpeakNormalThirdEvent(actor, text))

@UnfoundMethod().register(MUDObject, TargettableObject, basestring)
def speakTo(actor, target, text):
    if target not in actor.room:
        unfoundObject(actor)
    else:
        actor.receiveEvent(SpeakToFirstEvent(target, text))
        target.receiveEvent(SpeakToSecondEvent(actor, target, text))
        distributeEvent(actor.room, [actor],
                        SpeakToThirdEvent(actor, target, text))

def register(cdict):
    cdict['say'] = cdict['"'] = cdict["'"] = \
                   lambda actor, text, info: speak(actor, text)
    cdict['say,'] = cdict["','"] = cdict['",'] = speakToWrapper
