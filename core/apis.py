# Create your views here.
from django.http import HttpResponse, HttpResponseServerError, HttpResponseBadRequest
from django.shortcuts import redirect, render
import os
import core
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
        v = ""
        if key == "bilibili":
            v = os.environ['bilibili_cookie']
        elif key == "page_wait":
            v = os.environ['page_wait']
        elif key == "headless":
            v = os.environ['headless']
        return HttpResponse(v)

    if key == "bilibili":
        os.environ['bilibili_cookie'] = value
    elif key == "page_wait":
        os.environ['page_wait'] = str(int(value))
    elif key == "headless":
        os.environ['headless'] = value
    return HttpResponse()


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
