import json
import re
from typing import Optional

from django.http import HttpResponse, FileResponse, HttpResponseServerError

from core.model import Result
from tools import store, http_utils


class Service:

    @classmethod
    def get_prefix_pattern(cls) -> str:
        pass

    @classmethod
    def make_url(cls, index) -> str:
        pass

    @classmethod
    def get_url(cls, text: str) -> Optional[str]:
        urls = re.findall(r'(?<=' + cls.get_prefix_pattern() + ')\w+', text, re.I | re.M)
        if urls:
            return cls.make_url(urls[0])
        return None

    @classmethod
    def index(cls, url) -> Optional[str]:
        index = re.findall(r'(?<=com\/)\w+', url)
        try:
            return index[0]
        except IndexError:
            return None

    @classmethod
    def fetch(cls, url: str, mode=0) -> Result:
        """
        获取视频地址
        :param url:
        :param mode:
        :return:
        """
        pass

    @staticmethod
    def download_header():
        pass

    @classmethod
    def download(cls, url: str) -> HttpResponse:
        """
        下载视频
        :param url:
        :return:
        """
        result = cls.fetch(url)
        if result.is_success():
            name = cls.index(url) + '.mp4'
            url = result.get_data()
            data = json.dumps({'name': name, 'url': url})
            return HttpResponse(data)
        return HttpResponseServerError(result.get_data())

    @classmethod
    def proxy_download(cls, vtype, url, header: dict, mode=1) -> HttpResponse:
        # 检查文件
        index = cls.index(url)
        file = store.find(vtype, index)
        if file is not None:
            return Service.stream(file, index)

        result = cls.fetch(url, mode=mode)
        if not result.is_success():
            return HttpResponseServerError(result.get_data())

        if mode == 1:
            header = header.copy()
            header['referer'] = result.ref

        res = http_utils.get(url=result.get_data(), header=header)
        if http_utils.is_error(res):
            return HttpResponseServerError(str(res))

        store.save(vtype, res, index)
        res.close()

        file = store.find(vtype, index)
        return Service.stream(file, index)

    @staticmethod
    def stream(file, index) -> HttpResponse:
        try:
            # 设置响应头
            # StreamingHttpResponse将文件内容进行流式传输，数据量大可以用这个方法
            response = FileResponse(file)
            # 以流的形式下载文件,这样可以实现任意格式的文件下载
            response['Content-Type'] = 'application/octet-stream'
            # Content-Disposition就是当用户想把请求所得的内容存为一个文件的时候提供一个默认的文件名
            response['Content-Disposition'] = 'attachment;filename="{}"'.format(index + '.mp4')
        except Exception as e:
            response = HttpResponse(e)
        return response
