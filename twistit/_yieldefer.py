# Copyright (c) 2014 Stefan C. Mueller

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to
# deal in the Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
# sell copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, 
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER 
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING 
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
# IN THE SOFTWARE.

from twisted.internet import defer
from twisted.python import failure

def yieldefer(function):
    """
    Replacement for :func:`defer.inlineCallbacks` that supports cancellation.
    """
    defer.inlineCallbacks
    return lambda *args, **kwargs: _yielddefer(function, *args, **kwargs)

def _yielddefer(function, *args, **kwargs):
    """
    Called if a function decorated with :func:`yieldefer` is invoked.
    """
    
    retval = function(*args, **kwargs)
    
    if isinstance(retval, defer.Deferred):
        return retval
    
    if not (hasattr(retval, '__iter__') and 
            hasattr(retval, 'next') and 
            hasattr(retval, 'send') and 
            hasattr(retval, 'throw')):
        return defer.succeed(retval)
    
    iterator = retval
    
    
    def maybe_deferred(val):
        # We don't want exceptions to become twisted failures
        # because exceptions thrown by the generator methods
        # indicate exceptions thrown by the code _between_ the
        # yield statements or it indicates the end of the 
        # iteration.
        if isinstance(val, defer.Deferred):
            return val
        else:
            return defer.succeed(val)
    
    def success(value):
        try:
            d = maybe_deferred(iterator.send(value))
            d.addCallbacks(success, fail)
            return d
        except StopIteration:
            return None
        except defer._DefGen_Return as e:
            return e.value
    
    def fail(failure):
        try:
            d = maybe_deferred(failure.throwExceptionIntoGenerator(iterator))
            #d = iterator.throw(failure.value)
            d.addCallbacks(success, fail)
            return d
        except StopIteration:
            return None
        except defer._DefGen_Return as e:
            return e.value
        
    try:
        d = maybe_deferred(iterator.next())
        d.addCallbacks(success, fail)
    except StopIteration:
        d = defer.succeed(None)
    except:
        d = defer.fail()
        
    return d