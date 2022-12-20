import json
from typing import Union, Optional

import requests
from requests import Response


class HttpException(Exception):

    def __init__(self, code, msg):
        self.code = code
        self.msg = msg

    def __str__(self):
        return str({'code': self.code, 'message': self.msg})

    def __repr__(self):
        return 'HttpException(' + self.__str__() + ')'


def is_error(obj: Union[Optional[Response], Exception]) -> bool:
    return not hasattr(obj, 'status_code')


def get(url, param=None, header=None, redirect=True) -> Union[Optional[Response], Exception]:
    return execute(url, param, header, 1, redirect)


def post(url, param=None, header=None, redirect=True) -> Union[Optional[Response], Exception]:
    return execute(url, param, header, 2, redirect)


def execute(url, param, header, mode=1, allow_redirects=True) -> Union[Optional[Response], Exception]:
    if param is None:
        param = {}
    if header is None:
        header = {'Content-Type': 'application/json'}

    # header['Connection'] = 'Close'

    try:
        if mode == 1:
            resp = requests.get(url, headers=header, params=param, timeout=20, allow_redirects=allow_redirects)
        else:
            resp = requests.post(url, headers=header, json=param, timeout=20, allow_redirects=allow_redirects)
    except Exception as e:
        return e

    success = (resp.status_code < 400)
    if success:
        return resp

    # raise HttpException(resp.status_code, resp.reason)
    return HttpException(resp.status_code, resp.reason)


if __name__ == '__main__':
    res = get('http://httpbin.org/ip')
    if not is_error(res):
        print(json.loads(res.content))
    else:
        print(repr(res))
