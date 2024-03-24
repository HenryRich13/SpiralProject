import types


def count_bits(num: int):
    return 0 if num == 0 else (num & 1) + count_bits(num >> 1)


def chain_iters(*iterables):
    for iterable in iterables:
        for obj in iterable:
            yield obj


def switch(obj, cases: dict, error: Exception = None):
    for case, value in cases.items():
        if case == obj:
            return value
        if isinstance(case, types.LambdaType) and not isinstance(obj, types.LambdaType):
            if case(obj):
                return value
    if "DEFAULT" in cases.keys():
        return cases["DEFAULT"]
    if error is not None:
        raise error


def sc_switch(obj, cases: dict, error: Exception = None):
    func = switch(obj, cases, error)
    if func is not None:
        return func()
    return None
