FROM python:3.7-slim

WORKDIR /home/code

COPY ./requirements.txt ./
RUN pip install -r requirements.txt

COPY server.py ./

CMD hypercorn -w 16 --error-log - --access-log - -b 0.0.0.0:8080 --debug server:app