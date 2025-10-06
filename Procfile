web: cd backend && python manage.py runserver 0.0.0.0:$PORT
worker: cd backend && celery -A price_monitoring worker --loglevel=info
