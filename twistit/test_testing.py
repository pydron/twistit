# Copyright (C) 2015 Stefan C. Mueller

import unittest
from twisted.internet import defer
import twistit

class TestExtract(unittest.TestCase):
    
    def test_success(self):
        d = defer.succeed(42)
        self.assertEqual(42, twistit.extract(d))
        
    def test_fail(self):
        d = defer.fail(ValueError())
        self.assertRaises(ValueError, twistit.extract, d)
        
    def test_not_called(self):
        d = defer.Deferred()
        self.assertRaises(twistit.NotCalledError, twistit.extract, d)