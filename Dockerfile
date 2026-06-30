FROM python:3.10

WORKDIR /

COPY . /

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

CMD ["waitress-serve", "--host=0.0.0.0", "--port=8000", "projectdata.wsgi:application"]
