from django.conf import settings


def global_settings(request):
    # return any necessary values
    return {
        'JQUERY_DATE_FORMAT': settings.JQUERY_DATE_INPUT_FORMAT,
        'JQUERY_DATETIME_FORMAT': settings.JQUERY_DATETIME_INPUT_FORMAT
    }