class Listener(object):
    '''Base class for listeners.'''

    def __init__(self):
        self.listening = set()

    def register(self, source):
        """Register ourselves as a listener."""
        self.listening.add(source)

    def unregister(self, source):
        """Unregister ourselves as a listener."""
        self.listening.remove(source)

    def disconnecting(self, source):
        '''Acknowledge that an object has disconnected.'''
        source.removeListener(self)

    def transferControl(self, source, new):
        source.removeListener(self)
        new.addListener(self)
        
class ConnectionState(Listener):
    """Represents the state of the connection to the events as they collapse to
    text."""

    def __init__(self, telnet):
        self.telnet = telnet
        self.on_newline = False
        self.on_prompt = False
        self.want_prompt = True
        self.event = object()
        Listener.__init__(self)

    def avatar_get(self):
        return self.telnet.avatar

    def avatar_set(self, new):
        self.telnet.avatar = new

    avatar = property(avatar_get, avatar_set)

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
        self.event = object()

    def disconnecting(self, obj):
        if obj is self.avatar:
            #if this is the case, 
            for listening_to in self.listening:
                listening_to.removeListener(self)
            self.telnet.close()
        else:
            Listener.disconnecting(self, obj)

    def transferControl(self, source, other):
        if source is self.avatar:
            self.avatar = other
        Listener.transferControl(self, source, other)
