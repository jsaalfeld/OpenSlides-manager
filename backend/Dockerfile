from python:3.6

RUN apt-get update && \
    apt-get install -y \
     apt-transport-https \
     ca-certificates \
     curl \
     gnupg2 \
     software-properties-common && \
    curl -fsSL https://download.docker.com/linux/debian/gpg | apt-key add - && \
    apt-key fingerprint 0EBFCD88 && \
    add-apt-repository \
    "deb [arch=amd64] https://download.docker.com/linux/debian \
     $(lsb_release -cs) \
     stable" && \
    apt-get update && \
    apt-get install -y docker-ce

RUN pip install flask

COPY ./app /app
WORKDIR /app
COPY requirements.txt /tmp/requirements.txt
RUN pip install --upgrade pip setuptools
RUN pip install -r /tmp/requirements.txt

CMD python app.py