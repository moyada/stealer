import json
import logging
import re
from typing import Optional, Union, List
from urllib.parse import urlparse, parse_qs

from django.http import HttpResponse
from requests import Response

from core.interface import Service
from core.model import Result, ErrorResult, Info
from tools import http_utils
from core import config
from core.type import Video

logger = logging.getLogger('request')

app_headers = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "Accept-Language": "zh-CN,zh;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Host": "v.kuaishou.com",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Upgrade-Insecure-Requests": "1",
    # "cookie": config.kwai_cookie,
    "User-Agent": config.user_agent
}

desk_headers = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Host": "v.kuaishou.com",
    "Sec-Ch-Ua": config.sec_ua,
    "Sec-Ch-Ua-Mobile": "?0",
    "Sec-Ch-Ua-Platform": "\"macOS\"",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-User": "?1",
    "Upgrade-Insecure-Requests": "1",
    # "cookie": config.kwai_cookie,
    "User-Agent": config.web_user_agent
}

download_headers = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "accept-encoding": "gzip, deflate, br",
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
        # android
        elif "v.kuaishou.com" in text:
            urls = re.findall(r'(?<=v.kuaishou.com\/)\w+', text, re.I | re.M)
            if urls:
                return "https://v.kuaishou.com/" + urls[0]
        # web
        elif "www.kuaishou.com" in text:
            urls = re.findall(r'(?<=www.kuaishou.com\/)f\/[\w|-]+|short-video\/\w+', text, re.I | re.M)
            if urls:
                return "https://www.kuaishou.com/" + urls[0]
        return None

    @classmethod
    def index(cls, url) -> Optional[str]:
        if "v.kuaishou.com" in url:
            return re.findall(r'(?<=com\/)\w+', url)[0]
        if "kuaishou.com/short-video" in url:
            return re.findall(r'(?<=com\/short-video\/)\w+', url)[0]
        else:
            return re.findall(r'(?<=com\/[s|f]\/)[\w|-]+', url)[0]

    @classmethod
    def get_info(cls, url: str) -> Result:
        share_url = cls.get_url(url)
        if share_url is None:
            return ErrorResult.URL_NOT_INCORRECT

        # h = desk_headers if "www.kuaishou.com" in share_url else app_headers
        res = http_utils.get(share_url, param=None, header=app_headers, redirect=False)
        if http_utils.is_error(res):
            return ErrorResult.VIDEO_INFO_ERROR

        redirect_url = res.headers.get("Location")
        parsed_url = urlparse(redirect_url)
        params_dict = parse_qs(parsed_url.query)

        ck = '; '.join([f"{key}={value}" for key, value in res.cookies.items()])
        headers = {
            "Accept": "*/*",
            "Accept-Encoding": "gzip, deflate, br",
            "content-type": "application/json",
            "Cookie": ck,
            "Origin": "https://v.m.chenzhongtech.com",
            "Referer": redirect_url,
            "Sec-Ch-Ua": config.sec_ua,
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            "Sec-Fetch-User": "?1",
            "User-Agent": config.user_agent
        }

        params = {
            "fid": params_dict.get("fid")[0],
            "shareToken": params_dict.get("shareToken")[0],
            "shareObjectId": params_dict.get("shareObjectId")[0],
            "shareMethod": "TOKEN",
            "shareId": params_dict.get("shareId")[0],
            "shareResourceType": "PHOTO_OTHER",
            "shareChannel": "share_copylink",
            "kpn": "KUAISHOU",
            "subBiz": "BROWSE_SLIDE_PHOTO",
            "env": "SHARE_VIEWER_ENV_TX_TRICK",
            "h5Domain": "v.m.chenzhongtech.com",
            "photoId": params_dict.get("photoId")[0],
            "isLongVideo": False,
        }

        res = http_utils.post("https://v.m.chenzhongtech.com/rest/wd/photo/info?kpn=KUAISHOU&captchaToken=", param=params, header=headers)
        if http_utils.is_error(res):
            return ErrorResult.VIDEO_INFO_ERROR

        data = json.loads(res.content)

        if data['result'] != 1:
            return Result.failed(data['error_msg'])

        photo_id = params.get("photoId")
        info = Info(platform=vtype)
        if data.get('atlas', None) is None:
            info.filename = f'{photo_id}.mp4'
            info.video = KuaishouService.get_video(data)
        else:
            info.filename = f'{photo_id}.zip'
            info.images = KuaishouService.get_image(data)
        info.desc = KuaishouService.get_desc(data)
        info.cover = KuaishouService.get_cover(data)

        return Result.success(info)

    @staticmethod
    def get_cover(data) -> str:
        return data['photo']['coverUrls'][0]['url']

    @staticmethod
    def get_desc(data) -> str:
        return data['photo']['caption']

    @staticmethod
    def get_video(data) -> str:
        return data['photo']['mainMvUrls'][0]['url']

    @staticmethod
    def get_image(data) -> List[str]:
        host = 'https://' + data['atlas']['cdn'][0]
        images = data['atlas']['list']

        image_urls = []
        for image in images:
            url = host + image
            image_urls.append(url)

        return image_urls

    @classmethod
    def download_header(cls) -> dict:
        return download_headers


if __name__ == '__main__':
    KuaishouService.fetch('https://www.kuaishou.com/f/X-xvAv7g3pLJ1qf')
    KuaishouService.fetch('https://www.kuaishou.com/short-video/3x869ukmcuggqkg')
    KuaishouService.fetch('https://v.kuaishou.com/BHhfRt')

