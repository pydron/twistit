# Copyright (C) 2015 Stefan C. Mueller


from zope.interface import implementer  # @UnresolvedImport
from twisted.internet import interfaces, error


@implementer(interfaces.IReactorTime)
class TimeMock(object):
    """
    Implementation of the reactor clock that allows for manual
    incrementation of the time with :meth:`advanceTime`.
    """

    @implementer(interfaces.IDelayedCall)
    class MockDelayedCall(object):
        
        def __init__(self, clock, time, f, args, kw):
            self.clock = clock
            self.time = time
            self.f = f
            self.args = args
            self.kw = kw
            self.called = False
            self.cancelled = False
        
        def getTime(self):
            return self.time
        
        def cancel(self):
            self._check()
            self.cancelled = True
            self.clock._delayed_calls.remove(self)
        
        def delay(self, secondsLater):
            self._check()
            self.time += secondsLater
            
        def reset(self, secondsFromNow):
            self._check()
            self.time = self.clock.seconds() + secondsFromNow
        
        def active(self):
            return not self.called and not self.cancelled
        
        def call(self):
            self.called = True
            self.f(*self.args, **self.kw)
        
        def _check(self):
            if self.called:
                raise error.AlreadyCalled()
            elif self.cancelled:
                raise error.AlreadyCancelled()
            
        def __repr__(self):
            return "MockDelayedCall(%r, %r, %r)" % (self.f, self.args, self.kw)
        
    def __init__(self):
        self._seconds = 0
        self._delayed_calls = []
    
    def seconds(self):
        return self._seconds
    
    def callLater(self, delay, f, *args, **kw):
        c = self.MockDelayedCall(self, self.seconds() + delay, f, args, kw)
        self._delayed_calls.append(c)
        return c
    
    def getDelayedCalls(self):
        return tuple(self._delayed_calls)
    
    def advanceTime(self, seconds):
        """
        Advances the clock by `seconds` seconds. This will call 
        delayed calls that are due before or at the new time.
        """
        final_time = self._seconds + seconds
        calls = sorted(self._delayed_calls, key=lambda c:c.time)
        calls = [c for c in calls if c.time <= final_time]
        
        for c in calls:
            self._seconds = c.time
            c.call()
            self._delayed_calls.remove(c)
        
        self._seconds = final_time

                
