# Create your views here.
from route import controller
from core.type import Video


vtype = Video.BILIBILI


def fetch(request):
    return controller.fetch(vtype, request)


def download(request):
    return controller.download(vtype, request)
