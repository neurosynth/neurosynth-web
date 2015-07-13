from celery import Celery, Task
from nsweb.initializers import settings


def make_celery(app):
    """ Initialize and return a new Celery instance """
    celery = Celery(app.import_name, broker=settings.CELERY_BROKER_URL,
                    backend=settings.CELERY_RESULT_BACKEND)
    celery.conf.update(CELERY_ACCEPT_CONTENT=['json'],
                       CELERY_TASK_SERIALIZER='json',
                       CELERY_RESULT_SERIALIZER = 'json')
    TaskBase = celery.Task

    class ContextTask(TaskBase):
        abstract = True

        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)
    celery.Task = ContextTask
    return celery
