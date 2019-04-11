FROM python:3.7-slim

WORKDIR /home/code

RUN apt-get update && apt-get upgrade -y && apt-get install -y redis-server gcc libglib2.0-0 libsm-dev libopencv-*

COPY ./requirements.txt ./
RUN pip install -r requirements.txt

COPY ./resource/ ./resource/
COPY ./src/ ./src/
COPY ./templates/ ./templates/
COPY ./server.py ./server.py

CMD python server.py