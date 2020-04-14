# Create your views here.
from stealer import route
from tools.type import Video


def fetch(request):
    return route.fetch(Video.KUAISHOU, request)


def download(request):
    return route.download(Video.KUAISHOU, request)
