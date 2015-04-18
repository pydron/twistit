# Copyright (C) 2015 Stefan C. Mueller

"""
Tools for testing twisted code.
"""
from twisted.python import failure

class NotCalledError(Exception):
    def __init__(self):
        Exception.__init__(self, "Expected deferred to be finished by now.")

def has_result(d):
    """
    Returns `True` if adding a callback now would cause that callback to
    be invoked immediately. `False` if the deferred is waiting for the value.
    """
    return d.called and not d.paused

def extract(d):
    """
    Returns the value the given deferred was called back with or
    raise the exception the deferred errbacked with. if the
    deferred hasn't been called, a :class:`NotCalledError` is raised.
    """
    if not has_result(d):
        raise NotCalledError()
    else:
        result = []
        def callback(value):
            result.append(value)
        d.addBoth(callback)
        
        result = result[0]
        if isinstance(result, failure.Failure):
            result.raiseException()
        else:
            return result
    
    