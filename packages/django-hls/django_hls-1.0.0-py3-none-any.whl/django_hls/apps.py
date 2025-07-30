import logging
import sys
from django.apps import AppConfig
from django_hls.conf import get_setting

class DjangoHlsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'django_hls'

    def ready(self):
        import django_hls.tasks
        import django_hls.models

        # Only test when celery is not running (i.e. we are running Django itself)
        if get_setting('USE_CELERY') and not any("celery" in arg for arg in sys.argv):
            from django_hls.utils import is_celery_running
            try:
                celery_status = is_celery_running()
                if celery_status:
                    logging.info("Celery is enabled and running. Workers: %s", celery_status)
                else:
                    raise RuntimeError("Celery is enabled, but no workers are responding.")
            except Exception as e:
                logging.exception("Failed to ping Celery workers.")
                raise RuntimeError("Celery is required but not responding.") from e
