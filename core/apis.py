# Create your views here.
from django.http import HttpResponse, HttpResponseServerError, HttpResponseBadRequest
from django.shortcuts import redirect, render

import core
from core import config
from core.model import ErrorResult
from route import controller
from core.type import Video
import core.config


def index(request):
    return render(request, 'index.html', {
        'items': Video.items_json()
    })


def set_env(request):
    key = request.GET.get('key')
    if not key:
        return HttpResponseBadRequest(ErrorResult.TYPE_NOT_PRESENT.get_data())
    value = request.GET.get('value')
    if not value:
        return HttpResponseBadRequest(ErrorResult.TYPE_NOT_PRESENT.get_data())

    if key == "bilibili":
        config.bilibili_cookie = value


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
