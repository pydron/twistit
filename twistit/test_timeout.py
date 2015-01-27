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
import utwist

from twisted.internet import defer, task, reactor

class TestTimeout(unittest.TestCase):
    
    def test_immediate(self):
        d = defer.Deferred()
        d = twistit.timeout_deferred(d, 1)
        d.callback(42)
        self.assertEqual(42, extract_deferred(d))
        
    def test_success(self):
        d = defer.succeed(42)
        d = twistit.timeout_deferred(d, 1)
        self.assertEqual(42, extract_deferred(d))
        
    def test_failure(self):
        try:
            raise ValueError()
        except:
            d = defer.fail()
        d = twistit.timeout_deferred(d, 1)
        self.assertRaises(ValueError, extract_deferred, d)
        
    @utwist.with_reactor
    @twistit.yieldefer
    def test_timeout(self):
        d = defer.Deferred()
        d = twistit.timeout_deferred(d, 0.1)
        
        yield task.deferLater(reactor, 0.3, lambda :None)
        self.assertRaises(twistit.TimeoutError, extract_deferred, d)
        
    @utwist.with_reactor
    @twistit.yieldefer
    def test_delay(self):
        d = defer.Deferred()
        d = twistit.timeout_deferred(d, 0.3)
        
        yield task.deferLater(reactor, 0.1, d.callback, 42)
        self.assertEqual(42, extract_deferred(d))
        
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
    