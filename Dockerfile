FROM python:3.13
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
run python manage.py collectstatic --noinput
EXPOSE 10000
CMD ["gunicorn","To do task management.wsgi:application","--bind","0.0.0.0:10000"]