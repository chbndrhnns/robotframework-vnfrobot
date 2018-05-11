FROM lgatica/python-alpine:2.7.14
MAINTAINER Johannes Rueschel <code@rueschel.de>

RUN apk add --no-cache make docker

WORKDIR /vnfrobot
COPY requirements.txt .
RUN pip install -U pip

RUN pip install virtualenv
RUN virtualenv .robot

RUN . .robot/bin/activate && pip install -r requirements.txt

COPY . .

