from os import path


def cache_to_file(filepath: str, serializer, deserializer, namer):
    def wrapper(f):
        def cached_f(*args, **kwargs):
            filename = namer(*args, **kwargs)
            if not path.isfile(filepath + filename):
                res = f(*args, **kwargs)
                with open(filepath + filename, "w") as file:
                    file.write(serializer(res))
                return res
            else:
                print("using cached")
                with open(filepath + filename, "r") as file:
                    return deserializer(file.read())
        return cached_f
    return wrapper