
"""A couple of handy classes for the nitty-gritties of the telnet connection,
and keeping track of that sort of stuff.
"""
import logging
from functional import compose
from sha import sha
from twisted.conch.telnet import Telnet
from twisted.protocols.basic import LineOnlyReceiver
from grail2.objects import Player, BadPassword
from grail2.actions import get_actions
from grail2.actiondefs.system import logoffFinal, login
from grail2.listeners import ConnectionState
from grail2.strutils import sanitise, alphatise, safetise, articleise, \
                            wsnormalise

#some random vaguely related TODOs:
#-serialisation via dirty objects
#-heartbeat tick server (steal from Buyasta?)
#-referential integrity when MUDObjects go POOF
#-better cataloguing (at the very least, all MUDObjects by name)

class LoggerIn(Telnet, LineOnlyReceiver):
    """A class that calls a specific method, depending on what the last method
    called returned.
    """

    delimiter = '\n'

    def __init__(self, playercatalogue, startroom, ticker):
        Telnet.__init__(self)
        #LineOnlyReceiver doesn't have an __init__ method, weirdly.
        self.linestate = 'ignore'
        self.dispatchto = ChoiceHandler()
        self.ticker = ticker
        self.playercatalogue = playercatalogue
        self.startroom = startroom
        self.connection_state = None
        self.avatar = None

    applicationDataReceived = LineOnlyReceiver.dataReceived

    def lineReceived(self, line):
        """Receive a line of text and delegate it to the method asked for
        previously.
        """
        meth = getattr(self.dispatchto, 'line_%s' % self.linestate)
        logging.debug("Line %r received, putting %r for the ticker." %
                      (line, meth))
        self.ticker.add_command(meth)

    def close(self):
        """Convenience."""
        self.transport.loseConnection()

    def write(self, data):
        """Convenience."""
        logging.debug("Writing %r to the transport." % data)
        self.transport.write(data)

    def connectionMade(self):
        """The connection's been made, and send out the initial options."""
        Telnet.connectionMade(self)
        LineOnlyReceiver.connectionMade(self)
        self.dispatchto.line_initial()

    def connectionLost(self, reason):
        """Clean up and let the superclass handle it."""
        if self.avatar:
            logoffFinal(self.avatar)
        Telnet.connectionLost(self, reason)
        LineOnlyReceiver.connectionLost(self, reason)

class LineInfo(object):
    """A catch-all class for other useful information that needs to be handed
    to avatars with lines of commands.
    """

    def __init__(self, instigator = None): #XXX: probably other stuff to go
                                           #here too.
        self.instigator = instigator

class ConnectionHandler(object):

    def __init__(self, telnet):
        self.telnet = telnet

    def line_ignore(self, line):
        pass

    def write(self, text):
        self.telnet.write(text)

    def setstate(self, state):
        self.telnet.linestate = state

    def sethandler(self, handler):
        self.telnet.dispatchto = handler
        self.setstate('initial')

NEW_CHARACTER = 1
LOGIN = 2

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

class ChoiceHandler(ConnectionHandler):

    def line_initial(self):
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
            self.sethandler(CreationHandler(self.telnet))
        elif opt == LOGIN:
            self.write("What is your name?")
            self.sethandler(LoginHandler(self.telnet))

class CreationHandler(ConnectionHandler):

    def __init__(self, *args, **kwargs):
        self.name = None
        self.sdesc = None
        self.adjs = None
        self.passhash = None
        ConnectionHandler.__init__(self, *args, **kwargs)

    @strconstrained(corrector = alphatise)
    def line_initial(self, name):
        """The user's creating a new character. We've been given the name,
        so we ask for the password.
        """
        #XXX: checking if the name exists already.
        self.name = name
        self.write("Please enter a password for this character.")
        self.setstate('get_password')

    def line_get_password_new(self, line):
        """We've been given the password. Salt and hash it, then store the
        hash.
        """
        line = safetise(line)
        if len(line) <= 3:
            self.write("That password is not long enough.")
            return
        self.passhash = sha(line + self.name).digest()
        self.write("Please repeat your password.")
        self.setstate('repeat_password')

    def line_repeat_password(self, line):
        """Make sure the user can remember the password they've entered."""
        line = safetise(line)
        if sha(line + self.name).digest() != self.passhash:
            self.write("Those passwords don't match. Please enter a new one.")
            return 'get_password_new'
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
        avatar = Player(self.name, self.sdesc, self.adjs, get_actions(),
                        self.telnet.startroom)
        self.telnet.playercatalogue.add(avatar, self.passhash)
        self.sethandler(AvatarHandler(self.telnet, avatar))

class LoginHandler(ConnectionHandler):

    def __init__(self, telnet):
        self.name = None
        ConnectionHandler.__init__(self, telnet)
    
    @strconstrained(corrector = alphatise)
    def line_get_name_existing(self, line):
        """Logging in as an existing character, we've been given the name. We
        ask for the password next.
        """
        if self.telnet.playercatalogue.player_exists(line):
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
        passhash = sha(line + self.name).digest()
        try:
            avatar = self.telnet.playercatalogue.get(line, passhash)
        except BadPassword, err:
            self.write("That password is invalid. Goodbye!")
            self.telnet.connectionLost(err)
        else:
            self.sethandler(AvatarHandler(self.telnet, avatar))

class AvatarHandler(ConnectionHandler):

    def __init__(self, telnet, avatar):
        self.telnet = telnet
        self.avatar = avatar
        
        self.connection_state = ConnectionState(self.telnet)
        self.avatar.addListener(self.connection_state)
        self.telnet.startroom.add(self.avatar)
        login(self.avatar)
        self.connection_state.eventListenFlush(self.avatar)

    def line_initial(self, line):
        logging.debug('%r received, handling in avatar.' % line)
        try:
            self.avatar.receivedLine(line,
                                     LineInfo(instigator = self.avatar))
            self.avatar.eventFlush()
        except:
            logging.error('Unhandled error %e, closing session.')
            logoffFinal(self.avatar)
            raise
