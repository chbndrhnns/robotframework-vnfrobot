VENV:=. .robot/bin/activate
TO_CONSOLE:=False
VARS:=VNFROBOT_TO_CONSOLE=${TO_CONSOLE} PYTHONPATH=${PYTHONPATH}:vnfrobot:tests
PYTEST_CMD:=pytest -s
LOGLEVEL:=INFO

# app1
APP1_ROBOT:=app1.robot
APP1_DIR:=tests/fixtures/dc-python-redis
APP1_LOGS:=logs/app1
APP1_NAME:=app1

# app2
APP2_ROBOT:=app2.robot
APP2_DIR:=tests/fixtures/dc-haproxy
APP2_LOGS:=logs/app2
APP2_NAME:=app2


ROBOT_CMD:=robot --timestampoutputs --loglevel ${LOGLEVEL}

prepare:
	@find . -name '*.pyc' -delete
	@docker ps > /dev/null 2>&1 || echo "Docker is not running."
	@(docker info | grep "Swarm: active" > /dev/null 2>&1) || echo "Docker needs to be running Swarm mode."

run-logserver:
	@live-server --open=logs/report.html

app1: prepare
	(docker stack ps ${APP1_NAME} > /dev/null 2>&1) || (docker stack deploy -c ${APP1_DIR}/docker-compose.yml ${APP1_NAME})
	(VNFROBOT_USE_DEPLOYMENT=app1 \
	${VENV} && ${VARS} ${ROBOT_CMD} -d ${APP1_LOGS} ${APP1_DIR}) || echo true
	@docker stack rm ${APP1_NAME}


app2: prepare
	(docker stack ps ${APP1_NAME} > /dev/null 2>&1 || docker stack deploy -c ${APP2_DIR}/docker-compose.yml ${APP2_NAME})
	(VNF_USE_DEPLOYMENT=app2 \
	${VENV} && ${VARS} ${ROBOT_CMD} -d ${APP1_LOGS} ${APP2_DIR}) || echo true
	@docker stack rm ${APP2_NAME}

test-unit: prepare
	${VENV} && ${VARS} ${PYTEST_CMD} --ignore='tests/fixtures' --ignore 'tests/keywords' -m 'not integration' tests

test-integration: prepare
	${VENV} && ${VARS} ${PYTEST_CMD} -m 'integration' tests

test-keywords: prepare
	(docker stack ls | grep test-2svc) || (docker stack deploy -c tests/fixtures/dc-test-2svc.yml test-2svc)
	${VENV} && ${VARS} ${PYTEST_CMD} -m 'keyword' tests
	(docker stack rm test-2svc) || true

test: test-unit test-integration test-keywords
	echo true

install-requirements:
	npm install -g live-server

serve-docs:
	python -m rfhub --root /doc apps/lang

download-tools: tools-goss

tools-goss:
	curl -L https://github.com/aelsabbahy/goss/releases/download/v0.3.5/goss-linux-386 -o bin/goss-linux-386
	curl -L https://github.com/aelsabbahy/goss/releases/download/v0.3.5/goss-linux-amd64 -o bin/goss-linux-amd64
	chmod +x bin/*

build: test-unit
	docker build -t vnfrobot .
