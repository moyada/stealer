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
    "accept-encoding": "gzip, deflate",
    "user-agent": config.user_agent
}

share_headers = {
    "accept": "*/*",
    "accept-encoding": "gzip, deflate",
    "authority": "h5.pipix.com",
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin",
    "user-agent": config.user_agent
}

download_headers = {
    "accept": "*/*",
    "accept-encoding": "identity;q=1, *;q=0",
    "range": "bytes=0-",
    "sec-fetch-dest": "video",
    "sec-fetch-mode": "no-cors",
    "sec-fetch-site": "cross-sit",
    "user-agent": config.user_agent
}

vtype = Video.PIPIXIA


class PipixiaService(Service):

    @classmethod
    def get_prefix_pattern(cls) -> str:
        return 'h5\.pipix\.com/s\/'

    @classmethod
    def make_url(cls, index) -> str:
        return 'https://h5.pipix.com/s/' + index

    @classmethod
    def index(cls, url) -> Optional[str]:
        index = re.findall(r'(?<=s\/)\w+', url)
        try:
            return index[0]
        except IndexError:
            return None

    @classmethod
    def get_info(cls, url: str) -> Result:
        url = cls.get_url(url)
        if url is None:
            return ErrorResult.URL_NOT_INCORRECT

        res = http_utils.get(url, header=headers)
        if http_utils.is_error(res):
            return Result.error(res)

        try:
            id = re.findall(r"(?<=item\/)(\d+)(?=\?)", res.url)[0]
        except IndexError:
            return Result.failed(res.reason)

        url = "https://h5.pipix.com/bds/webapi/item/detail/?item_id=" + id + "&source=share"

        info_res = http_utils.get(url, header=share_headers)
        if http_utils.is_error(info_res):
            return Result.error(info_res)

        data = json.loads(str(info_res.text))

        try:
            item = data['data']['item']
            video = item['video']
            url = cls.get_video(video)
        except (KeyError, IndexError):
            return ErrorResult.VIDEO_ADDRESS_NOT_FOUNT

        info = Info(platform=vtype)
        info.filename = item["item_id_str"] + ".mp4"
        info.cover = item["cover"]["url_list"][0]["url"]
        info.desc = item["content"]
        info.video = url
        return Result.success(info)

    @classmethod
    def fetch(cls, url: str, mode=0) -> Result:
        url = cls.get_url(url)
        if url is None:
            return ErrorResult.URL_NOT_INCORRECT

        res = http_utils.get(url, header=headers)
        if http_utils.is_error(res):
            return Result.error(res)

        try:
            id = re.findall(r"(?<=item\/)(\d+)(?=\?)", res.url)[0]
        except IndexError:
            return Result.failed(res.reason)

        url = "https://h5.pipix.com/bds/webapi/item/detail/?item_id=" + id + "&source=share"

        info_res = http_utils.get(url, header=share_headers)
        if http_utils.is_error(info_res):
            return Result.error(info_res)

        data = json.loads(str(info_res.text))

        try:
            video = data['data']['item']['video']
            url = cls.get_video(video)
        except (KeyError, IndexError):
            return ErrorResult.VIDEO_ADDRESS_NOT_FOUNT

        return Result.success(url)

    @staticmethod
    def get_video(video: dict) -> Optional[str]:
        if video['video_download'] is not None:
            return video['video_download']['url_list'][0]['url']
        if video['video_god_comment_urls'] is not None:
            return video['video_god_comment_urls'][0]
        return None


if __name__ == '__main__':
    PipixiaService.fetch('https://h5.pipix.com/s/3asShh')
