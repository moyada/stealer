from django.shortcuts import render
from django.http import *

# Create your views here.
from douyin import service


def fetch(request):
    url = request.GET.get('url')
    if url is None:
        return HttpResponseBadRequest('url not present.')
    link = service.get_download(url)
    if link == "":
        return HttpResponseServerError("url analyse error.")
    return HttpResponse(link)


def download(request):
    url = request.GET.get('url')
    if url is None:
        return HttpResponseBadRequest('url not present.')
    return service.download(url)
