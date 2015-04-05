# Copyright (C) 2015 Stefan C. Mueller

import unittest
import twistit
from twisted.internet import defer
from twisted.python import failure

class TestOnErrorClose(unittest.TestCase):
    
    def setUp(self):
        self.msg = None
    
    def log(self, msg):
        self.msg = msg
    
    def test_no_error(self):
        
        class Protocol(object):
            def __init__(self):
                self.transport = MockAbortableTransport()
                self.msg = None
                
            def log(self, msg):
                self.msg = msg
            
            @twistit.on_error_close(log)
            def method(self):
                pass

        target = Protocol()
        target.method()
        
        self.assertFalse(target.transport.aborted)
        self.assertIsNone(self.msg)
        
    def test_success(self):
        
        class Protocol(object):
            def __init__(self):
                self.transport = MockAbortableTransport()
                self.msg = None
                
            def log(self, msg):
                self.msg = msg
            
            @twistit.on_error_close(log)
            def method(self):
                defer.succeed(42)

        target = Protocol()
        target.method()
        
        self.assertFalse(target.transport.aborted)
        self.assertIsNone(self.msg)
        
    def test_exception(self):
        
        class Protocol(object):
            def __init__(self):
                self.transport = MockAbortableTransport()
            
            @twistit.on_error_close(self.log)
            def method(self):
                raise ValueError()

        target = Protocol()
        target.method()
        
        self.assertTrue(target.transport.aborted)
        self.assertIsNotNone(self.msg)
        
    def test_failure(self):
        
        class Protocol(object):
            def __init__(self):
                self.transport = MockAbortableTransport()
            
            @twistit.on_error_close(self.log)
            def method(self):
                return defer.fail(failure.Failure(ValueError()))

        target = Protocol()
        target.method()
        
        self.assertTrue(target.transport.aborted)
        self.assertIsNotNone(self.msg)
        
        
    def test_loseConnection_fallback(self):
        
        class Protocol(object):
            def __init__(self):
                self.transport = MockClosableTransport()
                
            @twistit.on_error_close(self.log)
            def method(self):
                raise ValueError()

        target = Protocol()
        target.method()
        
        self.assertTrue(target.transport.closed)
        self.assertIsNotNone(self.msg)
        
    def test_no_close_or_abort(self):
        
        class Protocol(object):
            def __init__(self):
                self.transport = MockUnclosableTransport()
            
            @twistit.on_error_close(self.log)
            def method(self):
                raise ValueError()

        target = Protocol()
        target.method()
        
        self.assertIsNotNone(self.msg)
        
    def test_no_transport(self):
        
        class Protocol(object):
            def __init__(self):
                self.transport = None
            
            @twistit.on_error_close(self.log)
            def method(self):
                raise ValueError()

        target = Protocol()
        target.method()
        
        self.assertIsNotNone(self.msg)



class MockAbortableTransport(object):
    
    def __init__(self):
        self.aborted = False
        
    def abortConnection(self):
        self.aborted = True
    

class MockClosableTransport(object):
    
    def __init__(self):
        self.closed = False
        
    def loseConnection(self):
        self.closed = True
        
class MockUnclosableTransport(object):
    pass