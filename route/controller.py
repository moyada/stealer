from django.http import *

# Create your views here.
from core import handler_mapper
from core.model import ErrorResult
from core.type import Video


def fetch(vtype: Video, request):
    url = request.GET.get('url')
    if url is None:
        return HttpResponseBadRequest(ErrorResult.URL_NOT_PRESENT.get_data())

    service = handler_mapper.get_service(vtype)
    result = service.fetch(url)
    if result.is_success():
        return HttpResponse(result.get_data())
    return HttpResponseServerError(result.get_data())


def download(vtype: Video, request):
    url = request.GET.get('url')
    if url is None:
        return HttpResponseBadRequest(ErrorResult.URL_NOT_PRESENT.get_data())

    service = handler_mapper.get_service(vtype)
    response = service.download(url)
    return response
