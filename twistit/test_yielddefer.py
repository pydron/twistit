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

import unittest
import twistit

from twisted.internet import defer

class TestYieldDefer(unittest.TestCase):
    """
    Unit tests for :func:`twistit.yielddefer`.
    """
    
    def test_not_a_generator(self):
        
        @twistit.yieldefer
        def mock():
            return 42
        
        d = mock()
        self.assertEqual(42, extract_deferred(d))
        
    
    def test_yield_value(self):
        
        @twistit.yieldefer
        def mock():
            retval = yield 42
            defer.returnValue(retval)
        
        d = mock()
        self.assertEqual(42, extract_deferred(d))
        
    def test_yield_value_twice(self):
        
        @twistit.yieldefer
        def mock():
            yield 41
            retval = yield 42
            defer.returnValue(retval)
        
        d = mock()
        self.assertEqual(42, extract_deferred(d))
        
    def test_yield_deferred(self):
        
        @twistit.yieldefer
        def mock():
            retval = yield defer.succeed(42)
            defer.returnValue(retval)
            
        d = mock()
        self.assertEqual(42, extract_deferred(d))
        
    def test_yield_deferred_twice(self):
        
        @twistit.yieldefer
        def mock():
            yield defer.succeed(41)
            retval = yield defer.succeed(42)
            defer.returnValue(retval)
            
        d = mock()
        self.assertEqual(42, extract_deferred(d))
        
        
    def test_throw_first(self):
        @twistit.yieldefer
        def mock():
            raise ValueError()
            yield defer.succeed(41)
            
        d = mock()
        self.assertRaises(ValueError, extract_deferred, d)
        
        
    def test_throw_second(self):
        @twistit.yieldefer
        def mock():
            yield defer.succeed(41)
            raise ValueError()
            
        d = mock()
        self.assertRaises(ValueError, extract_deferred, d)
    
    
    def test_cancel_pass(self):
        def canceller(d):
            pass
        
        blocking = defer.Deferred(canceller)
        
        @twistit.yieldefer
        def mock():
            yield blocking
            
        d = mock()
        d.cancel()
        self.assertRaises(defer.CancelledError, extract_deferred, d)


    def test_cancel_callback(self):
        def canceller(d):
            d.callback(42)
        
        blocking = defer.Deferred(canceller)
        
        @twistit.yieldefer
        def mock():
            retval = yield blocking
            defer.returnValue(retval)
            
        d = mock()
        d.cancel()
        self.assertEqual(42, extract_deferred(d))
        
    def test_cancel_errback(self):
        def canceller(d):
            try:
                raise StubError()
            except:
                d.errback()
        
        blocking = defer.Deferred(canceller)
        
        @twistit.yieldefer
        def mock():
            retval = yield blocking
            defer.returnValue(retval)
            
        d = mock()
        d.cancel()
        self.assertRaises(StubError, extract_deferred, d)
        

class StubError(Exception):
    pass
        
def extract_deferred(d):
    if not d.called:
        raise ValueError("Deferred has not yet been called")
    value = [None]
    error = [None]
    def success(v):
        value[0] = v
    def fail(v):
        error[0] = v
    d.addCallbacks(success, fail)
    
    if error[0]:
        error[0].raiseException()
    else:
        return value[0]
    
    