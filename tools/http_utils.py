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


def get(url, param=None, header=None) -> Union[Optional[Response], Exception]:
    return execute(url, param, header)


def post(url, param=None, header=None) -> Union[Optional[Response], Exception]:
    return execute(url, param, header, 2)


def execute(url, param, header, mode=1) -> Union[Optional[Response], Exception]:
    if param is None:
        param = {}
    if header is None:
        header = {'Content-Type': 'application/json'}

    header['Connection'] = 'Close'

    try:
        if mode == 1:
            resp = requests.get(url, headers=header, data=param, timeout=20)
        else:
            resp = requests.post(url, headers=header, data=param, timeout=20)
    except Exception as e:
        return e

    success = (resp.status_code / 400) < 1
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
