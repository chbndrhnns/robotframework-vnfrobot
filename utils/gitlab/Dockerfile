FROM gliderlabs/alpine:latest
MAINTAINER Johannes Rueschel <code@rueschel.de>

RUN apk-install --update py-pip alpine-sdk g++ python-dev openssl-dev libffi libffi-dev bash git

COPY requirements.txt .

RUN \
  pip install -r requirements.txt
