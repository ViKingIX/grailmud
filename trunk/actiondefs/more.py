from grail2.events import SystemEvent
from grail2.utils import promptcolour

class MoreEvent(SystemEvent):

    def __init__(self, text, initial, current):
        self.text = text
        self.initial = initial
        self.current = current

    @promptcolour()
    def collapseToText(self, state, obj):
        state.sendEventLine(self.text)
        state.sendEventLine("Type MORE to continue reading -- %d lines left "
                            "to show, out of %d." %
                            (self.current, self.initial))

class NoMoreEvent(SystemEvent):

    @promptcolour()
    def collapseToText(self, state, obj):
        state.sendEventLine("There is no more. Don't both asking for any.")

def displayMore(actor):
    try:
        data = actor.chunks.next()
    except StopIteration:
        actor.receiveEvent(NoMoreEvent())
    else:
        actor.receiveEvent(MoreEvent(data, actor.chunks.initial_lines,
                                     actor.chunks.lines_left))

def register(cdict):
    cdict['more'] = lambda actor, text, info: displayMore(actor)
