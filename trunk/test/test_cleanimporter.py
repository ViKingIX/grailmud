from __future__ import with_statement

from grailmud.cleanimporter import CleanImporter
import string

def test_imported_names():
    with CleanImporter('string'):
        assert string.punctuation == punctuation
        assert string.capitalize == capitalize
        assert string.digits == digits

def test_cleanup():
    before = len(globals())
    with CleanImporter("string"):
        #this test is important: it makes sure this isn't a no-op
        assert len(globals()) != before
    assert len(globals()) == before

def test_no_clobbering():
    #need to do this because CleanImporter only adds it to the global scope.
    s = '''
punctuation = 'foo'
with CleanImporter("string"):
    pass
assert punctuation == 'foo'
'''
    exec s in globals(), locals()

#XXX: some tests for the import reimplementation.
