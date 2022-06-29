FROM python:slim-buster

WORKDIR /usr/src/app

RUN apt-get update
RUN apt-get -y install zlib1g-dev 

RUN pip install --upgrade pip
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
