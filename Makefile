VENV:=. .robot/bin/activate
TO_CONSOLE:=False
VARS:=VNFROBOT_TO_CONSOLE=${TO_CONSOLE} PYTHONPATH=$PYTHONPATH:vnfrobot:tests
PYTEST_CMD:=pytest -s
LOGLEVEL:=INFO
ROBOT_CMD:=robot -d logs --timestampoutputs --loglevel ${LOGLEVEL}
APP1_DIR:=tests/fixtures/dc-python-redis/dc-python-redis.robot
APP2_DIR:=tests/fixtures/dc-haproxy/dc-haproxy.robot

run-logserver:
	live-server --open=logs/report.html

app1:
	${VENV} && ${VARS} ${ROBOT_CMD} ${APP1_DIR}

app2:
	${VENV} && ${VARS} ${ROBOT_CMD} ${APP2_DIR}


test-unit:
	${VENV} && ${VARS} ${PYTEST_CMD} --ignore='tests/fixtures' --ignore 'tests/keywords' -m 'not integration' tests

test-integration:
	${VENV} && ${VARS} ${PYTEST_CMD} -m 'integration' tests

test-keywords:
	(docker stack ls | grep test-2svc) || (docker stack deploy -c tests/fixtures/dc-test-2svc.yml test-2svc)
	${VENV} && ${VARS} ${PYTEST_CMD} -m 'keyword' tests
	(docker stack rm test-2svc) || true

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
