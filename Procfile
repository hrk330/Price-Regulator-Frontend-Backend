web: cd backend && python3 manage.py runserver 0.0.0.0:$PORT
worker: cd backend && python3 -m celery -A price_monitoring worker --loglevel=info
