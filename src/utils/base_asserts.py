# -*- coding: utf-8 -*-

import datetime
from decimal import Decimal
from src.utils import (base, _log)


config_parser = None
logger = _log.set_logging('exceptions', config_parser)


@base.log_exceptions(AssertionError, logger)
def assert_equal_deviation(expected,
                           actual,
                           delta=Decimal('1')):
    assert bool(actual - delta <= expected < actual + delta)


@base.log_exceptions(AssertionError, logger)
def assert_list_member(val, *args):
    assert bool(val in args)


def in_interval(act, exp, dev=Decimal('0.03')):
    exp = Decimal(exp) if exp else 0
    act = Decimal(act) if exp else 0
    if abs(exp) < 1 or abs(act) < 1:
        return abs(exp - act) <= dev
    else:
        return abs(exp - act) / abs(act) <= dev


@base.log_exceptions(AssertionError, logger)
def assert_equal_delta_or_cent(act, exp, dev=Decimal('0.03')):
    assert in_interval(act, exp, dev)


def assert_with_types(act, exp, dev=Decimal('0.03')):
    if type(act) in (datetime.datetime, str):
        assert act == exp
    else:
        assert_equal_delta_or_cent(act, exp, dev=dev)


def deep_compare(act, exp, key=None, dev=Decimal('0.03'), skip_keys=None):
    skip_keys = skip_keys if skip_keys else list()
    if type(act) == dict:
        for k, act_v in act.items():
            if k in skip_keys:
                continue
            exp_v = exp[k]
            deep_compare(act_v, exp_v, k, dev, skip_keys=skip_keys)

    elif type(act) == list:
        act = sorted(act)
        exp = sorted(exp)
        for k, act_e in enumerate(act):
            exp_e = exp[k]
            deep_compare(act_e, exp_e, key, dev, skip_keys=skip_keys)
    else:
        if act is None and exp:
            return
        assert_with_types(act, exp, dev)
