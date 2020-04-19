import re
from typing import Optional

from django.http import HttpResponse, FileResponse

from core.model import Result


class Service:

    @classmethod
    def index(cls, url) -> Optional[str]:
        index = re.findall(r'(?<=com\/)\w+', url)
        try:
            return index[0]
        except IndexError:
            return None

    @classmethod
    def fetch(cls, url: str, model=0) -> Result:
        pass

    @classmethod
    def download(cls, url: str) -> HttpResponse:
        pass

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
