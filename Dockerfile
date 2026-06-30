FROM python:3.10

WORKDIR /

COPY . /

RUN pip install --upgrade pip
RUN pip install -r requirements.txt
RUN pip install gunicorn

RUN python manage.py collectstatic --noinput

EXPOSE 8000

CMD ["gunicorn", "projectdata.wsgi:application", "--bind", "0.0.0.0:8000"]
