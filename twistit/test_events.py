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

class TestEvents(unittest.TestCase):
    """
    Unit tests for :class:`twistit.Event`.
    """
    
    def test_no_cb(self):
        target = twistit.Event()
        target.fire(42)
    
    def test_one_cb(self):
        result = [None]
        def cb(value):
            result[0] = value
        
        target = twistit.Event()
        target.add_callback(cb)
        target.fire(42)
        
        self.assertEqual(42, result[0])
        
    def test_two_cb(self):
        result = [None, None]
        def cb0(value):
            result[0] = value
        def cb1(value):
            result[1] = value
        
        target = twistit.Event()
        target.add_callback(cb0)
        target.add_callback(cb1)
        target.fire(42)
        
        self.assertEqual([42,42], result)
        
    def test_remove(self):
        result = [None]
        def cb(value):
            result[0] = value
        
        target = twistit.Event()
        target.add_callback(cb)
        target.remove_callback(cb)
        target.fire(42)
        self.assertEqual(None, result[0])
        
    def test_next_event(self):
        result = [None]
        def cb(value):
            result[0] = value
            
        target = twistit.Event()
        d = target.next_event()
        d.addCallback(cb)
        target.fire(42)
        self.assertEqual(42, result[0])
        
    def test_next_event_nextevent(self):
        result = [None]
        def cb(value):
            result[0] = value
            
        target = twistit.Event()
        d = target.next_event()
        d.addCallback(cb)
        target.fire(42)
        target.fire(43)
        self.assertEqual(42, result[0])
        
    def test_derive(self):
        result = [None, None]
        def cb0(value):
            result[0] = value
        def cb1(value):
            result[1] = value
        
        target = twistit.Event()
        target.add_callback(cb0)
        
        derived = target.derive(lambda x:2*x)
        derived.add_callback(cb1)
        
        target.fire(42)
        
        self.assertEqual([42,84], result)
