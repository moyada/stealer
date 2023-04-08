from django.urls import path

from core import apis
from route import controller

urlpatterns = [
    path('list', apis.video_mapper, name='list'),
    path('fetch', apis.fetch, name='fetch'),
    path('download2', apis.download, name='download2'),
    path('info', controller.get_info, name='info'),
    path('download', controller.download_file, name='download'),
]