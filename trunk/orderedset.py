from sets import BaseSet

_set_types = (set, frozenset, BaseSet)

def _operand_set_checking(fn):
    def func(self, other):
        if not isinstance(other, _set_types):
            return NotImplemented
        res = fn(self, other)
        if res is None:
            return self
        return res
    return func

class OrderedSet(list):
    '''A collection of unique elements, kept in order. Mutable.'''
    #Possibly todo: write an immutable ordered set? Inheriting from tuple?
    
    def __init__(self, seq = ()):
        list.__init__(self)
        self.extend(seq)

    _overwrite = list.__init__

    def __repr__(self):
        return '%s(%s)' % (type(self).__name__, list.__repr__(self))

    def __setslice__(self, i, j, sequence):
        self.__setitem__(slice(i, j), sequence)

    def __setitem__(self, key, value):
        if isinstance(key, slice):
            res = self.intersection(value)
        else:
            res = value in self
        if res:
            raise ValueError('Item is already a member.')
        list.__setitem__(self, key, value)

    def __getitem__(self, key):
        res = list.__getitem__(self, key)
        if isinstance(key, slice):
            return OrderedSet(res)
        return res

    def __getslice__(self, i, j):
        return self.__getitem__(slice(i, j))

    #List methods, suitably wrapped and checked.

    def append(self, item):
        '''Append an element to the end of the ordered set.

        Quietly returns if it is already a member.
        '''
        if item in self:
            #raise ValueError("Item is already a member.")
            return #silently ignore.
                   #XXX: strict option?
        list.append(self, item)

    def count(self, value):
        '''Return the number of times an element occurs.

        Due to the very nature of sets, this will either be 0 or 1.
        '''
        return int(value in self)

    def extend(self, values):
        '''Extend the ordered set with a sequence of elements.

        This preserves the order of the elements. Duplicates are silently
        ignored.
        '''
        for value in values:
            self.add(value)

    def insert(self, key, value):
        '''Set a given index to a value.

        Raises a ValueError if the element is already a member.
        '''
        #why not just self[key] = value?
        self[key:key] = value

    #methods for frozenset compatability.

    #These two could be done using itertools.imap and the boolean operations.
    def issubset(self, other):
        '''Returns True if a given set is a subset of the ordered set.'''
        if len(self) > len(other):
            return False
        for elem in self:
            if elem not in other:
                return False
        return True

    def issuperset(self, other):
        '''Returns True if a given set is a superset of the ordered set.'''
        if len(self) < len(other):
            return False
        for elem in other:
            if elem not in self:
                return False
        return True

    def union(self, other):
        res = self.copy()
        res.extend(other)
        return res

    def intersection(self, other):
        res = OrderedSet()
        if len(self) > len(other):
            #speed: this check is not needed other than to minimise the number
            #of iterations.
            other, self = self, other
        for elem in self:
            if elem in other:
                res.add(elem)
        return res

    def difference(self, other):
        res = OrderedSet()
        for elem in self:
            if elem not in other:
                res.add(elem)
        return res

    def symmetric_difference(self, other):
        res = self.difference(other)
        for elem in other:
            if elem not in self:
                res.add(elem)
        return res

    def copy(self):
        return OrderedSet(self)
    __copy__ = copy

    #Set methods.
    update = extend

    def intersection_update(self, other):
        self._overwrite(self.intersection(other))

    def difference_update(self, other):
        self._overwrite(self.difference(other))

    def symmetric_difference_update(self, other):
        self._overwrite(self.symmetric_difference(other))
        
    def add(self, elem):
        if elem not in self:
            list.append(self, elem)

    #remove is already implemented in the list inheritance: it'll raise the
    #wrong error, though (IndexError instead of KeyError). So we must wrap it,
    #making sure the error raised can be caught by IndexError and KeyError.
    def remove(self, elem):
        try:
            list.remove(self, elem)
        except IndexError:
            raise DualError

    def discard(self, elem):
        if elem in self:
            self.remove(elem)

    #ditto as for remove, but we can do some dispatching.
    def pop(self, index = None):
        if index is None:
            #if index is none, it might be a set method, so the error raised
            #must be caught by "except IndexError" and "except KeyError".
            try:
                list.pop(self, -1)
            except IndexError:
                raise DualError
        else:
            #if not, it's a list thing: IndexError is expected, and list.pop
            #will raise that anyway.
            list.pop(self, index)

    __or__ = _operand_set_checking(union)
    __and__ = _operand_set_checking(intersection)
    __sub__ = _operand_set_checking(difference)
    __xor__ = _operand_set_checking(symmetric_difference)
    __ior__ = _operand_set_checking(update)
    __iand__ = _operand_set_checking(intersection_update)
    __isub__ = _operand_set_checking(difference_update)
    __ixor__ = _operand_set_checking(symmetric_difference_update)

    def clear(self):
        self._overwrite([])

    #Comparisons are difficult, as sets and lists do wildly different things.
    #Since the list comparisons are undefined in the library reference, AFAIK,
    #and the set ones are, those are what OrderedSets will support.
    
    #Should equality just test for membership (ie, set-style), or should
    #position count as well (list-style)? Of course, I could always do
    #dispatching to sniff out sets and compare them according to set rules, and
    #then use the list style on everything else.
    #The problem here is that __eq__ is overloaded, with two fundamentally
    #different operations. What would be more handy is two wholly separate
    #comparison functions. Then, code writers could pick and choose.

    def __lt__(self, other):
        if len(self) >= len(other):
            return False
        return self.issubset(other)

    __ge__ = issuperset

    def __gt__(self, other):
        if len(self) <= len(other):
            return False
        return self.issuperset(other)

    __le__ = issubset

    def __eq__(self, other):
        if isinstance(other, _set_types):
            return self.setcompare(other)
        else:
            return self.listcompare(other)

    listcompare = list.__eq__

    #we can't convert to set because we might have unhashable elements.
    #This assumes that neither operand will have non-unique elements.
    #obviously, we can't have non-unique elements, but they might.
    def setcompare(self, other):
        return set(self) == other

    def __ne__(self, other):
        return not (self == other)

    #my convenience methods.
    def rmapp(self, elem):
        try:
            self.remove(elem)
        except IndexError:
            pass
        self.append(elem)


class DualError(KeyError, IndexError):
    pass


OSet = OrderedSet
