
from django.http import *

# Create your views here.
import douyin.service
import kuaishou.service
from stealer.interface import Service
from tools.type import Video


routes = {
    Video.DOUYIN: douyin.service.INSTANCE,
    Video.KUAISHOU: kuaishou.service.INSTANCE,
}


def get_service(vtype: Video) -> Service:
    return routes.get(vtype)


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
