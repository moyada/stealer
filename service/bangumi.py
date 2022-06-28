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
    "content-type": "text/html",
    "user-agent": config.web_user_agent,
    "sec-ch-ua-mobile": "?0",
    "sec-fetch-dest": "document",
    "sec-fetch-mode": "navigate",
    "sec-fetch-site": "none",
    "sec-fetch-user": "?1",
    "upgrade-insecure-requests": "1"
}

user_headers = {
    "accept": "*/*",
    "content-type": "json",
    "cookie": config.bilibili_cookie,
    "user-agent": config.web_user_agent,
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


vtype = Video.BANGUMI


class BangumiService(Service):

    @classmethod
    def get_prefix_pattern(cls) -> str:
        # https://www.bilibili.com/bangumi/play/
        return 'www\.bilibili\.com\/bangumi\/play\/'

    @classmethod
    def make_url(cls, index) -> str:
        return 'https://www.bilibili.com/bangumi/play/' + index

    @classmethod
    def index(cls, url) -> Optional[str]:
        index = re.findall(r'(?<=bangumi\/play\/)\w+', url)
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

        html = res.text
        try:
            data = re.findall(r"(?<=window\.__INITIAL_STATE__=)(.*?)(?=;\(function\(\))", html)[0]
        except IndexError:
            return ErrorResult.VIDEO_ADDRESS_NOT_FOUNT

        data = json.loads(data)

        try:
            bvid = data['epInfo']['bvid']
            cid = data['epInfo']['cid']
        except Exception as e:
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
    BangumiService.fetch('https://www.bilibili.com/bangumi/play/ep280787?spm_id_from=333.337.0.0&from_spmid=666.25.episode.0')



