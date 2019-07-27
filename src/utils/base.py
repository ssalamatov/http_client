# -*- coding: utf-8 -*-

import uuid as _uuid
import random
import operator
import time
import math
import functools
import itertools

from src.utils import _log
from decimal import Decimal
from numbers import Number


def head(_list):
    if isinstance(_list, list) and _list != []:
        return _list[0]
    if isinstance(_list, tuple) and _list != ():
        return _list[0]
    else:
        return _list


def tail(_list):
    if isinstance(_list, list) and len(_list) > 1:
        return _list[1:]
    if isinstance(_list, tuple) and len(_list) > 1:
        return _list[1:]
    else:
        return []


def last(_list):
    if isinstance(_list, list) and _list != []:
        return _list[-1]
    if isinstance(_list, tuple) and _list != ():
        return _list[-1]
    else:
        return _list


def flatten(_list):
    return list(itertools.chain.from_iterable(_list))


def uuid():
    return str(_uuid.uuid4())


def find_val(obj, *args):
    return {k: obj.get(k) for k in args}


def clean_empty(obj, _except=None):
    _except = _except or []
    return {k: v for k, v in obj.items() if bool(v is not None and v != '' and v != {}) or k in _except}


def remove_keys(obj, *args):
    for key in args:
        try:
            del obj[key]
        except KeyError:
            pass


def action(obj, f, *args):
    if type(obj) == dict:
        f(obj, *args)
        for k, v in obj.items():
            action(v, f, *args)
    elif type(obj) == list:
        for e in obj:
            action(e, f, *args)


def random_val(obj=None):
    if type(obj) in (list, tuple):
        return random.choice(obj)
    else:
        return uuid()


def ej_list(data):
    if isinstance(data, list):
        return data[0] if len(data) == 1 else data
    else:
        return data


def all_or_none(args, val):
    return val() if all(args) else None


def non_zero(val):
    return bool(val is not None and val != 0)


def fmt_to_str(obj):
    if type(obj) == int:
        return '{0:.1f}'.format(obj)
    else:
        return obj


def to_str_with_zero(obj):
    if type(obj) == dict:
        for k, v in obj.items():
            obj[k] = to_str_with_zero(v)

    elif type(obj) == list:
        for count, x in enumerate(obj):
            obj[count] = to_str_with_zero(x)
        return obj
    else:
        return fmt_to_str(obj)


def retry(exception_to_check, tries=1, delay=4, logger=_log.set_logging('exceptions', None)):
    def wrapper(f):
        @functools.wraps(f)
        def f_retry(*args, **kwargs):
            mtries, mdelay = tries, delay
            while True:
                try:
                    return f(*args, **kwargs)
                except exception_to_check as e:
                    msg = '%s, Retrying in %d seconds...' % (mtries, mdelay)
                    if logger:
                        logger.exception('There was an exception in: %s' % f.__name__)
                        logger.exception('%s' % f.__doc__)
                        logger.exception('Message: %s' % e)
                    if mtries <= 1:
                        raise e
                    logger.exception(msg)
                    mtries -= 1
                    time.sleep(mdelay)
        return f_retry
    return wrapper


def log_exceptions(exception_to_check, logger=_log.set_logging('exceptions', None)):
    def wrapper(f):
        @functools.wraps(f)
        def f_retry(*args, **kwargs):
            try:
                return f(*args, **kwargs)
            except exception_to_check as e:
                if logger:
                    logger.exception('There was an exception in: %s(%s %s)' % (f.__name__, args, kwargs))
                    logger.exception('%s' % f.__doc__)
                    logger.exception('Message: %s' % e)
                raise e
        return f_retry
    return wrapper


# have to refactoring
def delay(func, result=None, timeout=30):
    while timeout > 0:
        v = func()
        if result is None and v is True:
            break
        else:
            if v.data == result:
                break
        time.sleep(1)
        timeout -= 1
    else:
        return False
    return True


def partition(items, predicate=bool):
    a, b = itertools.tee((predicate(item), item) for item in items)
    return ((item for pred, item in a if not pred),
            (item for pred, item in b if pred))


def safe_oper(f, exc=TypeError):
    try:
        return f()
    except exc:
        return None


def safe_sum(*val):
    if all(isinstance(v, Number) for v in val):
        return sum(val)
    else:
        return functools.reduce(operator.add, filter(lambda i: i, val))


def save_min(val1, val2):
    is_num_val1 = isinstance(val1, Number)
    is_num_val2 = isinstance(val2, Number)
    if is_num_val1 and is_num_val2:
        return min(val1, val2)
    elif is_num_val1:
        return val1
    elif is_num_val2:
        return val2


def save_max(val1, val2):
    is_num_val1 = isinstance(val1, Number)
    is_num_val2 = isinstance(val2, Number)
    if is_num_val1 and is_num_val2:
        return max(val1, val2)
    elif is_num_val1:
        return val1
    elif is_num_val2:
        return val2


def safe_sum_two(val1, val2):
    is_num_val1 = isinstance(val1, Number)
    is_num_val2 = isinstance(val2, Number)
    if is_num_val1 and is_num_val2:
        return val1 + val2
    elif is_num_val1:
        return val1
    elif is_num_val2:
        return val2
    else:
        return 0


def safe_sub_two(val1, val2):
    is_num_val1 = isinstance(val1, Number)
    is_num_val2 = isinstance(val2, Number)
    if is_num_val1 and is_num_val2:
        return val1 - val2
    elif is_num_val1:
        return val1
    elif is_num_val2:
        return -val2
    else:
        return 0


def safe_multiply(m1, m2):
    is_num_m1 = isinstance(m1, Number)
    is_num_m2 = isinstance(m2, Number)

    if is_num_m1 and is_num_m2:
        return m1 * m2


def safe_divide(m1, m2):
    is_num_m1 = isinstance(m1, Number)
    is_num_m2 = isinstance(m2, Number)

    if is_num_m1 and is_num_m2:
        return m1 / m2


def safe_sub(m1, m2):
    is_num_m1 = isinstance(m1, Number)
    is_num_m2 = isinstance(m2, Number)

    if is_num_m1 and is_num_m2:
        return m1 - m2


def get_min(x, y):
    is_num_m1 = isinstance(x, Number)
    is_num_m2 = isinstance(y, Number)

    if is_num_m1 and is_num_m2:
        return min(x, y)
    return x or y


def get_max(x, y):
    is_num_m1 = isinstance(x, Number)
    is_num_m2 = isinstance(y, Number)

    if is_num_m1 and is_num_m2:
        return max(x, y)
    return x or y


def safe_compare(fun, x, y):
    if x and y:
        return fun(x, y)
    else:
        return x or y


def rand_bool():
    return random.choice([True, False])


def rand_float(from_, to):
    return random.uniform(from_, to)


def number_or_nil(n):
    return n if isinstance(n, Number) else Decimal('0')


def join(data):
    return ','.join(data) if type(data) == list else data


def ceil_to(n, prec=2):
    mult = math.pow(10, prec)
    if isinstance(n, Decimal):
        mult = Decimal(mult)
    return math.ceil(mult * n) / mult


def floor_to(n, prec=2):
    mult = math.pow(10, prec)
    if isinstance(n, Decimal):
        mult = Decimal(mult)
    return math.floor(mult * n) / mult
