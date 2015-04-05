# Copyright (C) 2015 Stefan C. Mueller
import functools
from twisted.internet import defer



def on_error_close(logger):
    """
    Decorator for callback methods that implement `IProtocol`. 
    
    Any uncaught exception is logged and the connection is closed
    forcefully.
    
    Usage::
        import logger
        logger = logging.getLogger(__name__)
        
        class MyProtocol(Protocol):
          @on_error_close(logger.error)
          def connectionMade():
              ...
    
    The argument passed to `on_error_close` will be invoked with a
    string message.
    
    The motivation behind this decorator is as follows:
    
    Due to bugs it sometimes happens that exceptions are thrown out out
    callback methods in protocols. Twisted ignores them, at best they
    are logged. This is always a bug, as errors should be handled in the
    callback and not let to continue up the call stack. As such, the 
    behaviour after this occured is typically not well defined and 
    unpredictable. 
    
    A well made protocol implementation can handle unexpected connection
    losses as they may occur at any time in a real world environment.
    
    By closing the connection, there is a certain chance
    that we enter a code path that can recover, or at least gracefully
    cleanup. 
    
    In my experience, this often means that unit-tests fail with a more
    useful error message. Without it, I sometimes get the case that a
    unit-test (or even the final application) just blocks forever
    with no information on what is going wrong.
    """
    
    def make_wrapper(func):
        
        @functools.wraps(func)
        def wrapper(self, *args, **kwargs):
            
            d = defer.maybeDeferred(func, self, *args, **kwargs)
            def on_error(err):
                logger("Unhandled failure in %r:%s" % (func, err. getTraceback()))
                
                if hasattr(self, "transport"):
                    if hasattr(self.transport, "abortConnection"):
                        self.transport.abortConnection()
                    elif hasattr(self.transport, "loseConnection"):
                        self.transport.loseConnection()
            d.addErrback(on_error)
            
        return wrapper
    return make_wrapper