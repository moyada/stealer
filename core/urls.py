from django.urls import path

from core import apis

urlpatterns = [
    path('list', apis.video_mapper, name='list'),
    path('fetch', apis.fetch, name='fetch'),
    path('download', apis.download, name='download'),
]