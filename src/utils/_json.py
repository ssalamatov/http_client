# -*- coding: utf-8 -*-

from datetime import (datetime, date, timezone)
from decimal import (Decimal, InvalidOperation)
from json import JSONDecoder


class JsonDecoderOverriden(JSONDecoder):
    # TODO: make json decoder faster, now it is about 2-3 cycles of decoding, extremely slow for GS
    pass


def json_encoder(value):
    if type(value) in (date, datetime):
        return value.isoformat()
    elif type(value) in (Decimal, int, float):
        return float(value)
    else:
        return value


def parse_object(val):
    if not isinstance(val, bool) and (isinstance(val, int) or isinstance(val, float)):
        val = Decimal(str(val))
    elif isinstance(val, str):
        try:
            val = Decimal(val)
        except (InvalidOperation, ValueError):
            try:
                val = datetime.strptime(val, '%Y-%m-%d %H:%M:%S.%f')
                val = val.replace(tzinfo=timezone.utc)
            except ValueError:
                try:
                    val = datetime.strptime(val, '%Y-%m-%dT%H:%M:%S.%fZ')
                    val = val.replace(tzinfo=timezone.utc)
                except ValueError:
                    try:
                        val = datetime.strptime(val, '%Y-%m-%dT%H:%M:%SZ')
                        val = val.replace(tzinfo=timezone.utc)
                    except ValueError:
                        pass
    return val


def json_decoder(obj):
    if isinstance(obj, dict):
        for k, v in obj.items():
            obj[k] = json_decoder(v)
        return obj
    elif isinstance(obj, list):
        for k, e in enumerate(obj):
            obj[k] = json_decoder(e)
        return obj
    else:
        return parse_object(obj)
