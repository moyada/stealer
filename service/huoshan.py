
import re
from django.http import HttpResponse, HttpResponseServerError

from stealer.interface import Service
from stealer.model import Result, ErrorResult
from tools import store, analyzer, http_utils, config
from tools.type import Video

headers = {
    "user-agent": config.user_agent
}

info_headers = {
    "accept": "*/*",
    "accept-encoding": "gzip, deflate",
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin",
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

vtype = Video.HUOSHAN


class HuoshanService(Service):

    @classmethod
    def index(cls, url) -> str:
        index = re.findall(r'(?<=s\/)\w+', url)
        return index[0]

    @classmethod
    def fetch(cls, url: str, model=0) -> Result:
        """
        获取视频详情
        :param url:
        :param model:
        :return:
        """
        url = analyzer.get_url(vtype, url)
        if url is None:
            return ErrorResult.URL_NOT_FOUNT

        # 请求短链接，获得itemId
        res = http_utils.get(url, header=headers)
        if http_utils.is_error(res):
            return Result.error(res)

        item_id = re.findall(r"(?<=item_id=)\d+(?=\&)", res.url)[0]

        # 视频信息链接
        infourl = "https://share.huoshan.com/api/item/info?item_id=" + item_id

        # 请求长链接，获取play_addr
        url_res = http_utils.get(infourl, header=info_headers)
        if http_utils.is_error(url_res):
            return Result.error(url_res)

        vhtml = str(url_res.text)
        video_id = re.findall(r'(?<=video_id\=)\w+(?=\&)', vhtml)[0]

        if not video_id:
            return ErrorResult.VIDEO_ADDRESS_NOT_FOUNT

        link = "https://api.huoshan.com/hotsoon/item/video/_source/?video_id=" + video_id + "&line=0&app_id=0&vquality=normal"
        result = Result.success(link)

        if model != 0:
            result.ref = res.url
        return result

    @classmethod
    def download(cls, url) -> HttpResponse:
        """
        下载视频
        :param url:
        :return:
        """
        # 检查文件
        index = cls.index(url)
        file = store.find(vtype, index)
        if file is not None:
            return Service.stream(file, index)

        result = cls.fetch(url, model=1)
        if not result.is_success():
            return HttpResponseServerError(result.get_data())

        dheaders = download_headers.copy()
        dheaders['referer'] = result.ref

        res = http_utils.get(url=result.get_data(), header=dheaders)
        if http_utils.is_error(res):
            return HttpResponseServerError(str(res))

        store.save(vtype, res, index)
        res.close()

        file = store.find(vtype, index)
        return Service.stream(file, index)


if __name__ == '__main__':
    HuoshanService.fetch('http://share.huoshan.com/hotsoon/s/eVDEDNYXu78')
