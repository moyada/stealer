from typing \
    import Type

from django.http import *

# Create your views here.
from service import *
from stealer.interface import Service
from tools.type import Video


routes = {
    Video.DOUYIN: douyin.DouyinService,
    Video.KUAISHOU: kuaishou.KuaishouService,
    Video.HUOSHAN: huoshan.HuoshanService,
    Video.XIGUA: xigua.XiguaService,
    Video.PIPIXIA: pipixia.PipixiaService,
}


def get_service(vtype: Video) -> Type[Service]:
    service = routes.get(vtype)
    if service is None:
        raise ModuleNotFoundError('Not match route, Video type ' + vtype.name)
    return service


def fetch(vtype: Video, request):
    url = request.GET.get('url')
    if url is None:
        return HttpResponseBadRequest('url not present.')

    service = get_service(vtype)
    result = service.fetch(url)
    if result.is_success():
        return HttpResponse(result.get_data())
    return HttpResponseServerError(result.get_data())


def download(vtype: Video, request):
    url = request.GET.get('url')
    if url is None:
        return HttpResponseBadRequest('url not present.')

    service = get_service(vtype)
    response = service.download(url)
    return response
