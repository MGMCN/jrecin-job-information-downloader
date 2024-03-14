FROM python:3.11-slim-bullseye

LABEL maintainer="MGMCN"

COPY . /APP

WORKDIR /APP

RUN pip3 install -r requirements.txt && \
    mkdir excels

CMD python3 main.py