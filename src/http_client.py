# -*- coding: utf-8 -*-

import simplejson as json
import requests

from requests import (adapters, exceptions)
from decimal import Decimal
from collections import namedtuple
from src.utils import (base, _json, _log)


config_parser = None
logger = _log.set_logging('http_client', config_parser)

cfg = config_parser.parse_config()

cfg_http_client = cfg['clients']['http_client']
max_retry = cfg_http_client['max_retry']
timeout = cfg_http_client['timeout']

headers = {
    'content-type': 'application/json',
    'charset': 'UTF-8',
    'Accept-Encoding': 'gzip'}


class HTTPWrapperClient:

    def __init__(self, session=None, headers=None):
        self.session = session or requests.Session()
        self.headers = headers

    def post(self,
             url, data=None, json=None, text=None, serializer=None, deserializer=None,
             headers=None, max_retry=None, timeout=None):
        return Req(
            http_wrapper_client(url=url, session=self.session, method='POST', params=data, data=json, text=text,
                                serializer=serializer or _json.json_encoder,
                                deserializer=deserializer,
                                headers=headers or self.headers, _max_retry=max_retry, _timeout=timeout))

    def put(self,
            url, json=None, serializer=None, deserializer=None, headers=None, max_retry=None, timeout=None):
        return Req(
            http_wrapper_client(url=url, session=self.session, method='PUT', data=json,
                                serializer=serializer or _json.json_encoder,
                                deserializer=deserializer,
                                headers=headers or self.headers, _max_retry=max_retry, _timeout=timeout))

    def get(self,
            url, data=None, serializer=None, deserializer=None, headers=None, max_retry=None, timeout=None, **kw):

        return Req(
            http_wrapper_client(
                url=url, session=self.session, method='GET', params=data,
                serializer=serializer or _json.json_encoder,
                deserializer=deserializer,
                headers=headers or self.headers, _max_retry=max_retry, _timeout=timeout, **kw))

    def delete(self,
               url, data=None, serializer=None, deserializer=None, headers=None, max_retry=None, timeout=None):

        return Req(
            http_wrapper_client(
                url=url, session=self.session, method='DELETE', params=data,
                serializer=serializer or _json.json_encoder,
                deserializer=deserializer,
                headers=headers or self.headers, _max_retry=max_retry, _timeout=timeout))


class Req:
    def __init__(self, req):
        self.req = req

    @property
    def code(self):
        return getattr(self.req, 'code')

    @property
    def reason(self):
        return getattr(self.req, 'reason')

    @property
    def json(self):
        return getattr(self.req, 'json')

    @property
    def text(self):
        return getattr(self.req, 'text')

    @property
    def data(self):
        return self.json if self.json or self.json in ({}, []) else self.text

    @property
    def request(self):
        return getattr(self.req, 'req')

    @property
    def headers(self):
        return getattr(self.req, 'headers')

    @property
    def is200(self):
        return bool(self.code == 200)

    @property
    def is202(self):
        return bool(self.code == 202)

    @property
    def is204(self):
        return bool(self.code == 204)

    @property
    def is20x(self):
        return any(map(lambda code: self.code == code, [200, 201, 202, 204]))

    @property
    def is404(self):
        return bool(self.code == 404)

    @property
    def is201(self):
        return bool(self.code == 201)

    @property
    def is400(self):
        return bool(self.code == 400)

    @property
    def is403(self):
        return bool(self.code == 403)

    @property
    def is500(self):
        return bool(self.code == 500)

    @property
    def view(self):
        return {'code': self.code, 'url': self.req.url, 'data': self.data}

    def __repr__(self):
        return '%s' % self.view


@base.retry(exception_to_check=(
        exceptions.ConnectTimeout,
        exceptions.ConnectionError,
        exceptions.ChunkedEncodingError), tries=4, logger=logger)
def http_wrapper_client(url, session=None, method='GET', params=None, data=None, text=None,
                        serializer=None, deserializer=None, headers=None, _max_retry=max_retry, _timeout=60, **kw):
    """
    Wrapper for http requests client
    """
    request = namedtuple('request', ['code', 'reason', 'req', 'text', 'json', 'headers', 'url'])

    stream = kw.get('stream')
    session = session or requests.Session()
    params = base.clean_empty(params) if params else None

    session.mount(url, adapters.HTTPAdapter(max_retries=_max_retry))

    if data is not None:
        data = json.dumps(data, namedtuple_as_object=True, default=serializer)

        logger.debug(data)

    req = requests.Request(method, url, params=params, data=text or data, headers=headers)
    prepare_req = req.prepare()

    res = session.send(prepare_req, timeout=_timeout, verify=False, **kw)
    res_code = getattr(res, 'status_code')
    res_reason = getattr(res, 'reason')
    res_headers = getattr(res, 'headers')
    res_url = getattr(res, 'url')
    res_text = None
    res_json = None

    try:
        res.raise_for_status()
        if not stream:
            res_text = getattr(res, 'text')
            try:
                if deserializer:
                    res_json = json.loads(
                        res_text, parse_int=Decimal, parse_float=Decimal, object_hook=deserializer)
                else:
                    res_json = json.loads(res_text, parse_int=Decimal, parse_float=Decimal)

            except json.JSONDecodeError:
                res_json = None
        else:
            return request(
                res_code, res_reason, res, None, None, res_headers, res_url)

    except exceptions.HTTPError:
        if 400 <= res_code <= 500:
            res_text = getattr(res, 'text')
            try:
                res_json = json.loads(res_text, parse_int=Decimal, parse_float=Decimal)
            except json.JSONDecodeError:
                res_json = None

    return request(
        res_code, res_reason, res, res_text, res_json, res_headers, res_url)


def get_chunk(stream, chunk_size):
    for chunk in stream.iter_lines(decode_unicode=True, chunk_size=chunk_size):
        yield json.loads(chunk.decode('utf-8'))
