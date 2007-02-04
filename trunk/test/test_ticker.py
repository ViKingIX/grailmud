from grail2.ticks import Ticker
import pickle
import grail2

def test_ticker_freq_setting():
    interval = 0.5
    t = Ticker(interval)
    assert t.freq == interval

def test_command_added():
    t = Ticker(1)
    #hackish
    called = []
    t.add_command(lambda: called.append(True))
    t.tick()
    assert called

def test_clears_doing_list():
    def doing_list_checker():
        assert not ticker.doing

    ticker = Ticker(1)
    ticker.add_command(doing_list_checker)
    ticker.tick()

def test_frequency_persists():
    freq = 1
    t = Ticker(freq)
    t = pickle.loads(pickle.dumps(t))
    assert t.freq == freq

def foo_function_1():
    pass

def foo_function_2():
    pass

def test_doing_persists():
    t = Ticker(1)
    t.add_command(foo_function_1)
    t.add_command(foo_function_2)
    olddoing = t.doing
    t = pickle.loads(pickle.dumps(t))
    assert t.doing == olddoing

class MockObjStore(object):

    def commit(self):
        pass

class MockInstance(object):

    def __init__(self):
        self.objstore = MockObjStore()

grail2.instance._bind(MockInstance())
