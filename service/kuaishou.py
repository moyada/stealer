import json
import logging
import re
from typing import Optional, Union, List

from django.http import HttpResponse
from requests import Response

from core.interface import Service
from core.model import Result, ErrorResult, Info
from tools import http_utils
from core import config
from core.type import Video

logger = logging.getLogger('request')

app_headers = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "Accept-Language": "zh-CN,zh;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Host": "v.kuaishou.com",
    "sec-ch-ua": "\" Not A;Brand\";v=\"99\", \"Chromium\";v=\"100\", \"Google Chrome\";v=\"100\"",
    "sec-ch-ua-mobile": "?1",
    "sec-ch-ua-platform": "\"Android\"",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Upgrade-Insecure-Requests": "1",
    "cookie": config.kwai_cookie,
    "user-agent": config.user_agent
}

desk_headers = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Host": "www.kuaishou.com",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-User": "?1",
    "Upgrade-Insecure-Requests": "1",
    "cookie": config.kwai_cookie,
    "user-agent": config.user_agent
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

        logger.info('get video param')
        h = desk_headers if "www.kuaishou.com" in share_url else app_headers
        res = http_utils.get(share_url, param=None, header=h, redirect=False)
        if http_utils.is_error(res):
            return ErrorResult.VIDEO_INFO_ERROR

        ref = res.headers['location']

        logger.info('find video info')

        if "chenzhongtech" in ref:
            res, photo_id = cls.get_app_info(ref)
        elif "gifshow" in ref:
            photo_id = re.findall(r'(?<=photo\/)\w+', ref)[0]
            res = cls.get_desk_info(photo_id, ref)
        else:
            photo_id = re.findall(r'(?<=short-video\/)\w+', ref)[0]
            ref = ref.replace('/short-video', 'https://m.gifshow.com/fw/photo')
            res = cls.get_desk_info(photo_id, ref)

        if http_utils.is_error(res):
            return ErrorResult.VIDEO_INFO_NOT_FOUNT

        data = json.loads(res.content)

        if data['result'] != 1:
            return Result.failed(data['error_msg'])

        info = Info(platform=vtype)
        if data.get('atlas', None) is None:
            info.filename = photo_id + '.mp4'
            info.video = KuaishouService.get_video(data)
        else:
            info.filename = photo_id + '.zip'
            info.images = KuaishouService.get_image(data)
        info.desc = KuaishouService.get_desc(data)
        info.cover = KuaishouService.get_cover(data)

        return Result.success(info)

    @classmethod
    def fetch(cls, url: str, mode=0) -> Result:
        share_url = cls.get_url(url)
        if share_url is None:
             return ErrorResult.URL_NOT_INCORRECT

        h = desk_headers if "www.kuaishou.com" in share_url else app_headers
        res = http_utils.get(share_url, param=None, header=h, redirect=False)
        if http_utils.is_error(res):
            return Result.error(res)

        ref = res.headers['location']

        if "chenzhongtech" in ref:
            res, photo_id = cls.get_app_info(ref)
        elif "gifshow" in ref:
            photo_id = re.findall(r'(?<=photo\/)\w+', ref)[0]
            res = cls.get_desk_info(photo_id, ref)
        else:
            photo_id = re.findall(r'(?<=short-video\/)\w+', ref)[0]
            ref = ref.replace('/short-video', 'https://m.gifshow.com/fw/photo')
            res = cls.get_desk_info(photo_id, ref)

        if http_utils.is_error(res):
            return Result.error(res)

        data = json.loads(res.content)

        if data.get('atlas', None) is None:
            result = Result.success(KuaishouService.get_video(data))
        else:
            result = Result.success(KuaishouService.get_image(data))
            result.type = 1

        if mode != 0:
            result.ref = share_url
        return result

    @staticmethod
    def get_desk_info(photo_id, ref) -> Union[Optional[Response], Exception]:
        info_headers = {
            "Host": "m.gifshow.com",
            "Origin": "https://m.gifshow.com",
            "Content-Type": "application/json",
            "sec-ch-ua-mobile": "?1",
            "sec-ch-ua-platform": "\"Android\"",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            "Referer": ref,
            "user-agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1",
            "Cookie": config.gifshow_cookie,
        }
        params = {
            "env": 'SHARE_VIEWER_ENV_TX_TRICK',
            "photoId": photo_id,
            "h5Domain": "m.gifshow.com",
            "isLongVideo": False,
        }

        param = ref.split('&')
        if len(param) > 1:
            query = {k.split('=')[0]: k.split('=')[1] for k in ref.split('&')}
            for k, v in query.items():
                params[k] = v

        return http_utils.post("https://m.gifshow.com/rest/wd/photo/info?kpn=KUAISHOU_VISION&captchaToken=",
                               param=params, header=info_headers)


    @staticmethod
    def get_app_info(ref) -> (Union[Optional[Response], Exception], str):
        info_headers = {
            "Host": "v.m.chenzhongtech.com",
            "Origin": "https://v.m.chenzhongtech.com",
            "Content-Type": "application/json",
            "sec-ch-ua-mobile": "?1",
            "sec-ch-ua-platform": "\"Android\"",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            "Referer": ref,
            "user-agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1",
            "Cookie": config.kwai_cookie,
        }

        query = {k.split('=')[0]: k.split('=')[1] for k in ref.split('&')}
        params = {
            "env": 'SHARE_VIEWER_ENV_TX_TRICK',
            "photoId": query.get('photoId'),
            "shareToken": query.get('shareToken'),
            "shareObjectId": query.get('shareObjectId'),
            "shareResourceType": 'PHOTO_OTHER',
            "fid": query.get('fid'),
            "shareMethod": 'token',
            "shareChannel": 'share_copylink',
            "h5Domain": "v.m.chenzhongtech.com",
            "isLongVideo": False,
            "kpn": "KUAISHOU",
            "subBiz": "BROWSE_SLIDE_PHOTO",
        }

        return http_utils.post("https://v.m.chenzhongtech.com/rest/wd/photo/info?kpn=KUAISHOU&captchaToken=",
                              param=params, header=info_headers), query.get('photoId')


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

    @staticmethod
    def download_header() -> dict:
        return download_headers

    @classmethod
    def download(cls, url) -> HttpResponse:
        return cls.proxy_download(vtype, url, download_headers, ".mp4")


if __name__ == '__main__':
    KuaishouService.fetch('https://www.kuaishou.com/f/X-xvAv7g3pLJ1qf')
    KuaishouService.fetch('https://www.kuaishou.com/short-video/3x869ukmcuggqkg')
    KuaishouService.fetch('https://v.kuaishou.com/BHhfRt')

