from django.http import HttpResponse, FileResponse, HttpResponseServerError

from core import config, handler_mapper
from core.model import Info
from tools import store, http_utils

header = {
    "accept": "*/*",
    "accept-encoding": "identity;q=1, *;q=0",
    "accept-language": "zh-CN,zh;q=0.9,ja;q=0.8,en;q=0.7,zh-TW;q=0.6,de;q=0.5,fr;q=0.4,ca;q=0.3,ga;q=0.2",
    "range": "bytes=0-",
    "sec-fetch-dest": "video",
    "sec-fetch-mode": "no-cors",
    "sec-fetch-site": "cross-sit",
    "user-agent": config.user_agent
}


def download(info: Info) -> HttpResponse:
    file = store.find_file(info.platform, info.filename)
    if file is not None:
        return make_stream_response(file, info.filename)

    service = handler_mapper.get_service(info.platform)
    if info.extra is not None:
        service.complex_download(info)
    elif info.video != '':
        res = http_utils.get(url=info.video, header=service.download_header())
        if http_utils.is_error(res):
            return HttpResponseServerError(str(res))
        if len(res.content) < 1024:
            return HttpResponseServerError("作品下载失败")
        store.save_file(info.platform, res, info.filename)
        res.close()
    else:
        store.save_image(info.platform, info.images, info.filename)

    file = store.find_file(info.platform, info.filename)
    if file is not None:
        return make_stream_response(file, info.filename)
    return HttpResponseServerError('download error')


def make_stream_response(file, filename) -> HttpResponse:
    try:
        # 设置响应头
        # StreamingHttpResponse将文件内容进行流式传输，数据量大可以用这个方法
        response = FileResponse(file)
        # 以流的形式下载文件,这样可以实现任意格式的文件下载
        response['Content-Type'] = 'application/octet-stream'
        # Content-Disposition就是当用户想把请求所得的内容存为一个文件的时候提供一个默认的文件名
        response['Content-Disposition'] = 'attachment;filename="{}"'.format(filename)
    except Exception as e:
        response = HttpResponse(e)
    # finally:
    #     file.close()
    return response
