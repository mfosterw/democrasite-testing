web: gunicorn gettingstarted.wsgi
worker: celery --app=tasks.app worker --loglevel=INFO
