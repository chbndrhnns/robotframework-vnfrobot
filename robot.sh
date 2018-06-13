#!/usr/bin/env sh

set +x

. .robot/bin/activate
PYTHONPATH=$PYTHONPATH:$(pwd)/vnfrobot robot -e 'no' $*