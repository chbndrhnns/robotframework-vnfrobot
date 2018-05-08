run-logserver:
	live-server --open=logs/report.html

test-unit:
	. .robot/bin/activate && \
	PYTHONPATH=$PYTHONPATH:vnfrobot:tests pytest -s tests -m 'not integration'

test-integration:
	. .robot/bin/activate && \
    PYTHONPATH=$PYTHONPATH:vnfrobot:tests pytest -s tests -m 'not keyword' -m 'not flaky'

test-keywords:
	. .robot/bin/activate && \
    PYTHONPATH=$PYTHONPATH:vnfrobot:tests pytest -s tests -m 'keyword'

test: test-unit test-integration test-keywords
	echo true

robot-tests:
	. .robot/bin/activate && \
	PYTHONPATH=$$PYTHONPATH:$$(pwd)/vnf-robot robot \
	-d logs \
	--timestampoutputs \
	tests/*.robot

easy-voting-tests:
	. .robot/bin/activate; \
	PYTHONPATH=$$PYTHONPATH:$$(pwd)/vnf-robot robot \
	-d logs \
	apps/easy-voting-app/easy-voting-app-simple.robot

install-requirements:
	npm install -g live-server

serve-docs:
	python -m rfhub --root /doc apps/lang

download-tools: tools-goss

tools-goss:
	curl -L https://github.com/aelsabbahy/goss/releases/download/v0.3.5/goss-linux-386 -o bin/goss-linux-386
	curl -L https://github.com/aelsabbahy/goss/releases/download/v0.3.5/goss-linux-amd64 -o bin/goss-linux-amd64
	chmod +x bin/*
