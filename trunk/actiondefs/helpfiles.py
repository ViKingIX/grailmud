from grail2.events import SystemEvent
from grail2.utils import promptcolour
from grail2.strutils import wsnormalise

class HelpEvent(SystemEvent):

    def __init__(self, pagename, helppage):
        self.pagename = pagename
        self.helppage = helppage

    @promptcolour('normal', chunk = True)
    def collapseToText(self, state, obj):
        state.sendEventLine("HELP %s:" % self.pagename.upper())
        state.sendEventLine'')
        state.sendEventLine(self.helppage)

class HelpNotFoundEvent(SystemEvent):

    def __init__(self, pagename):
        self.pagename = pagename

    @promptcolour('normal')
    def collapseToText(self, state, obj):
        state.sendEventLine("No help was found on '%s'." % self.pagename)

def helpGetter(hdict):
    def realHelp(actor, text):
        #maybe TODO: implement some sort of adjective search thing. Or perhaps
        #a full-text search.
        text = wsnormalise(text.lower())
        if text in hdict:
            actor.receiveEvent(HelpEvent(text, hdict[text]))
        else:
            actor.receiveEvent(HelpNotFoundEvent(text))
    return realHelp

def get_helpfiles():
    '''Poke around in actiondefs for helpfiles. Maybe there ought to be other
    places to look, but it seems to be a good idea to have the action
    definitions near the helpfiles.
    '''
    #no, this is not anti-namespace pollution, this is breaking an import cycle
    from grail2.actions import modules
    for module in modules:
        if hasattr(module, 'help_register'):
            module.help_register(hdict)
    return hdict

def register(cdict):
    cdict['help'] = helpGetter(get_helpfiles())

def help_register(hdict):
    hdict['help'] = \
        'Just type HELP <phrase> to look up the help for it. A search will be '\
        'implemented someday.'
    
hdict = {}
