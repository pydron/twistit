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

class Event(object):
    """
    Twisted-style observer pattern.
    
    Twisted deferreds can only be fired once. This class is handy to expose
    recuring events for which there might be mulitple observers.
    
    Observers can register themselves by passing a functions to
    :meth:`add_callback`. These functions are invoked if :meth:`fire` is
    called. The value passed to `fire` is passed on to the callbacks.
    
    """
    
    def __init__(self):
        self._callbacks = []
    
    def add_callback(self, callback):
        """
        Registers a callback that will be invoked on
        future calls to :meth:`fire`. The `callback` should
        take a single argument, the value passed to `fire`.
        """
        self._callbacks.append(callback)
    
    def remove_callback(self, callback):
        """
        Unregisters a previously registered callback.
        Future calls to :meth:`fire` will no longer invoke it.
        """
        self._callbacks.remove(callback)
        
    def next_event(self):
        """
        Returns a :class:`~defer.Deferred` that will be called back
        with the value of the next event.
        """
        d = defer.Deferred()
        
        def cb(value):
            self.remove_callback(d.callback)
            return value
        d.addBoth(cb)
        
        self.add_callback(d.callback)
        return d
    
    def fire(self, value):
        """
        Invoke all registered callbacks and pass the given
        value as the argument.
        """
        for callback in self._callbacks[:]:
            callback(value)
    
    def derive(self, modifier):
        """
        Returns a new :class:`Event` instance that will fire
        when this event fires. The value passed to the callbacks
        to the new event is the return value of the given
        `modifier` function which is passed the original value.
        """
        def forward(value):
            changed_value = modifier(value)
            derived.fire(changed_value)
        
        derived = Event()
        self.add_callback(forward)
        return derived
    
