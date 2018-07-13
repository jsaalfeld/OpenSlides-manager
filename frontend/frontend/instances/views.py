from django.shortcuts import render
from django.http import HttpResponse
from django.apps import apps
import urllib.request, json

def index(request):
    return HttpResponse("Hallo I bims, 1 Welt")

def list(request):
    api_path = 'get_instances'
    BackendConfigModel = apps.get_model('config', 'BackendConfig')
    api_url = BackendConfigModel.objects.get()
    api_url = str(api_url)
    with urllib.request.urlopen(api_url + api_path) as url:
        backend_json = json.loads(url.read().decode())
        print(backend_json)
        retval = ''
        for key, value in backend_json.items():
            retval += ' ' + value
        return HttpResponse(retval)


def detail(request):
    return HttpResponse("details")