# This file was written with the help of Adam Vandervorst

from os import path, makedirs
from time import monotonic_ns


def timer(filepath, namer):
    """
    Times how long it takes to execute a function F, and saves that to a file
    :param filepath: The directory in which to save the timing file
    :param namer: Injective function that takes as input the arguments of F and outputs a unique filename that will be
                  used to save the timing.
    :return: ???
    """
    def wrapper(f):
        def timed_f(*args, **kwargs):
            t0 = monotonic_ns()
            res = f(*args, **kwargs)
            duration = monotonic_ns() - t0
            filename = namer(*args, **kwargs)
            if not path.exists(path.dirname(filepath + filename)):
                print(filepath + filename)
                makedirs(path.dirname(filepath + filename))
            with open(filepath + filename, 'w') as file:
                file.write(str(duration))
            return res
        return timed_f
    return wrapper
