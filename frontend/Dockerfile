from python:3.6

RUN pip install flask

COPY ./app /app
WORKDIR /app
COPY requirements.txt /tmp/requirements.txt
RUN pip install --upgrade pip setuptools
RUN pip install -r /tmp/requirements.txt

CMD python app.py