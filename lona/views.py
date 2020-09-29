def frontend(request):
    return {
        'template': request.server.settings.FRONTEND_TEMPLATE,
        'request': request,
    }


def handle_404(request):
    return {
        'template': request.server.settings.ERROR_404_TEMPLATE,
        'request': request,
    }


def handle_500(request, exception):
    return {
        'template': request.server.settings.ERROR_500_TEMPLATE,
        'request': request,
        'exception': exception,
    }
