import logging
import time
import signal


class TimeoutException(Exception):  # Custom exception class
    pass


def break_after(seconds=2):
    def timeout_handler(signum, frame):  # Custom signal handler
        raise TimeoutException

    def function(function):
        def wrapper(*args, **kwargs):
            signal.signal(signal.SIGALRM, timeout_handler)
            signal.alarm(seconds)
            try:
                res = function(*args, **kwargs)
                signal.alarm(0)  # Clear alarm
                return res
            except TimeoutException:
                print(u'Oops, timeout: %s sec reached.' % seconds, function.__name__, args, kwargs)
            return

        return wrapper

    return function
