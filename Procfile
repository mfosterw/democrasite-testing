web: gunicorn democrasite.wsgi
worker: celery --app=democrasite.celery_app worker --loglevel=INFO
release: python manage.py migrate
