from django.conf import settings


DEFAULTS = {
    'SEGMENT_DURATION': 10,
    'M3U8_FILE_NAME': 'output.m3u8',
    'USE_CELERY' : False,
    'CELERY_QUEUE' : 'celery',
}


def get_setting(name):
    return getattr(settings, f"HLS_{name}", DEFAULTS.get(name))