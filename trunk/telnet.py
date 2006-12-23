import logging
from functional import compose
from twisted.conch.telnet import Telnet
from twisted.protocols.basic import LineOnlyReceiver
from grail2.objects import Player
from grail2.actions import cdict
from grail2.actiondefs.system import logoffFinal, login
from grail2.strutils import sanitise, alphatise, safetise, articleise, \
                            wsnormalise
from grail2.rooms import Room

class StatefulTelnet(Telnet, LineOnlyReceiver):

    delimiter = '\n'

    linestate = 'ignore'

    applicationDataReceived = LineOnlyReceiver.dataReceived

    def lineReceived(self, line):
        #State monad anyone?
        meth = getattr(self, 'line_%s' % self.linestate)
        logging.debug("Line %r received, calling %r." % (line, meth))
        rval = meth(line)
        if rval is not None:
            self.linestate = rval

    def line_ignore(self, line):
        pass

    def connectionLost(self, reason):
        Telnet.connectionLost(self, reason)
        LineOnlyReceiver.connectionLost(self, reason)

    def connectionMade(self):
        Telnet.connectionMade(self)
        LineOnlyReceiver.connectionMade(self)

    def close(self):
        self.transport.loseConnection()

    def write(self, data):
        logging.debug("Writing %r to the transport." % data)
        self.transport.write(data)

    def sendIACGA(self):
        self.transport.write('\xff\xfa')

def strconstrained(blankallowed = False, corrector = sanitise):
    def constrained(fn):
        def checker(self, line):
            line = corrector(line.lower())
            if not blankallowed and not line:
                self.write('Try actually writing something usable?')
                return
            return fn(self, line)
        return checker
    return constrained

class LoggerIn(StatefulTelnet):

    linestate = 'get_name'
    avatar = None
    startroom = Room("A very plain room",
                     "This is a plain room. The sky is an overcast grey, but "
                     "without an interesting pattern of clouds in it. The "
                     "ground is an anonymous grey dirt, compacted by the "
                     "stomping of a million different feet into a featureless "
                     "plain, stretching as far as you can see, the greyness of "
                     "the ground and the greyness of the sky melding at the "
                     "horizon, denying itself even the interestingness of a "
                     "sharp contrast between ground and sky.")

    def connectionMade(self):
        StatefulTelnet.connectionMade(self)
        self.transport.write("Enter your name.")

    @strconstrained(corrector = alphatise)
    def line_get_name(self, line):
        self.name = line
        self.write("Enter your description (eg, 'short fat elf').")
        return 'get_sdesc'

    @strconstrained(corrector = compose(sanitise, wsnormalise))
    def line_get_sdesc(self, line):
        self.sdesc = articleise(line)
        self.write("Enter a comma-separated list of words that can be used to "
                   "refer to you (eg, 'hairy tall troll') or a blank line to "
                   "use your description.")
        return 'get_adjs'

    @strconstrained(blankallowed = True,
                    corrector = compose(alphatise, wsnormalise))
    def line_get_adjs(self, line):
        if not line:
            line = self.sdesc
        self.adjs = set(line.split())
        self.connection_state = ConnectionState(self)
        self.avatar = Player(self.connection_state, self.name, self.sdesc,
                             self.adjs, cdict, self.startroom)
        self.connection_state.avatar = self.avatar
        self.startroom.add(self.avatar)
        login(self.avatar, '')
        self.connection_state.eventListenFlush(self.avatar)
        return 'avatar'

    @strconstrained(blankallowed = True, corrector = safetise)
    def line_avatar(self, line):
        saneline = sanitise(line)
        logging.debug('%r received, handling in avatar.' % saneline)
        self.avatar.receivedLine(saneline,
                                 LineInfo(instigator = self.avatar))
        self.avatar.eventFlush()

    def connectionLost(self, reason):
        if self.avatar:
            logoffFinal(self.avatar)
        StatefulTelnet.connectionLost(self, reason)

class LineInfo(object):

    def __init__(self, instigator = None): #XXX: probably other stuff to go
                                           #here too.
        self.instigator = instigator

class ConnectionState(object):

    def __init__(self, telnet):
        self.telnet = telnet
        self.listening = set()
        self.on_newline = False
        self.on_prompt = False
        self.want_prompt = True
        self.avatar = None

    def register(self, source):
        self.listening.add(source)

    def unregister(self, source):
        self.listening.remove(source)
        if not self.listening:
            self.telnet.close()

    def sendIACGA(self):
        self.telnet.write('\xFF\xFA')

    def sendPrompt(self):
        logging.debug("Sending a prompt.")
        self.forceNewline()
        self.telnet.write('-->')
        self.sendIACGA()
        self.on_prompt = True
        self.want_prompt = True
        self.on_newline = False

    def forcePrompt(self):
        if not self.on_prompt:
            self.sendPrompt()

    def sendEventLine(self, line):
        self.sendEventData(line + '\r\n')

    def sendEventData(self, data):
        self.telnet.write(data)
        logging.debug("%r written." % data)
        self.on_prompt = False
        self.on_newline = data[-2:] == '\r\n'

    def dontWantPrompt(self):
        self.want_prompt = False

    def setColourName(self, colour):
        pass #XXX

    def forceNewline(self):
        if not self.on_newline:
            self.telnet.write('\r\n')
            self.on_newline = True

    def forcePromptNL(self):
        self.forcePrompt()
        self.forceNewline()

    def listenToEvent(self, obj, event):
        logging.debug("Handling event %r." % event)
        event.collapseToText(self, self.avatar)

    def eventListenFlush(self, obj):
        logging.debug("Flushing the events, and stuff.")
        if self.want_prompt:
            self.sendPrompt()
        self.want_prompt = True
