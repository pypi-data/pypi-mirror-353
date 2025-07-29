from inspect import isgenerator, isgeneratorfunction
from bscript import Failure

def _iter(t):
    if isgeneratorfunction(t):
        t_inst = t()
        yield from t_inst
    else:
        while (r := t()): yield r

def sequence(*tasks):
    for t in tasks:
        yield from _iter(t)

def fallback(*tasks):
    for t in tasks:
        try:
            yield from _iter(t)
            return
        except Failure:
            pass

    raise Failure()

def forever(task):
    assert not isgenerator(task)
    while True:
        yield from _iter(task)

def decorate(task, *others):
    assert not isgeneratorfunction(task)
    assert not isgenerator(task)
    while True:
        if not (r := task()):
            for o in others:
                o()
        yield r
