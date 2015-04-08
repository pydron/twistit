# Copyright (C) 2015 Stefan C. Mueller

import unittest
import twistit
from twisted.internet import error

class TestTimeMock(unittest.TestCase):
    
    def setUp(self):
        

        self.target = twistit.TimeMock()
        
        def mock_f():
            self.f_called_at = self.target.seconds()
        self.f = mock_f
        self.f_called_at = None
       
        def mock_g():
            self.g_called_at = self.target.seconds()
        self.g = mock_g
        self.g_called_at = None
        
    
    def test_starts_at_zero(self):
        self.assertEqual(0, self.target.seconds())
        
    def test_seconds(self):
        self.target.advanceTime(123)
        self.assertEqual(123, self.target.seconds())
        
    def test_advance_incremental(self):
        self.target.advanceTime(10)
        self.target.advanceTime(20)
        self.assertEqual(30, self.target.seconds())
        
    def test_advance_zero(self):
        self.target.advanceTime(10)
        self.target.advanceTime(0)
        self.assertEqual(10, self.target.seconds())
                
    def test_zero_delay_not_called_immediately(self):
        self.target.callLater(0, self.f)
        self.assertIsNone(self.f_called_at)
        
    def test_zero_delay_called(self):
        self.target.callLater(0, self.f)
        self.target.advanceTime(0)
        self.assertEqual(self.f_called_at, 0)
        
    def test_delay(self):
        self.target.callLater(1, self.f)
        self.target.advanceTime(1)
        self.assertEqual(self.f_called_at, 1)
        
    def test_delay_jump_over(self):
        self.target.callLater(1, self.f)
        self.target.advanceTime(2)
        self.assertEqual(self.f_called_at, 1)
        
    def test_delay_before(self):
        self.target.callLater(1, self.f)
        self.target.advanceTime(0.5)
        self.assertEqual(self.f_called_at, None)
        
    def test_delay_offset(self):
        self.target.advanceTime(10)
        self.target.callLater(1, self.f)
        self.target.advanceTime(2)
        self.assertEqual(self.f_called_at, 11)
        
    def test_delay_offset_before(self):
        self.target.advanceTime(10)
        self.target.callLater(1, self.f)
        self.target.advanceTime(0.5)
        self.assertEqual(self.f_called_at, None)
        
    def test_multiple_sametime(self):
        self.target.callLater(10, self.f)
        self.target.callLater(10, self.g)
        self.target.advanceTime(11)
        self.assertEqual(self.f_called_at, 10)
        self.assertEqual(self.g_called_at, 10)
        
    def test_multiple_differentime_onejmp(self):
        self.target.callLater(8, self.f)
        self.target.callLater(10, self.g)
        self.target.advanceTime(11)
        self.assertEqual(self.f_called_at, 8)
        self.assertEqual(self.g_called_at, 10)
        
    def test_multiple_differentime_separately(self):
        self.target.callLater(8, self.f)
        self.target.callLater(10, self.g)
        self.target.advanceTime(9)
        self.assertEqual(self.f_called_at, 8)
        self.assertEqual(self.g_called_at, None)
        self.target.advanceTime(2)
        self.assertEqual(self.g_called_at, 10)
        
    def test_delay_call(self):
        c = self.target.callLater(10, self.f)
        c.delay(5)
        self.target.advanceTime(14)
        self.assertEqual(self.f_called_at, None)
        self.target.advanceTime(2)
        self.assertEqual(self.f_called_at, 15)
        
    def test_reset_call(self):
        c = self.target.callLater(10, self.f)
        self.target.advanceTime(8)
        c.reset(10)
        self.target.advanceTime(9)
        self.assertEqual(self.f_called_at, None)
        self.target.advanceTime(2)
        self.assertEqual(self.f_called_at, 18)
        
    def test_cancel(self):
        c = self.target.callLater(10, self.f)
        self.target.advanceTime(9)
        c.cancel()
        self.target.advanceTime(2)
        self.assertEqual(self.f_called_at, None)
        
    def test_cancel_called_error(self):
        c = self.target.callLater(10, self.f)
        self.target.advanceTime(11)
        self.assertRaises(error.AlreadyCalled, c.cancel)
        
    def test_delay_called_error(self):
        c = self.target.callLater(10, self.f)
        self.target.advanceTime(11)
        self.assertRaises(error.AlreadyCalled, c.delay, 10)
        
    def test_reset_called_error(self):
        c = self.target.callLater(10, self.f)
        self.target.advanceTime(11)
        self.assertRaises(error.AlreadyCalled, c.reset, 10)
        
    def test_cancel_cancelled_error(self):
        c = self.target.callLater(10, self.f)
        c.cancel()
        self.assertRaises(error.AlreadyCancelled, c.cancel)
        
    def test_delay_cancelled_error(self):
        c = self.target.callLater(10, self.f)
        c.cancel()
        self.assertRaises(error.AlreadyCancelled, c.delay, 10)
        
    def test_reset_cancelled_error(self):
        c = self.target.callLater(10, self.f)
        c.cancel()
        self.assertRaises(error.AlreadyCancelled, c.reset, 10)
        
    def test_getTime(self):
        self.target.advanceTime(100)
        c = self.target.callLater(10, self.f)
        self.assertEqual(c.getTime(), 110)
        
    def test_getTime_reset(self):
        self.target.advanceTime(100)
        c = self.target.callLater(15, self.f)
        self.target.advanceTime(10)
        c.reset(50)
        self.assertEqual(c.getTime(), 160)
        
    def test_getTime_delay(self):
        self.target.advanceTime(100)
        c = self.target.callLater(15, self.f)
        self.target.advanceTime(10)
        c.delay(50)
        self.assertEqual(c.getTime(), 165)