#!/usr/bin/env bash

set +x

. ~/.virtualenvs/robot/bin/activate
PYTHONPATH=$PYTHONPATH:$(pwd)/vnf-robot robot $*