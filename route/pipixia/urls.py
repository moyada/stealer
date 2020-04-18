from django.urls import path

from route.pipixia import views

urlpatterns = [
    path('fetch', views.fetch, name='fetch'),
    path('download', views.download, name='download'),
]