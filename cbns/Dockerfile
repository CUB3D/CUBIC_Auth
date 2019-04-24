FROM python:3.7-slim

WORKDIR /home/code

RUN apt update && apt upgrade -y && apt install -y gcc

COPY ./requirements.txt ./
RUN pip install -r requirements.txt

COPY server.py ./

#CMD hypercorn -w 16 --error-log - --access-log - -b 0.0.0.0:8080 --debug server:app
CMD uvicorn --host 0.0.0.0 --port 8080 --log-level info server:app