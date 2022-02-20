import re
from typing import Optional

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
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "accept-encoding": "gzip, deflate, br",
    # "host": "txmov2.a.kwimgs.com",
    # "range": "bytes=0-",
    # "sec-fetch-dest": "video",
    # "sec-fetch-mode": "no-cors",
    # "sec-fetch-site": "cross-sit",
    "Upgrade-Insecure-Requests": '1',
    "user-agent": config.user_agent
}

vtype = Video.KUAISHOU


class KuaishouService(Service):

    @classmethod
    def get_url(cls, text: str) -> Optional[str]:
        if "kuaishouapp" in text:
            urls = re.findall(r'(?<=v.kuaishouapp.com\/s\/)\w+', text, re.I | re.M)
        else:
            urls = re.findall(r'(?<=v.kuaishou.com\/)\w+', text, re.I | re.M)

        if urls:
            return urls[0]
        return None

    @classmethod
    def index(cls, url) -> Optional[str]:
        if "kuaishouapp" in url:
            return re.findall(r'(?<=com\/s\/)\w+', url)[0]
        else:
            return re.findall(r'(?<=com\/)\w+', url)[0]

    @classmethod
    def fetch(cls, share_url: str, mode=0) -> Result:
        # url = cls.get_url(share_url)
        # if url is None:
        #     return ErrorResult.URL_NOT_INCORRECT

        # 请求短链接，获得itemId和dytk
        res = http_utils.get(share_url, header=headers)
        if http_utils.is_error(res):
            return Result.error(res)

        html = res.text
        try:
            url = re.findall(r"(?<=\"srcNoMark\":\"https://)(.*?)(?=.mp4)", html)[0]
        except IndexError:
            return ErrorResult.VIDEO_ADDRESS_NOT_FOUNT

        if not url:
            return ErrorResult.VIDEO_ADDRESS_NOT_FOUNT

        url = "https://" + url + ".mp4"
        result = Result.success(url)
        if mode != 0:
            result.ref = share_url
        return result

    @classmethod
    def download(cls, url) -> HttpResponse:
        return cls.proxy_download(vtype, url, download_headers, ".mp4")


if __name__ == '__main__':
    KuaishouService.fetch('https://v.kuaishou.com/3ke4p2')

