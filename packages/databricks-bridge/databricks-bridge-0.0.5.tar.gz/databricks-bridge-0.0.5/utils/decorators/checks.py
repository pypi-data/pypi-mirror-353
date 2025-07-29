import functools


def null_raiser(func):
    """
    Use this decorator to check your input dictionary doesn't have any null values.
    Use this only if you know the data shouldn't be null anywhere
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        for arg in args:
            for k, v in arg.items():
                if v is None:
                    raise ValueError(f"There is a null value for key: {k}")
        return func(*args, **kwargs)
    return wrapper


