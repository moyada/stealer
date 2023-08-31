import json
import re
from typing import List
from urllib import parse

from django.http import HttpResponse

from core.interface import Service
from core.model import Result, ErrorResult, Info
from tools import http_utils
from core import config
from core.type import Video


headers = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "sec-ch-ua": "\"Not?A_Brand\";v=\"8\", \"Chromium\";v=\"108\", \"Google Chrome\";v=\"108\"",
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": "\"macOS\"",
    "sec-fetch-dest": "document",
    "sec-fetch-mode": "navigate",
    "sec-fetch-site": "none",
    "sec-fetch-user": "?1",
    "upgrade-insecure-requests": "1",
    "user-agent": config.web_user_agent
}

web_headers = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "sec-ch-ua": "\"Not?A_Brand\";v=\"8\", \"Chromium\";v=\"108\", \"Google Chrome\";v=\"108\"",
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": "\"macOS\"",
    "sec-fetch-dest": "document",
    "sec-fetch-mode": "navigate",
    "sec-fetch-site": "none",
    "sec-fetch-user": "?1",
    "upgrade-insecure-requests": "1",
    "cookie": config.dy_cookie,
    "user-agent": config.web_user_agent
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
    def get_info(cls, url: str) -> Result:
        share_url = cls.get_url(url)
        if share_url is None:
            return ErrorResult.URL_NOT_INCORRECT

        # 请求短链接，获得itemId
        res = http_utils.get(share_url, header=headers, redirect=True)
        if http_utils.is_error(res):
            return ErrorResult.VIDEO_INFO_NOT_FOUNT

        try:
            # item_id = re.findall(r"(?<=video/)\d+", res.headers['location'])[0]
            item_id = re.findall(r"(?<=\w/)\d+", res.url)[0]
        except IndexError:
            return ErrorResult.VIDEO_INFO_NOT_FOUNT

        share_url = f'https://www.douyin.com/video/{item_id}?previous_page=app_code_link'
        res = http_utils.get(share_url, header=web_headers)
        if http_utils.is_error(res):
            return ErrorResult.VIDEO_INFO_NOT_FOUNT

        json_data = re.findall(r'(?<=<script id=\"RENDER_DATA\" type=\"application\/json\">)(.*?)(?=<\/script>)', res.text)
        if len(json_data) == 0:
            return ErrorResult.VIDEO_INFO_ERROR

        aweme_data = json.loads(parse.unquote(json_data[0]))

        data = None
        for k, v in aweme_data.items():
            if isinstance(v, str):
                continue
            if 'awemeId' in v:
                data = v['aweme']

        if data is None or data['statusCode'] != 0:
            return ErrorResult.VIDEO_ADDRESS_NOT_FOUNT

        data = data['detail']

        info = Info(platform=vtype)
        info.desc = DouyinService.get_desc(data)
        info.cover = DouyinService.get_cover(data)

        if data['awemeType'] == 0:
            info.video = DouyinService.get_video(data)
            info.filename = data['awemeId'] + ".mp4"
        else:
            info.images = DouyinService.get_image(data)
            info.filename = data['awemeId'] + ".zip"

        return Result.success(info)

    @staticmethod
    def get_cover(data) -> str:
        return data['video']['cover']

    @staticmethod
    def get_desc(data) -> str:
        return data['desc']

    @staticmethod
    def get_video(data) -> str:
        br = data['video']['bitRateList']

        rate = 0
        url = ''
        for item in br:
            if item['bitRate'] > rate:
                rate = item['bitRate']
                url = item['playApi']
        return "https:" + url

    @staticmethod
    def get_image(data) -> List[str]:
        image_urls = []
        for image in data['images']:
            urls = image['urlList']
            url = urls[-1]
            image_urls.append(url)
        return image_urls


if __name__ == '__main__':
    DouyinService.get_info('气场十足# 海贼王 # 男孩... https://v.douyin.com/hbCnFqa/')
