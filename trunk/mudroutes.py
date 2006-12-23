import re
from itertools import izip
from pyparsing import *

curly_repeat = Combine('{' + Word(nums) +
                       Optional(Suppress(',') + Optional(Word(nums))) +
                       '}')

repeat_pattern = curly_repeat ^ '?' ^ '*' ^ '+'

specials = r'\(){[*?+'
unspecials = ''.join(x for x in printables if x not in specials)
escape = '\\'

escaped_special = Suppress(escape) + oneOf(list(specials))

def regular_action(_, res, _):
    return [re.escape(res[0]) + res[1]]

def capture_action(_, res, _):
    return ['?P<%s>%%s)%s' % tuple(res)]

regular_text = Combine(ZeroOrMore(oneOf(list(unspecials)) ^ escaped_special)) +\
               repeat_pattern
regular_text.setParseAction(regular_action)
capture_name = Suppress('[') + (Word(alphas) ^ '.') + Suppress(']') +\
               repeat_pattern
capture_name.setParseAction(capture_action)
regular_group = Suppress('(') + regular_text + Suppress(')') +\
                repeat_pattern
regular_group.setParseAction(regular_action)

expr = ZeroOrMore(regular_text ^ capture_name ^ regular_group)

class Mapper(object):

    def __init__(self):
        self.routesmap = []

    def register(self, route, **constraints):
        regex = route2regex(route, constraints)
        def get_fn(fn):
            self.routesmap.append((regex, fn))
            return fn
        return get_fn

    def connect(self, string, **kwargs):
        for regex, fn in self.routesmap:
            match = regex.match(string)
            if match:
                kwargs.update(match.groupdict())
                fn(**kwargs)
                break

def route2regex(route, constraints):
    res = ''.join(expr.parseString(route))
    return res % constraints

def peeksorted(seqs, cmp = None, key = None, reverse = False):
    firsts = izip(*seqs).next()
    f2s = dict(izip(firsts, seqs))
    for first in sorted(firsts, key, cmp, reverse):
        yield f2s[first]

def strip_empties(seqs):
    for seq in seqs:
        ts = tuple(seq)
        if ts:
            yield ts

def merge(*seqs, **kwargs):
    cmp = kwargs.pop('cmp', None)
    seqs = tuple(strip_empties(seqs))
    while seqs:
        iseqs = peeksorted(seqs, cmp = cmp)
        cur = iseqs.next()
        yield cur[0]
        seqs = tuple(strip_empties((cur[1:],) + tuple(iseqs)))
