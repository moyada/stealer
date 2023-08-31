import json
import os
import re
from typing import Optional

from django.http import HttpResponse, HttpResponseServerError

import tools.ffmpeg
from core.interface import Service
from core.model import Result, ErrorResult, Info, Extra
from tools import http_utils, store
from core import config
from core.type import Video
from tools.store import make_path

headers = {
    "accept": "*/*",
    "content-type": "json",
    "user-agent": config.user_agent
}

web_headers = {
    "accept": "*/*",
    "sec-ch-ua": "\"Not?A_Brand\";v=\"8\", \"Chromium\";v=\"108\", \"Google Chrome\";v=\"108\"",
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": "\"macOS\"",
    "sec-fetch-dest": "document",
    "sec-fetch-mode": "navigate",
    "sec-fetch-site": "none",
    "sec-fetch-user": "?1",
    "upgrade-insecure-requests": "1",
    "cookie": config.bilibili_cookie,
    "user-agent": config.web_user_agent,
}

user_headers = {
    "Accept": "json",
    "Sec-Ch-Ua": "\"Not?A_Brand\";v=\"8\", \"Chromium\";v=\"108\", \"Google Chrome\";v=\"108\"",
    "Sec-Ch-Ua-mobile": "?0",
    "Sec-Ch-Ua-Platform": "\"macOS\"",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-site",
    "Origin": "https://www.bilibili.com",
    "Cookie": config.bilibili_cookie,
    "User-Agent": config.web_user_agent
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
        print(text)
        if "bilibili" in text:
            urls = re.findall(r'(?<=www\.bilibili\.com\/video\/).+', text, re.I | re.M)
            if urls:
                return "https://www.bilibili.com/video/" + urls[0]
            return None

        urls = re.findall(r'(?<=b23\.tv\/)\w+', text, re.I | re.M)
        print(urls)
        if len(urls) == 0:
            return None
        url = "https://b23.tv/" + urls[0]
        res = http_utils.get(url, header=headers, redirect=False)
        url = res.headers['location']
        print(url)
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
    def get_info(cls, url: str) -> Result:
        burl = cls.get_url(url)
        if burl is None:
            print('error')
            return ErrorResult.URL_NOT_INCORRECT

        video_data = BiliBiliService.get_data(burl)

        bvid = video_data['bvid']

        res = http_utils.get('https://api.bilibili.com/x/player/pagelist',
                             param={'bvid': bvid, 'jsonp': 'jsonp'}, header=headers)
        if http_utils.is_error(res):
            return Result.error(res)

        data = json.loads(res.content)

        p = re.findall(r"(?<=p=)(\d)", burl)
        if len(p) == 0:
            index = 0
        else:
            index = int(p[0]) - 1

        try:
            cid = data['data'][index]['cid']
        except (KeyError, IndexError):
            return ErrorResult.VIDEO_ADDRESS_NOT_FOUNT

        res = http_utils.get(url, header=user_headers)
        result = re.findall(r'(?<=<script>window.__playinfo__=).*(?=</script><script>)', res.text)
        data = json.loads(result[0])

        extra = None
        try:
            videos = [video for video in data['data']['dash']['video']]
            audios = [audio for audio in data['data']['dash']['audio']]
            extra = Extra(videos=videos, audios=audios)
        except (KeyError, IndexError):
            try:
                url = data['data']['durl'][0]['url']
            except (KeyError, IndexError):
                return ErrorResult.VIDEO_ADDRESS_NOT_FOUNT

        info = Info(platform=vtype)
        info.filename = str(cid) + ".mp4"
        info.cover = video_data['pic']
        info.desc = video_data['title']
        info.video = url
        info.extra = extra
        return Result.success(info)

    @staticmethod
    def get_data(url: str) -> dict:
        res = http_utils.get(url, header=web_headers)
        data = re.findall(r'(?<="videoData":).*(?=,"upData")', res.text)
        return json.loads(data[0])

    @classmethod
    def download_header(cls) -> dict:
        return download_headers

    # @classmethod
    # def download(cls, url) -> HttpResponse:
    #     return cls.proxy_download(vtype, url, download_headers, ".mp4", mode=0)

    @classmethod
    def complex_download(cls, info: Info):
        index = info.filename.split('.')[0]
        video_url, audio_url = "", ""

        qn = 0
        for v in info.extra.videos:
            if v['bandwidth'] <= qn:
                continue
            video_url = v['baseUrl']
            qn = v['bandwidth']

        qn = 0
        for v in info.extra.audios:
            if v['bandwidth'] <= qn:
                continue
            audio_url = v['baseUrl']
            qn = v['bandwidth']

        res = http_utils.get(url=video_url, header=download_headers)
        if http_utils.is_error(res):
            return HttpResponseServerError(str(res))
        if len(res.content) < 1024:
            return HttpResponseServerError("作品下载失败")

        vfile = store.save(vtype, res, "tmp_" + index, ".mp4")
        res.close()

        res = http_utils.get(url=audio_url, header=download_headers)
        if http_utils.is_error(res):
            return HttpResponseServerError(str(res))
        afile = store.save(vtype, res, "tmp_" + index, ".aac")
        res.close()

        output = make_path(vtype.value, info.filename)
        tools.ffmpeg.concat(vfile, afile, output)

        os.remove(vfile)
        os.remove(afile)


if __name__ == '__main__':
    # BiliBiliService.fetch('https://www.bilibili.com/video/BV17s411P7oi?p=5&share_source=copy_web')
    BiliBiliService.fetch('https://www.bilibili.com/video/BV1k24y1N7iu/')


