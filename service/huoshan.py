
import re
from typing import Optional

from django.http import HttpResponse

from core.interface import Service
from core.model import Result, ErrorResult
from tools import http_utils
from core import config
from core.type import Video


headers = {
    "user-agent": config.user_agent
}

info_headers = {
    "accept": "*/*",
    "accept-encoding": "gzip, deflate",
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin",
    "user-agent": config.user_agent
}

download_headers = {
    "accept": "*/*",
    "accept-encoding": "identity;q=1, *;q=0",
    "accept-language": "zh-CN,zh;q=0.9,ja;q=0.8,en;q=0.7,zh-TW;q=0.6,de;q=0.5,fr;q=0.4,ca;q=0.3,ga;q=0.2",
    "range": "bytes=0-",
    "sec-fetch-dest": "video",
    "sec-fetch-mode": "no-cors",
    "sec-fetch-site": "cross-sit",
    "user-agent": config.user_agent
}

vtype = Video.HUOSHAN


class HuoshanService(Service):

    @classmethod
    def get_prefix_pattern(cls) -> str:
        return 'com/hotsoon/s\/'

    @classmethod
    def make_url(cls, index) -> str:
        return 'https://share.huoshan.com/hotsoon/s/' + index

    @classmethod
    def index(cls, url) -> Optional[str]:
        index = re.findall(r'(?<=s\/)\w+', url)
        try:
            return index[0]
        except IndexError:
            return None

    @classmethod
    def fetch(cls, url: str, mode=0) -> Result:
        url = cls.get_url(url)
        if url is None:
            return ErrorResult.URL_NOT_INCORRECT

        # 请求短链接，获得itemId
        res = http_utils.get(url, header=headers)
        if http_utils.is_error(res):
            return Result.error(res)

        try:
            item_id = re.findall(r"(?<=item_id=)\d+(?=\&)", res.url)[0]
        except IndexError:
            return Result.failed(res.reason)

        # 视频信息链接
        infourl = "https://share.huoshan.com/api/item/info?item_id=" + item_id

        # 请求长链接，获取play_addr
        url_res = http_utils.get(infourl, header=info_headers)
        if http_utils.is_error(url_res):
            return Result.error(url_res)

        vhtml = str(url_res.text)
        try:
            video_id = re.findall(r'(?<=video_id\=)\w+(?=\&)', vhtml)[0]
        except IndexError:
            return Result.failed(url_res.reason)

        if not video_id:
            return ErrorResult.VIDEO_ADDRESS_NOT_FOUNT

        link = "https://api.huoshan.com/hotsoon/item/video/_source/?video_id=" + video_id + "&line=0&app_id=0&vquality=normal"
        result = Result.success(link)

        if mode != 0:
            result.ref = res.url
        return result

    @classmethod
    def download(cls, url) -> HttpResponse:
        return cls.proxy_download(vtype, url, download_headers, ".mp4")


if __name__ == '__main__':
    HuoshanService.fetch('http://share.huoshan.com/hotsoon/s/eVDEDNYXu78')
