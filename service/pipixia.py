import json
import re
from django.http import HttpResponse, HttpResponseServerError

from stealer.interface import Service
from stealer.model import Result, ErrorResult
from tools import store, analyzer, http_utils, config
from tools.type import Video

headers = {
    "accept": "*/*",
    "accept-encoding": "gzip, deflate",
    "user-agent": config.user_agent
}

share_headers = {
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
    "range": "bytes=0-",
    "sec-fetch-dest": "video",
    "sec-fetch-mode": "no-cors",
    "sec-fetch-site": "cross-sit",
    "user-agent": config.user_agent
}

vtype = Video.PIPIXIA


class PipixiaService(Service):

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

        res = http_utils.get(url, header=headers)
        if http_utils.is_error(res):
            return Result.error(res)

        id = re.findall(r"(?<=item\/)(\d+)(?=\?)", res.url)[0]
        url = "https://h5.pipix.com/bds/webapi/item/detail/?item_id=" + id + "&source=share"

        info_res = http_utils.get(url, header=share_headers)
        if http_utils.is_error(info_res):
            return Result.error(info_res)

        data = json.loads(str(info_res.text))

        try:
            url = data['data']['item']['origin_video_download']['url_list'][0]['url']
        except KeyError:
            return ErrorResult.VIDEO_ADDRESS_NOT_FOUNT

        return Result.success(url)

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

        result = cls.fetch(url)
        if not result.is_success():
            return HttpResponseServerError(result.get_data())

        res = http_utils.get(url=result.get_data(), header=download_headers)
        if http_utils.is_error(res):
            return HttpResponseServerError(str(res))

        store.save(vtype, res, index)
        res.close()

        file = store.find(vtype, index)
        return Service.stream(file, index)


if __name__ == '__main__':
    PipixiaService.fetch('http://h5.pipix.com/s/3asShh')