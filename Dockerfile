FROM python:3.7-slim

WORKDIR /home/code

RUN apt-get update && apt-get upgrade -y && apt-get install -y gcc libmariadbclient-dev
#libglib2.0-0 libsm-dev libopencv-*

COPY ./requirements.txt ./
RUN pip install -r requirements.txt

COPY ./alembic.ini ./
COPY ./migrations/ ./migrations/

COPY ./.env ./

#RUN cd /home/code && alembic upgrade head

#COPY ./resource/ ./resource/
#COPY ./src/ ./src/
#COPY ./templates/ ./templates/

#CMD python -m src
CMD gunicorn -b 0.0.0.0:8080 src.core.server:app