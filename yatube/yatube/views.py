from django.http import HttpResponse


def index(request):
    return HttpResponse('Главная страница')


def group(request):
    return HttpResponse('Страницы сообществ')
