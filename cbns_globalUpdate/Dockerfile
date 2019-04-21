FROM python:3.7-slim

WORKDIR /home/code

COPY ./requirements.txt ./
RUN pip install -r requirements.txt

COPY update.py ./

CMD python update.py