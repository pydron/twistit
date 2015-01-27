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

from twisted.python import failure
from twisted.internet import reactor, defer

def timeout_deferred(deferred, timeout, error_message="Timeout occured"):
    """
    Waits a given time, if the given deferred hasn't called back
    by then we cancel it. If the deferred was cancelled by the timeout,
    a `TimeoutError` error is produced.
    
    Returns `deferred`.
    """
    
    timeout_occured = [False]
    
    def got_result(result):
        if not timeout_occured[0]:
            # Deferred called back before the timeout.
            delayedCall.cancel()
            return result
        else:
            if isinstance(result, failure.Failure) and result.check(defer.CancelledError):
                # Got a `CancelledError` after we called  `cancel()`.
                # Replace it with a `TimeoutError`.
                raise TimeoutError(error_message)
            else:
                # Apparently the given deferred has something else to tell us.
                # It might be that it completed before the `cancel()` had an effect
                # (or as a result thereof). It might also be that it triggered an
                # error. In either case, we want this to be visible down-stream.
                return result
    
    def time_is_up():
        timeout_occured[0] = True
        deferred.cancel()
    delayedCall = reactor.callLater(timeout, time_is_up)

    deferred.addBoth(got_result)
    return deferred

class TimeoutError(Exception):
    """
    Error produced if a deferred times out due to :func:`timeout_deferred`.
    """
    def __init__(self, value):
        self.value = value
    def __repr__(self):
        return "TimeoutError(%s)" % repr(self.value)