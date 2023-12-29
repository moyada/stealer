import json
import re
from typing import Optional

from django.http import HttpResponse

from core.interface import Service
from core.model import Result, ErrorResult, Info
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
    def get_info(cls, url: str) -> Result:
        # url = cls.get_url(url)
        # if url is None:
        #     return ErrorResult.URL_NOT_INCORRECT

        result = re.findall(r'(?<=www.bilibili.com/bangumi/playx/ep)\d+', url)
        if len(result) == 0:
            return ErrorResult.URL_NOT_INCORRECT

        res = http_utils.get(f'https://api.bilibili.com/pgc/view/web/season?ep_id={result[0]}', header=headers)
        if http_utils.is_error(res):
            return Result.error(res)

        data = json.loads(res.content)

        item = None
        for e in data["result"]["episodes"]:
            if e["ep_id"] == 280787:
                item = e
                break

        # http://api.bilibili.com/x/player/playurl?cid=227539569&bvid=BV1cD4y1m7ce&qn=112&fnval=16
        res = http_utils.get('http://api.bilibili.com/x/player/playurl',
                             param={
                                 'cid': item["cid"],
                                 'bvid': item["bvid"],
                                 'qn': 112,
                                 'fnval': 0,
                                 'fnver': 0,
                                 'fourk': 1,
                             }, header=user_headers)
        if http_utils.is_error(res):
            return Result.error(res)

        data = json.loads(res.content)
        try:
            url = data['data']['durl'][0]['url']
        except (KeyError, IndexError):
            return ErrorResult.VIDEO_ADDRESS_NOT_FOUNT

        info = Info(platform=vtype)
        info.filename = str(item["cid"]) + ".mp4"
        info.cover = item['cover']
        info.desc = item['long_title']
        info.video = url
        # info.extra = extra
        return Result.success(info)

    @classmethod
    def fetch(cls, url: str, mode=0) -> Result:
        url = cls.get_url(url)
        if url is None:
            return ErrorResult.URL_NOT_INCORRECT

        # https://api.bilibili.com/pgc/view/web/season?ep_id=280787
        # result > episodes > foreach > bvid

        # 请求短链接，获得itemId
        res = http_utils.get("https://api.bilibili.com/pgc/view/web/season?ep_id=280787", header=headers)
        if http_utils.is_error(res):
            return Result.error(res)

        data = json.loads(res.content)

        bvid = ""
        cid = None

        for e in data["result"]["episodes"]:
            if e["ep_id"] == 280787:
                bvid = e["bvid"]
                cid = e["cid"]

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

        data = json.loads(res.content)

        try:
            url = data['data']['durl'][0]['url']
        except (KeyError, IndexError):
            return ErrorResult.VIDEO_ADDRESS_NOT_FOUNT

        result = Result.success(url)
        if mode != 0:
            result.ref = res.url
        return result

    @classmethod
    def download_header(cls) -> dict:
        return download_headers


if __name__ == '__main__':
    BangumiService.get_info('https://www.bilibili.com/bangumi/play/ep280787?spm_id_from=333.337.0.0&from_spmid=666.25.episode.0')



