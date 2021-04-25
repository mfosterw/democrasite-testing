web: gunicorn democrasite.wsgi
worker: celery --app=tasks.app worker --loglevel=INFO
