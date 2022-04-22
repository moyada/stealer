import json
import re

from django.http import HttpResponse

from core.interface import Service
from core.model import Result, ErrorResult
from tools import http_utils
from core import config
from core.type import Video


headers = {
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

vtype = Video.DOUYIN


class DouyinService(Service):

    @classmethod
    def get_prefix_pattern(cls) -> str:
        # www.iesdouyin.com
        return 'douyin\.com\/'

    @classmethod
    def make_url(cls, index) -> str:
        return 'https://v.douyin.com/' + index

    @classmethod
    def fetch(cls, url: str, mode=0) -> Result:
        url = cls.get_url(url)
        if url is None:
            return ErrorResult.URL_NOT_INCORRECT

        # 请求短链接，获得itemId
        res = http_utils.get(url, header=headers)
        if http_utils.is_error(res):
            return Result.error(res)

        # html = str(res.content)
        try:
            item_id = re.findall(r"(?<=video/)\d+", res.url)[0]
        except IndexError:
            return Result.failed(res.reason)

        # 组装视频长链接
        infourl = "https://www.iesdouyin.com/web/api/v2/aweme/iteminfo/?item_ids=" + item_id + "&dytk="# + dytk

        # 请求长链接，获取play_addr
        url_res = http_utils.get(infourl, header=headers)
        if http_utils.is_error(url_res):
            return Result.error(url_res)

        data = json.loads(str(url_res.text))
        if not data['status_code'] == 0:
            return Result.failed(data['status_msg'])

        item = data['item_list'][0]
        if item['aweme_type'] == 4:
            result = DouyinService.get_video(item)
        elif item['aweme_type'] == 2:
            result = DouyinService.get_image(item)
            result.extra = ".zip"
        else:
            return ErrorResult.VIDEO_ADDRESS_NOT_FOUNT

        if mode == 1:
            result.ref = res.url
        return result

    @staticmethod
    def get_video(data) -> Result:
        try:
            # vid = data['video']['vid']
            link = data['video']['play_addr']['url_list'][0]
            link = link.replace('playwm','play')
            return Result.success(link)
        except Exception as e:
            return ErrorResult.VIDEO_ADDRESS_NOT_FOUNT

        # try:
        #     ratio = data['video']['ratio']
        # except Exception as e:
        #     ratio = "540p"
        #
        # link = "https://aweme.snssdk.com/aweme/v1/play/?video_id=" + vid + \
        #         "&line=0&ratio="+ratio+"&media_type=4&vr_type=0&improve_bitrate=0" \
        #         "&is_play_url=1&is_support_h265=0&source=PackSourceEnum_PUBLISH"
        # return Result.success(link)

    @staticmethod
    def get_image(data) -> Result:
        try:
            images = data['images']
        except Exception as e:
            return ErrorResult.VIDEO_ADDRESS_NOT_FOUNT

        image_urls = []
        for image in images:
            urls = image['url_list']
            url = urls[-1]
            image_urls.append(url)

        result = Result.success(image_urls)
        result.type = 1
        return result

    @classmethod
    def download(cls, url) -> HttpResponse:
        return cls.proxy_download(vtype, url, download_headers, ".mp4")


if __name__ == '__main__':
    DouyinService.fetch('https://v.douyin.com/cCBrrq/')

