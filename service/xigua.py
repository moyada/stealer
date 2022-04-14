import re
from django.http import HttpResponse

from core.interface import Service
from core.model import Result, ErrorResult
from tools import http_utils
from core import config
from core.type import Video


headers = {
    "accept": "*/*",
    "accept-encoding": "gzip, deflate, br",
    "accept-language": "en,zh-CN;q=0.9,zh;q=0.8,de;q=0.7",
    "user-agent": config.user_agent
}

download_headers = {
    "accept": "*/*",
    "accept-encoding": "identity;q=1, *;q=0",
    "host": "jsmov2.a.yximgs.com",
    "range": "bytes=0-",
    "sec-fetch-dest": "video",
    "sec-fetch-mode": "no-cors",
    "sec-fetch-site": "cross-sit",
    "user-agent": config.user_agent
}

vtype = Video.XIGUA


class XiguaService(Service):

    @classmethod
    def get_prefix_pattern(cls) -> str:
        return 'ixigua\.com\/'

    @classmethod
    def make_url(cls, index) -> str:
        return 'https://www.ixigua.com/' + index

    @classmethod
    def fetch(cls, url: str, mode=0) -> Result:
        url = cls.get_url(url)
        if url is None:
            return ErrorResult.URL_NOT_INCORRECT

        # 请求短链接，获得itemId和dytk
        res = http_utils.get(url, header=headers)
        if http_utils.is_error(res):
            return Result.error(res)

        html = str(res.content)
        url = re.findall(r"(?<=type=\"video\/mp4\" src=\")(.*?)(?=\")", html)[0]
        if not url:
            return ErrorResult.VIDEO_ADDRESS_NOT_FOUNT

        result = Result.success(url)
        if mode != 0:
            result.ref = res.url
        return result

    @classmethod
    def download(cls, url) -> HttpResponse:
        return cls.proxy_download(vtype, url, download_headers, ".mp4")
