'''
Created on 17.08.2015

@author: stefan
'''


import unittest
import twistit
import utwist

from twisted.internet import task, reactor
import time
import threading

class TestHoldUp(unittest.TestCase):
    
    
    def setUp(self):
        self._mainthread = None
    
    def report(self, mainthread):
        self._mainthread = mainthread
        
    @utwist.with_reactor
    @twistit.yieldefer
    def test_not_blocking(self):
        self._mainthread = None
        
        @twistit.yieldefer
        def f():
            for _ in range(10):
                yield task.deferLater(reactor, 0.2, lambda :None)
                
        stop_detector = twistit.holdup_detector(0.1, report=self.report)
                
        yield task.deferLater(reactor, 0, f)
        yield stop_detector()
        
        self.assertIsNone(self._mainthread)
        
    
    @utwist.with_reactor
    @twistit.yieldefer
    def test_blocking(self):
        
        @twistit.yieldefer
        def f():
            for _ in range(10):
                time.sleep(0.2)
                
        stop_detector = twistit.holdup_detector(0.1, report=self.report)
                
        yield task.deferLater(reactor, 0, f)
        yield stop_detector()
 
        self.assertIs(self._mainthread, threading.current_thread())
        