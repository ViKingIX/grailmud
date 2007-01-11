from collections import deque
from pyparsing import *
from string import punctuation, maketrans, printable
from random import randrange, choice
from grail2.strutils import wsnormalise
from grail2.utils import smartdict

napunctuation = ''.join(s for s in punctuation if s != "'")

def _prepare_line(line):
    stripped = line.translate(maketrans('', ''), napunctuation).lower()
    for in_, out in translations.iteritems():
        stripped = stripped.replace(in_, out)
    return stripped

class _NoResponse(Exception):
    pass

def _respondline(line, new = True):
    #would caching be a good idea?
    line = _prepare_line(line)
    hits = []
    for pattern, responsetemps in responses:
        try:
            result, = pattern.parseString(line)
        except ParseException:
            continue
        else:
            hits.append((responsetemps, result))
    if hits:
        temps, result = choice(hits)
        temp = choice(temps)
        return temp % smartdict({'res': bettertranslate(result,
                                                        reflections)})
    else:
        raise _NoResponse

class Therapist(object):
    '''A really silly and stupid ELIZA implementation.'''

    def __init__(self):
        self.prev_heard = deque()

    def chat(self, line):
        try:
            res = _respondline(line)
        except _NoResponse:
            res = self._nomatch()
        else:
            if line not in self.prev_heard:
                self.prev_heard.append(line)
                if len(self.prev_heard) > 10:
                    self.prev_heard.popleft()
        return res

    def _nomatch(self):
        if self.prev_heard and randrange(0, 2):
            line = choice(self.prev_heard)
            self.prev_heard.remove(line)
            #don't wrap this in a try block, because it shouldn't ever fail if
            #we get here. some sort of caching may be a good idea.
            return _respondline(line, new = False)
        else:
            return 'Please go on.'

translations = {'should': 'need to',
                'must': 'need to',
                "'ll": ' will',
                "'ve": ' have',
                "'d": ' could',
                "'m": ' am',
                "'re": ' are',
                "n't": ' not'}

reflections = {
  "am": "are",
  "you are": "i am",
  "was" : "were",
  "i": "you",
  "my": "your",
  "are": "am",
  "your": "my",
  "yours": "mine",
  "you": "me",
  "me": "you",
  "mine": "yours"
}

def bettertranslate(string, dictionary):
    #XXX: still doesn't bloody work.
    string = string.replace('%', '%%')
    for in_, out in dictionary.iteritems():
        string = re.sub(r'\b%s\b' % re.escape(in_),
                        '%%("%s".lower())s' % out.upper(),
                        string)
    return string % smartdict()

responses = [(Suppress('i') + Word(printable),
             ('Why do you %(res)s?',
              'Do you enjoy that?'))]