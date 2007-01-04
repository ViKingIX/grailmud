'''Type-based multimethods, with support for call-next-method functionality.
'''
import bisect
from functional import partial
from grail2.orderedset import OrderedSet

class Not(object):
    '''A type's complement.'''

    def __init__(self, typ):
        self.typ = typ

class Union(object):
    '''The union of several types.'''

    def __init__(self, *types):
        self.types = types

class Intersection(object):
    '''The intersection of several types.'''

    def __init__(self, *types):
        self.types = types

def complement(a, b):
    '''The difference of two types.'''
    return Intersection(a, Not(b))

def _cooler_issubclass(child, parent):
    '''An issubclass that's aware of the above classes.'''
    #typically, where multimethods would be a boon, we can't use them because
    #we have to bootstrap.
    if isinstance(parent, Not):
        return not _cooler_issubclass(child, parent.typ)
    if isinstance(parent, Union):
        return any(_cooler_issubclass(child, typ) for typ in parent.types)
    if isinstance(parent, Intersection):
        return all(_cooler_issubclass(child, typ) for typ in parent.types)
    return issubclass(child, parent)

class Signature(object):
    '''A Signature of types for a function. Can be ordered, though it's only a
    partial ordering.
    '''

    def __init__(self, tsig):
        #Explicitly convert to tuple to prevent Bad Things from happening with
        #generator expressions.
        self.tsig = tuple(tsig)
    
    def __cmp__(self, other):
        if len(self.tsig) != len(other.tsig):
            return NotImplemented
        
        if self.tsig == other.tsig:
            return 0
        
        z = zip(self.tsig, other.tsig)
        #Is it just me, or is the argument order for issubclass completely
        #arbitrary? I've tripped up on that so many times - my preferred method
        #of turning it into a Haskell style infix thingy and then reading it
        #aloud ("b `issubclass` a") doesn't help. I think it ought to be renamed
        #'issubclassof' and the argument order reversed.
        if all(_cooler_issubclass(b, a) for a, b in z):
            return 1
        if all(_cooler_issubclass(a, b) for a, b in z):
            return -1
        
        #Can we even get here?
        return NotImplemented

    def __repr__(self):
        return "Signature%s" % repr(self.tsig)

    def __hash__(self):
        return hash(self.tsig)

class Multimethod(object):
    '''A function that can dispatch based on the types of all its arguments, not
    just the first one, like it is traditionally.
    '''

    def __init__(self):
        self.signatures = OrderedSet()
        self.s2fs = {}
        self.lastfunc = None
        self.next_method_stack = []

    def register(self, *sig):
        '''Takes a signature of types, and returns a function that takes a
        function, which registers the given function to the internal machinery
        with the signature.
        '''
        sig = Signature(sig)
        def functiongrabber(func):
            if func is self:
                #special case to allow stacking, eg for default options
                if self.lastfunc is None:
                    raise ValueError("This should not happen: lastfunc is None"
                                     " and func is self.")
                func = self.lastfunc
            #The magic is actually done here: self.signatures is always in
            #sorted order, so that when we iterate through it it's just a
            #matter of checking if the signature matches or not. Of course,
            #this means we need to -maintain- sorted order, so bisect.insort
            #is used to do the algorithmic lifting.
            if sig not in self.signatures:
                #If it's already in there, it'll be at the correct index.
                #But, if we do get an identically-signatured method definition,
                #the behaviour I think correct is to only have the very last
                #function defined with that signature called. An error would
                #also work, though.
                bisect.insort(self.signatures, sig)
            self.s2fs[sig] = func
            self.lastfunc = func
            return self
        return functiongrabber

    def __call__(self, *args):
        sig = Signature(type(arg) for arg in args)
        self.next_method_stack.append(iter(self.signatures))
        try:
            self._get_next_method(sig)(*args)
        finally:
            del self.next_method_stack[-1]

    def __get__(self, instance, owner):
        #Support for being used as a bound method.
        if instance is None:
            return self
        else:
            return partial(self, instance)

    def _fail(self):
        '''This is called when there's no matching type signature. Please, do
        override this.
        '''
        raise TypeError("No matching signature was found.")

    def _get_next_method(self, csig, noisy = True):
        '''Gets the next method from the stack of Signature-yielding iterables.
        '''
        #Here comes the clever bit: self.signatures is stored in a sorted order,
        #going from most to least specific type signatures, so we can simply
        #iterate through it comparing our signature with its elements and use
        #the first matching signature's function.
        for sig in self.next_method_stack[-1]:
            if sig >= csig:
                return self.s2fs[sig]
        if noisy:
            self._fail()

    def call_next_method(self, *args):
        '''Calls the next method down from the present one. Throws an error
        if it doesn't have a next method.
        '''
        self._call_next_method_helper(args, True)

    def call_next_method_quiet(self, *args):
        '''Like call_next_method, but it doesn't throw.'''
        self._call_next_method_helper(args, False)

    def _call_next_method_helper(self, args, noisy):
        sig = Signature(type(arg) for arg in args)
        if not self.next_method_stack:
            raise ValueError("Don't call this outside of a call to a "
                             "multimethod.")
        meth = self._get_next_method(sig, noisy)
        meth(*args)