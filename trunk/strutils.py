from string import printable, whitespace, ascii_letters, digits, punctuation
from pyparsing import *

nwprintable = ''.join(s for s in printable if s not in whitespace)

alnumspace = ascii_letters + digits + whitespace

def sanitise(string):
    #strip non-alphabetic/space chars from string.
    return ''.join(s for s in string if s.isalpha() or s == ' ')

def alphatise(string):
    #strip non-alphabetic chars from string.
    return ''.join(s for s in string if s.isalpha())

def safetise(string):
    #strip non-printable chars from the string
    return ''.join(s for s in string if s in printable)

def articleise(string):
    if string[0] in 'aeiou':
        return 'an ' + string
    return 'a ' + string

def capitalise(s):
    s.capitalize()

#it takes prefixes of symbols to be the 'head word'.
_hwspattern = (Word(punctuation) + Optional(Word(alnumspace))) | \
              (Optional(Word(nwprintable)) + Optional(Word(printable)))

def head_word_split(string):
    res = _hwspattern.parseString(string)
    if len(res) == 0:
        return ('', '')
    elif len(res) == 1:
        return (res[0], '')
    else:
        return res

def wsnormalisehelper(string):
    buf = ''
    for c in string:
        if c not in whitespace:
            buf += c
        elif buf:
            yield buf
            buf = ''
    yield buf

def wsnormalise(string):
    return ' '.join(wsnormalisehelper(string))
