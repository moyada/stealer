# Create your views here.
from django.http import HttpResponse, HttpResponseServerError, HttpResponseBadRequest
from django.shortcuts import redirect, render

import core
from core.model import ErrorResult
from route import controller
from core.type import Video


def index(request):
    return render(request, 'index.html', {
        'items': Video.items_json()
    })


def ip(request):
    return redirect('http://httpbin.org/ip')


def fetch(request):
    itype = request.GET.get('type')
    if itype is None:
        return HttpResponseBadRequest(ErrorResult.TYPE_NOT_PRESENT.get_data())

    vtype = core.type.video_mapper.get(itype)
    if vtype is None:
        return HttpResponseServerError(ErrorResult.MAPPER_NOT_EXIST.get_data())

    return controller.fetch(vtype, request)


def download(request):
    itype = request.GET.get('type')
    if itype is None:
        return HttpResponseBadRequest(ErrorResult.TYPE_NOT_PRESENT.get_data())

    vtype = core.type.video_mapper.get(itype)
    if vtype is None:
        return HttpResponseServerError(ErrorResult.MAPPER_NOT_EXIST.get_data())

    return controller.download(vtype, request)


def video_mapper(request):
    return HttpResponse(core.type.video_mapper_json)
