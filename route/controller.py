import json
import logging
from typing import Union, Optional, Any

from django.http import *

from core import handler_mapper, cache, vid_download
from core.model import ErrorResult
from core.type import Video
from tools import store

logger = logging.getLogger('request')


def get_info(request):
    url = request.GET.get('url')
    if url is None:
        return HttpResponseBadRequest(ErrorResult.URL_NOT_PRESENT.get_data())

    vtype, url = get_vtype(url)
    if vtype is None:
        return HttpResponseBadRequest(ErrorResult.URL_NOT_INCORRECT.get_data())

    token = store.get_token(vtype, url)
    info = cache.get(token)
    if info is not None:
        dic = info.to_dict()
        dic['token'] = token
        return HttpResponse(json.dumps(dic))

    logger.info(f'get {vtype.value} video info ==> {url}.')

    service = handler_mapper.get_service(vtype)
    result = service.get_info(url)

    if result.is_success():
        info = result.get_data()
        cache.save(token, info)
        dic = info.to_dict()
        dic['token'] = token
        return HttpResponse(json.dumps(dic))
    return HttpResponseServerError(result.get_data())


def download_file(request):
    url = request.GET.get('url')
    token = request.GET.get('token')
    if url is None and token is None:
        return HttpResponseBadRequest(ErrorResult.URL_NOT_PRESENT.get_data())
    if url is not None:
        vtype, url = get_vtype(url)
        token = store.get_token(vtype, url)

    info = cache.get(token)
    if info is None:
        return HttpResponseNotFound(ErrorResult.VIDEO_INFO_NOT_FOUNT.get_data())

    logger.info(f'download {info.platform.value} ==> {info.desc}.')
    return vid_download.download(info)


def fetch(vtype: Video, request):
    url = request.GET.get('url')
    if url is None:
        return HttpResponseBadRequest(ErrorResult.URL_NOT_PRESENT.get_data())

    vtype = check_vtype(vtype, url)
    if vtype is None:
        return HttpResponseBadRequest(ErrorResult.URL_NOT_INCORRECT.get_data())

    service = handler_mapper.get_service(vtype)
    logger.info('fetch {} <== {}.'.format(vtype.label, url))
    result = service.fetch(url)
    if result.is_success():
        return HttpResponse(result.get_data())
    return HttpResponseServerError(result.get_data())


def download(vtype: Video, request):
    url = request.GET.get('url')
    if url is None:
        return HttpResponseBadRequest(ErrorResult.URL_NOT_PRESENT.get_data())

    vtype = check_vtype(vtype, url)
    if vtype is None:
        return HttpResponseBadRequest(ErrorResult.URL_NOT_INCORRECT.get_data())

    service = handler_mapper.get_service(vtype)
    logger.info('download {} <== {}.'.format(vtype.label, url))
    response = service.download(url)
    return response


def get_vtype(url: str) -> (Optional[Video], str):
    for v, service in handler_mapper.service_mapper.items():
        share_url = service.get_url(url)
        if share_url:
            return v, share_url
    return None, ''


def check_vtype(vtype: Video, url: str) -> Union[Optional[Video], Any]:
    if vtype is not Video.AUTO:
        return vtype

    for v, service in handler_mapper.service_mapper.items():
        if service.get_url(url):
            return v
    return None
