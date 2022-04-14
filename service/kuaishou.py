import json
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
            if urls:
                return "https://v.kuaishouapp.com/s/" + urls[0]
        else:
            urls = re.findall(r'(?<=v.kuaishou.com\/)\w+', text, re.I | re.M)
            if urls:
                return "https://v.kuaishou.com/" + urls[0]

        return None

    @classmethod
    def index(cls, url) -> Optional[str]:
        if "kuaishouapp" in url:
            return re.findall(r'(?<=com\/s\/)\w+', url)[0]
        else:
            return re.findall(r'(?<=com\/)\w+', url)[0]

    @classmethod
    def fetch(cls, url: str, mode=0) -> Result:
        share_url = cls.get_url(url)
        if share_url is None:
             return ErrorResult.URL_NOT_INCORRECT

        # 请求短链接，获得itemId和dytk
        res = http_utils.get(share_url, header=headers)
        if http_utils.is_error(res):
            return Result.error(res)

        html = res.text
        try:
            data = re.findall(r"(?<=window\.pageData= )(.*?)(?=<\/script>)", html)[0]
        except IndexError:
            return ErrorResult.VIDEO_ADDRESS_NOT_FOUNT

        data = json.loads(data)
        if data['video']['type'] == 'video':
            result = KuaishouService.get_video(data)
        else:
            result = KuaishouService.get_image(data)

        if mode != 0:
            result.ref = share_url
        return result

    @staticmethod
    def get_video(data) -> Result:
        try:
            url = data['video']['srcNoMark']
        except Exception as e:
            return ErrorResult.VIDEO_ADDRESS_NOT_FOUNT
        return Result.success(url)

    @staticmethod
    def get_image(data) -> Result:
        try:
            host = 'https://' + data['video']['imageCDN']
            images = data['video']['images']
        except Exception as e:
            return ErrorResult.VIDEO_ADDRESS_NOT_FOUNT

        image_urls = []
        for image in images:
            url = host + image['path']
            image_urls.append(url)

        result = Result.success(image_urls)
        result.type = 1
        return result

    @classmethod
    def download(cls, url) -> HttpResponse:
        return cls.proxy_download(vtype, url, download_headers, ".mp4")


if __name__ == '__main__':
    KuaishouService.fetch('https://v.kuaishou.com/3ke4p2')

