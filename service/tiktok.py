import io
import json
import re

from django.http import HttpResponse

from core.interface import Service
from core.model import Result, ErrorResult
from tools import http_utils
from core.type import Video


headers = {
    "user-agent": 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.122 Safari/537.36'
}

download_headers = {
    "accept": "*/*",
    "accept-encoding": "identity;q=1, *;q=0",
    "accept-language": "zh-CN,zh;q=0.9,ja;q=0.8,en;q=0.7,zh-TW;q=0.6,de;q=0.5,fr;q=0.4,ca;q=0.3,ga;q=0.2",
    "range": "bytes=0-",
    "sec-fetch-dest": "video",
    "sec-fetch-mode": "no-cors",
    "sec-fetch-site": "cross-sit",
    "user-agent": 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.122 Safari/537.36'
}

vtype = Video.TIKTOK


class TiktokService(Service):

    @classmethod
    def get_prefix_pattern(cls) -> str:
        return 'vm\.tiktok\.com\/'

    @classmethod
    def make_url(cls, index) -> str:
        return 'http://vm.tiktok.com/' + index

    @classmethod
    def fetch(cls, url: str, mode=0) -> Result:
        url = cls.get_url(url)
        if url is None:
            return ErrorResult.URL_NOT_INCORRECT

        # 请求短链接，获得itemId和dytk
        res = http_utils.get(url, header=headers)
        if http_utils.is_error(res):
            return Result.error(res)

        try:
            props = re.findall(r"(?<=<script id=\"__NEXT_DATA__\" type=\"application\/json\" crossorigin=\"anonymous\">)"
                              r"(.*?)"
                              r"(?=<\/script><script crossorigin=\"anonymous\")", res.text)
        except IndexError:
            return Result.failed(res.reason)

        data = json.loads(str(props[0]))

        try:
            video_url = data['props']['pageProps']['videoData']['itemInfos']['video']['urls'][0]
        except (KeyError, IndexError):
            return ErrorResult.VIDEO_ADDRESS_NOT_FOUNT

        res = http_utils.get(video_url)
        text = res.content.decode('utf-8', 'ignore')

        index = text.index('vid:')
        vid = text[index+4: index+36]
        download_url = 'https://api2.musical.ly/aweme/v1/playwm/?video_id=' + vid
        result = Result.success(download_url)

        if mode == 1:
            result.ref = res.url
        return result

    @classmethod
    def download(cls, url, m=None) -> HttpResponse:
        return cls.proxy_download(vtype, url, download_headers, ".mp4", m)


if __name__ == '__main__':
    TiktokService.fetch('http://vm.tiktok.com/vwQ5YT')
