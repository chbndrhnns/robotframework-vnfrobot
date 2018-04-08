#!/usr/bin/env bash

. ~/.virtualenvs/robot/bin/activate
PYTHONPATH=$PYTHONPATH:$(pwd)/vnf-robot robot $*