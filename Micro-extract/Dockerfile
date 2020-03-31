FROM debian:latest

MAINTAINER Eliot courtel <eliot.courtel@wanadoo.fr>

RUN apt-get update -y

RUN apt install build-essential libpoppler-cpp-dev pkg-config python3-dev -y
RUN apt install python3-pip -y
RUN pip3 install pdftotext
WORKDIR /home/root/

COPY ./requirements.txt ./
RUN pip3 install -r requirements.txt

COPY ./API/ ./API

ENTRYPOINT python3 ./API/server.py
