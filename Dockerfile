FROM python:3.7-slim

WORKDIR /home/code

RUN apt-get update && apt-get upgrade -y && apt-get install -y build-essential libffi-dev libssl-dev libmariadbclient-dev

COPY ./requirements.txt ./
RUN pip install -r requirements.txt

COPY ./alembic.ini ./
COPY ./migrations/ ./migrations/

RUN cd /home/code && alembic upgrade head

COPY ./static ./static/
COPY ./src/ ./src/
COPY ./templates/ ./templates/

CMD gunicorn -w 4 -b 0.0.0.0:8085 src.core.server:app
