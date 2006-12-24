# pylint: disable-msg=C0103
#it complains about practically all of the names in this module...
"""A couple of handy classes for the nitty-gritties of the telnet connection,
and keeping track of that sort of stuff.
"""
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
    """A class that calls a specific method, depending on what the last method
    called returned.
    """

    delimiter = '\n'

    linestate = 'ignore'

    applicationDataReceived = LineOnlyReceiver.dataReceived

    def lineReceived(self, line):
        """Receive a line of text and delegate it to the method asked for
        previously.
        """
        #State monad anyone?
        meth = getattr(self, 'line_%s' % self.linestate)
        logging.debug("Line %r received, calling %r." % (line, meth))
        rval = meth(line)
        if rval is not None:
            self.linestate = rval

    def line_ignore(self, line):
        """A no-op, the default."""
        pass

    def connectionLost(self, reason):
        """The connection's been lost; notify the superclasses."""
        Telnet.connectionLost(self, reason)
        LineOnlyReceiver.connectionLost(self, reason)

    def connectionMade(self):
        """The connection's been made; notify the superclasses."""
        Telnet.connectionMade(self)
        LineOnlyReceiver.connectionMade(self)

    def close(self):
        """Convenience."""
        self.transport.loseConnection()

    def write(self, data):
        """Convenience."""
        logging.debug("Writing %r to the transport." % data)
        self.transport.write(data)

class NotAllowed(Exception):
    """The input was not acceptable, with an optional explanation."""

    def __init__(self, msg = "That input is invalid."):
        self.msg = msg

def toint(s):
    """Convert s to an int, or throw a NotAllowed."""
    try:
        return int(s)
    except ValueError:
        return NotAllowed("That couldn't be parsed as a number.")

def strconstrained(blankallowed = False, corrector = sanitise,
                   msg = 'Try actually writing something usable?'):
    """Decorator to ensure that the function is only called with acceptable
    input.
    """
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
        """The connection's been made, and send out the initial options."""
        StatefulTelnet.connectionMade(self)
        self.write("Welcome to GrailMUD.\r\n")
        self.write("Please choose:\r\n")
        self.write("1) Enter the game with a new character.\r\n")
        self.write("2) Log in as an existing character.\r\n")
        self.write("Please enter the number of your choice.\xff\xfa")

    #we want this here for normalisation purposes.
    @strconstrained(corrector = toint)
    def line_choice_made(self, opt):
        """The user's made their choice, so we pick the appropriate route: we
        either create a new character, or log in as an old one.
        """
        if opt == NEW_CHARACTER:
            self.write("Enter your name.")
            return 'get_name_new'
        elif opt == LOGIN:
            self.write("What is your name?")
            return 'get_name_existing'

    @strconstrained(corrector = alphatise)
    def line_get_name_existing(self, line):
        """Logging in as an existing character, we've been given the name. We
        ask for the password next.
        """
        if line in self.playercatalogue.byname:
            self.name = line
            self.write("Please enter your password.\xff\xfa")
            return 'get_password_existing'
        else:
            self.write("That name is not recognised. Please try again.")

    def line_get_password_existing(self, line):
        """We've been given the password. Check that it's correct, and then
        insert the appropriate avatar into the MUD.
        """
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
        """The user's creating a new character. We've been given the name,
        so we ask for the password.
        """
        self.name = line
        self.write("Please enter a password for this character.")
        return 'get_password_new'

    def line_get_password_new(self, line):
        """We've been given the password. Salt and hash it, then store the hash.
        """
        line = safetise(line)
        if len(line) <= 3:
            self.write("That password is not long enough.")
            return
        self.passhash = sha(line + self.name).digest()
        self.write("Enter your description (eg, 'short fat elf').")
        return 'get_sdesc'

    @strconstrained(corrector = compose(sanitise, wsnormalise))
    def line_get_sdesc(self, line):
        """Got the sdesc; ask for the adjectives."""
        self.sdesc = articleise(line)
        self.write("Enter a comma-separated list of words that can be used to "
                   "refer to you (eg, 'hairy tall troll') or a blank line to "
                   "use your description.")
        return 'get_adjs'

    @strconstrained(blankallowed = True,
                    corrector = compose(alphatise, wsnormalise))
    def line_get_adjs(self, line):
        """Got the adjectives; create the avatar, add it to the catalogue, and
        insert the avatar into the game.
        """
        if not line:
            line = self.sdesc
        self.adjs = set(line.split())
        avatar = Player(self.name, self.sdesc, self.adjs, cdict,
                        self.startroom)
        self.playercatalogue.add(avatar, self.passhash)
        self.initialise_avatar(avatar)
        return 'avatar'

    def initialise_avatar(self, avatar):
        """Get the avatar (and us!) into a working state."""
        self.avatar = avatar
        self.connection_state = ConnectionState(self)
        self.avatar.addListener(self.connection_state)
        self.connection_state.avatar = self.avatar
        self.startroom.add(self.avatar)
        login(self.avatar)
        self.connection_state.eventListenFlush(self.avatar)

    @strconstrained(blankallowed = True, corrector = safetise)
    def line_avatar(self, line):
        """Toss the line received to the avatar."""
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
        """Clean up and let the superclass handle it."""
        if self.avatar:
            logoffFinal(self.avatar)
        StatefulTelnet.connectionLost(self, reason)

class LineInfo(object):
    """A catch-all class for other useful information that needs to be handed
    to avatars with lines of commands.
    """

    def __init__(self, instigator = None): #XXX: probably other stuff to go
                                           #here too.
        self.instigator = instigator

class ConnectionState(object):
    """Represents the state of the connection to the events as they collapse to
    text."""

    def __init__(self, telnet):
        self.telnet = telnet
        self.listening = set()
        self.on_newline = False
        self.on_prompt = False
        self.want_prompt = True
        self.avatar = None

    def register(self, source):
        """Register ourselves as a listener."""
        self.listening.add(source)

    def unregister(self, source):
        """Unregister ourselves as a listener."""
        self.listening.remove(source)
        if not self.listening:
            self.telnet.close()

    def sendIACGA(self):
        """Write an IAC GA (go-ahead) code to the telnet connection."""
        self.telnet.write('\xFF\xFA')

    def sendPrompt(self):
        """Send a prompt, plus an IAC GA (-without- a trailing newline)."""
        logging.debug("Sending a prompt.")
        self.forceNewline()
        self.telnet.write('-->')
        self.sendIACGA()
        self.on_prompt = True
        self.want_prompt = True
        self.on_newline = False

    def forcePrompt(self):
        """Ensure we are on a prompt. May be a noop."""
        if not self.on_prompt:
            self.sendPrompt()

    def sendEventLine(self, line):
        """Send a line, with \\r\\n appended."""
        self.sendEventData(line + '\r\n')

    def sendEventData(self, data):
        """Write a blob of data to the telnet connection. Sets self.on_prompt to
        False, and on_newline to the appropriate value.
        """
        self.telnet.write(data)
        logging.debug("%r written." % data)
        self.on_prompt = False
        self.on_newline = data[-2:] == '\r\n'

    def dontWantPrompt(self):
        """We don't want a prompt next flush."""
        self.want_prompt = False

    def setColourName(self, colour):
        """Set our colour output to a predefined one."""
        pass #XXX

    def forceNewline(self):
        """Ensure we're on a newline."""
        if not self.on_newline:
            self.telnet.write('\r\n')
            self.on_newline = True

    def forcePromptNL(self):
        """Ensure we're on a prompt-newline."""
        self.forcePrompt()
        self.forceNewline()

    def listenToEvent(self, obj, event):
        """Collapse an event to text."""
        logging.debug("Handling event %r." % event)
        event.collapseToText(self, self.avatar)

    def eventListenFlush(self, obj):
        """Send off a final prompt to finish off the events."""
        logging.debug("Flushing the events, and stuff.")
        if self.want_prompt:
            self.sendPrompt()
        self.want_prompt = True
