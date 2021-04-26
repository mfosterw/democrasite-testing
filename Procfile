web: newrelic-admin run-program gunicorn democrasite.wsgi
worker: newrelic-admin run-program celery --app=democrasite.celery_app worker --loglevel=INFO
release: python manage.py migrate
