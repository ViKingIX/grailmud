import logging
from functional import compose
from sha import sha
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

class NotAllowed(Exception):

    def __init__(self, msg = "That input is invalid."):
        self.msg = msg

def toint(s):
    try:
        return int(s)
    except TypeError:
        return NotAllowed("That couldn't be parsed as a number.")

def strconstrained(blankallowed = False, corrector = sanitise,
                   msg = 'Try actually writing something usable?'):
    def constrained(fn):
        def checker(self, line):
            try:
                line = corrector(line.lower())
            except NotAllowed, e:
                self.write(e.msg)
            else:
                if not blankallowed and not line:
                    self.write(msg)
                    return
                return fn(self, line)
        return checker
    return constrained

NEW_CHARACTER = 1
LOGIN = 2

class LoggerIn(StatefulTelnet):

    linestate = 'choice_made'
    avatar = None

    def connectionMade(self):
        StatefulTelnet.connectionMade(self)
        self.write("Welcome to GrailMUD.\r\n")
        self.write("Please choose:\r\n")
        self.write("1) Enter the game with a new character.\r\n")
        self.write("2) Log in as an existing character.\r\n")
        self.write("Please enter the number of your choice.\xff\xfa")

    #we want this here for normalisation purposes.
    @strconstrained(corrector = toint)
    def line_choice_made(self, opt):
        if opt == NEW_CHARACTER:
            self.write("Enter your name.")
            return 'get_name_new'
        elif opt == LOGIN:
            self.write("What is your name?")
            return 'get_name_existing'

    @strconstrained(corrector = alphatise)
    def line_get_name_existing(self, line):
        if line in self.playercatalogue.byname:
            self.name = line
            self.write("Please enter your password.\xff\xfa")
            return 'get_password_existing'
        else:
            self.write("That name is not recognised. Please try again.")

    def line_get_password_existing(self, line):
        line = safetise(line)
        if len(line) <= 3:
            self.write("That password is not long enough.")
            return
        passhash = sha(line + self.name).digest()
        if passhash != self.playercatalogue.passhashes[self.name]:
            self.write("That password is invalid. Goodbye!")
            self.connectionLost('bad password')
            return
        avatar = self.playercatalogue.byname[self.name]
        self.initialise_avatar(avatar)
        return 'avatar'

    @strconstrained(corrector = alphatise)
    def line_get_name_new(self, line):
        self.name = line
        self.write("Please enter a password for this character.")
        return 'get_password_new'

    def get_password_new(self, line):
        line = safetise(line)
        if len(line) <= 3:
            self.write("That password is not long enough.")
            return
        self.passhash = sha(line + self.name).digest()
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
        avatar = Player(self.name, self.sdesc, self.adjs, cdict,
                        self.startroom)
        self.playercatalogue.add(avatar, self.passhash)
        self.initialise_avatar(avatar)
        return 'avatar'

    def initialise_avatar(self, avatar):
        self.avatar = avatar
        self.connection_state = ConnectionState(self)
        self.avatar.addListener(self.connection_state)
        self.connection_state.avatar = self.avatar
        self.startroom.add(self.avatar)
        login(self.avatar)
        self.connection_state.eventListenFlush(self.avatar)

    @strconstrained(blankallowed = True, corrector = safetise)
    def line_avatar(self, line):
        saneline = sanitise(line)
        logging.debug('%r received, handling in avatar.' % saneline)
        try:
            self.avatar.receivedLine(saneline,
                                     LineInfo(instigator = self.avatar))
            self.avatar.eventFlush()
        except:
            logging.error('Unhandled error %e, closing session.')
            logoffFinal(self.avatar)
            raise

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
