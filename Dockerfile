
FROM python:3.10

WORKDIR /

COPY . /

RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt \
    && pip install --no-cache-dir gunicorn

# CMD ["python", "manage.py", "collectstatic", "--noinput"]

EXPOSE 8000

CMD ["sh", "-c", "python manage.py collectstatic --noinput && gunicorn projectdata.wsgi:application --bind 0.0.0.0:8000"]
