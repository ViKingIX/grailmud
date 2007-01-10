"""Contains some classes for dealing with containers."""
from grail2.orderedset import OrderedSet
from grail2.utils import InstanceTracker

class UnfoundError(Exception):
    """The object wasn't found."""
    pass

class Room(InstanceTracker):
    """A single container or 'room'."""

    def __init__(self, title, desc):
        self.contents = OrderedSet()
        self.title = title
        self.desc = desc
        InstanceTracker.__init__(self)

    def add(self, obj):
        """Add an object to the room. Does not modify the object to reflect
        this.
        """
        self.contents.add(obj)

    def remove(self, obj):
        """Remove an object from the room. Does not modify the object to reflect
        this.
        """
        self.contents.remove(obj)

    def matchContent(self, attrs, count, test = (lambda x: True)):
        """Looks for an object matching the given criteria in the room.

        attrs is a set of attributes the object must have. count is the number
        of the object in the room. test is an optional function to check the
        object up against.
        """
        for obj in self.contents:
            if obj.match(attrs) and test(obj):
                if count == 0:
                    return obj
                else:
                    count -= 1
        raise UnfoundError()

    def __contains__(self, obj):
        return obj in self.contents
