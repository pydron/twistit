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

from twisted.internet import task
import threading
import sys
import traceback
import logging
logger = logging.getLogger(__name__)

def holdup_detector(max_delay=0.2,report_interval=1, report=None):
    
    event = threading.Event()
    run = threading.Event()
    run.set()
    
    main_thread = threading.current_thread()
    
    if not report:
        def report(main_thread):
            frame = sys._current_frames()[main_thread.ident]
            
            stack = "  ".join(traceback.format_stack(frame))
            
            logger.warn("Reactor thread busy for more than %s seconds: \n%s" % 
                        (max_delay, stack))
    
    def monitor_thread():
        blocked = False
        while run.is_set():
            event.clear()
            blocked = not event.wait(max_delay if not blocked else report_interval)
            if blocked:
                report(main_thread)
            
    
    def reset():
        event.set()
        
    def shutdown():
        run.clear()
        lc.stop()
    
    lc = task.LoopingCall(reset)
    lc.start(max_delay/2.0)
    
    t = threading.Thread(target=monitor_thread)
    t.daemon = True
    t.start()
    
    return shutdown