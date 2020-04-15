from django.http import HttpResponse, HttpResponseRedirect


def index(request):
    return HttpResponse()


def ip(request):
    return HttpResponseRedirect('http://httpbin.org/ip')
