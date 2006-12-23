from orderedset import OrderedSet

class UnfoundError(Exception):
    pass

class Room(object):

    def __init__(self, title, desc):
        self.contents = OrderedSet()
        self.title = title
        self.desc = desc

    def add(self, obj):
        self.contents.add(obj)

    def remove(self, obj):
        self.contents.remove(obj)

    def matchContent(self, attrs, count, test = (lambda x: True)):
        for obj in self.contents:
            if obj.match(attrs) and test(obj):
                if count == 0:
                    return obj
                else:
                    count -= 1
        raise UnfoundError()

    def __contains__(self, obj):
        return obj in self.contents
