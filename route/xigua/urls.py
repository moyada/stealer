from django.urls import path

from route.xigua import views

urlpatterns = [
    path('fetch.html', views.fetch, name='fetch'),
    path('download.html', views.download, name='download'),
]