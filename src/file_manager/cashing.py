# This file was written with the help of Adam Vandervorst

import json
import os
from os import path


def cache_to_file(filepath: str, serializer, deserializer, namer):
    """
    Caches a slow function F, saving its output to a file using a provided serializer-deserializer pair,
    hashing the inputs (for retrieval) into filenames via namer.
    :param filepath: Path to the directory in which the cache file will be saved
    :param serializer: Function O -> J that converts the output O of the function F you want to cache to a json writable
                       object J, without loss of information.
    :param deserializer: Function J -> O that is the inverse of the serializer function, taking a json readable object
                         J and constructing the cached functions F original output O.
    :param namer: Injective function that takes as input the arguments of F and outputs a unique filename that will be
                  used to write or retreive F's output.
    :return: ???
    """
    def wrapper(f):
        def cached_f(*args, **kwargs):
            filename = namer(*args, **kwargs)
            if not path.isfile(filepath + filename):
                res = f(*args, **kwargs)
                if not path.exists(path.dirname(filepath + filename)):
                    print(filepath + filename)
                    os.makedirs(path.dirname(filepath + filename))
                with open(filepath + filename, "w") as file:
                    json.dump(serializer(res), file)
                return res
            else:
                # print("using cached")
                with open(filepath + filename, "r") as file:
                    return deserializer(json.load(file))
        return cached_f
    return wrapper
