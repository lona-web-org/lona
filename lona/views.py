def frontend(request):
    return {
        'template': request.server.settings.FRONTEND_TEMPLATE,
    }


def not_found_404(request):
    return {
        'template': request.server.settings.NOT_FOUND_404_TEMPLATE,
    }


def internal_error_500(request):
    return {
        'template': request.server.settings.INTERNAL_ERROR_500_TEMPLATE,
    }
