from python:3.6

RUN pip install flask

WORKDIR /app
COPY requirements.txt /tmp/requirements.txt
RUN pip install --upgrade pip setuptools
RUN pip install -r /tmp/requirements.txt
ADD frontend /app
RUN ls /app

RUN python manage.py migrate
CMD python manage.py runserver
