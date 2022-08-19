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
    "content-type": "json",
    "user-agent": config.user_agent
}

user_headers = {
    "accept": "*/*",
    "content-type": "json",
    "cookie": config.bilibili_cookie,
    "user-agent": config.user_agent
}

download_headers = {
    "accept": "*/*",
    "accept-encoding": "identity;q=1, *;q=0",
    "range": "bytes=0-",
    "sec-fetch-dest": "video",
    "sec-fetch-mode": "no-cors",
    "sec-fetch-site": "cross-sit",
    "referer": "https://www.bilibili.com",
    "user-agent": config.user_agent
}


vtype = Video.BILIBILI


class BiliBiliService(Service):

    @classmethod
    def get_url(cls, text: str) -> Optional[str]:
        if "bilibili" in text:
            urls = re.findall(r'(?<=www\.bilibili\.com\/video\/).+', text, re.I | re.M)
            if urls:
                return "https://www.bilibili.com/video/" + urls[0]
            return None

        urls = re.findall(r'(?<=b23\.tv\/)\w+', text, re.I | re.M)
        if len(urls) == 0:
            return None
        url = "https://b23.tv/" + urls[0]
        res = http_utils.get(url, header=headers)
        url = res.url
        return url

    # @classmethod
    # def get_prefix_pattern(cls) -> str:
    #     # https://b23.tv/lizymu4
    #     return 'www\.bilibili\.com\/video\/'

    @classmethod
    def make_url(cls, index) -> str:
        return index

    @classmethod
    def index(cls, url) -> Optional[str]:
        if "b23.tv" in url:
            return re.findall(r'(?<=b23\.tv\/)\w+', url, re.I | re.M)[0]

        try:
            bvid = re.findall(r'(?<=video\/)\w+', url)[0]
        except IndexError:
            return None

        p = re.findall(r"(?<=p=)(\d)", url)
        if len(p) == 0:
            return bvid
        else:
            return bvid + '-' + p[0]

    @classmethod
    def get_bvid(cls, url) -> Optional[str]:
        try:
            return re.findall(r'(?<=video\/)\w+', url)[0]
        except IndexError:
            return None

    @classmethod
    def fetch(cls, url: str, mode=0) -> Result:
        burl = cls.get_url(url)
        if burl is None:
            return ErrorResult.URL_NOT_INCORRECT

        bvid = cls.get_bvid(burl)
        if bvid is None:
            return ErrorResult.URL_NOT_INCORRECT

        res = http_utils.get('https://api.bilibili.com/x/player/pagelist',
                             param={'bvid': bvid, 'jsonp': 'jsonp'}, header=headers)
        if http_utils.is_error(res):
            return Result.error(res)

        data = json.loads(str(res.text))
        p = re.findall(r"(?<=p=)(\d)", url)
        if len(p) == 0:
            index = 0
        else:
            index = int(p[0]) - 1

        try:
            cid = data['data'][index]['cid']
        except (KeyError, IndexError):
            return ErrorResult.VIDEO_ADDRESS_NOT_FOUNT

        # http://api.bilibili.com/x/player/playurl?cid=227539569&bvid=BV1cD4y1m7ce&qn=112&fnval=16
        res = http_utils.get('http://api.bilibili.com/x/player/playurl',
                             param={
                                 'cid': cid,
                                 'bvid': bvid,
                                 'qn': 112,
                                 'fnval': 0,
                                 'fnver': 0,
                                 'fourk': 1,
                            }, header=user_headers)
        if http_utils.is_error(res):
            return Result.error(res)

        data = json.loads(str(res.text))

        try:
            url = data['data']['durl'][0]['url']
            # url = data['data']['dash']['video'][0]['baseUrl']
        except (KeyError, IndexError):
            return ErrorResult.VIDEO_ADDRESS_NOT_FOUNT

        result = Result.success(url)
        if mode != 0:
            result.ref = res.url
        return result

    @classmethod
    def download(cls, url) -> HttpResponse:
        return cls.proxy_download(vtype, url, download_headers, ".mp4", mode=0)


if __name__ == '__main__':
    BiliBiliService.fetch('https://www.bilibili.com/video/BV17s411P7oi?p=5&share_source=copy_web')
    BiliBiliService.fetch('https://www.bilibili.com/video/BV1oK41157Gm?share_source=copy_web')


