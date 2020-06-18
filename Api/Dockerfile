FROM debian:latest

MAINTAINER Eliot courtel <eliot.courtel@wanadoo.fr>

RUN apt-get update -y

RUN apt install build-essential libpoppler-cpp-dev pkg-config python3-dev -y
RUN apt install python3-pip -y
RUN pip3 install pdftotext

RUN apt-get install tesseract-ocr -y
RUN apt-get install libtesseract-dev -y

RUN pip3 install pytesseract

WORKDIR /home/root/

COPY ./requirements.txt ./
RUN pip3 install -r requirements.txt

COPY ./ ./API

RUN mkdir files

ENTRYPOINT python3 ./API/server.py
