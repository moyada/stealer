import re
from django.http import HttpResponse, HttpResponseServerError

from core.interface import Service
from core.model import Result, ErrorResult
from tools import store, analyzer, http_utils
from core import config
from core.type import Video


headers = {
    "accept": "*/*",
    "accept-encoding": "gzip, deflate, br",
    "accept-language": "en,zh-CN;q=0.9,zh;q=0.8,de;q=0.7",
    "user-agent": config.user_agent
}

download_headers = {
    "accept": "*/*",
    "accept-encoding": "identity;q=1, *;q=0",
    "host": "jsmov2.a.yximgs.com",
    "range": "bytes=0-",
    "sec-fetch-dest": "video",
    "sec-fetch-mode": "no-cors",
    "sec-fetch-site": "cross-sit",
    "user-agent": config.user_agent
}

vtype = Video.KUAISHOU


class KuaishouService(Service):

    @classmethod
    def index(cls, url) -> str:
        index = re.findall(r'(?<=com\/)\w+', url)
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
            return ErrorResult.URL_NOT_INCORRECT

        # 请求短链接，获得itemId和dytk
        res = http_utils.get(url, header=headers)
        if http_utils.is_error(res):
            return Result.error(res)

        html = res.text
        url = re.findall(r"(?<=srcNoMark&#34;:&#34;)(.*?)(?=&)", html)[0]
        if not url:
            return ErrorResult.VIDEO_ADDRESS_NOT_FOUNT

        result = Result.success(url)
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
    KuaishouService.fetch('http://v.kuaishou.com/3ke4p2')

