release: python manage.py migrate && python manage.py collectstatic --noinput
web: gunicorn quickrate.wsgi --log-file -