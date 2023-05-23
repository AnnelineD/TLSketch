from os import path, makedirs
from time import monotonic_ns


def timer(filepath, namer):
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
