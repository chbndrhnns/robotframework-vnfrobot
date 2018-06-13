VENV:=. .robot/bin/activate
TO_CONSOLE:=$(or ${VNFROBOT_T_CONSOLE}, True)
LOGLEVEL:=$(or ${VNFROBOT_LOG_LEVEL}, DEBUG)
VARS:=VNFROBOT_TO_CONSOLE=${TO_CONSOLE} VNFROBOT_RESPECT_BREAKPOINTS=False PYTHONPATH=${PYTHONPATH}:vnfrobot:tests
PYTEST_CMD:=pytest -s
PWD:=$(shell pwd)

# app1
APP1_ROBOT:=app1.robot
APP1_DIR:=apps/dc-python-redis
APP1_LOGS:=logs/app1/
APP1_LOGS_ITER:=logs/app1-iter/
APP1_NAME:=app1

# app2
APP2_ROBOT:=app2.robot
APP2_DIR:=apps/dc-haproxy
APP2_LOGS:=logs/app2/
APP2_NAME:=app2


ROBOT_CMD:=robot --timestampoutputs --loglevel ${LOGLEVEL}

# validate that there is a Docker instance running in swarm mode
prepare:
	@find . -name '*.pyc' -delete
	@docker ps > /dev/null 2>&1 || echo "Docker is not running."
	@(docker info | grep "Swarm: active" > /dev/null 2>&1) || echo "Docker needs to be running Swarm mode."

prepare-steps:
	@rm -rf ${APP1_LOGS_ITER}*.html

# run a webserver for browsing the log files
run-logserver:
	@live-server --open=logs/report.html

app1-steps-pdf:
	for file in ${APP1_LOGS_ITER}*.html; do \
		puppeteer print ${PWD}/$${file} ${PWD}/$${file}.pdf; \
	done

app1-steps: prepare prepare-steps app1-iter-1 app1-iter-2 app1-iter-2-refactor app1-iter-3-1 app1-iter-3-2 app1-iter-4-1 app1-iter-4-2 app1-steps-pdf

# run tests for app1
app1: prepare
	(docker-compose -f ${APP1_DIR}/docker-compose.yml pull)
	(docker stack ps ${APP1_NAME} > /dev/null 2>&1) || (docker stack deploy -c ${APP1_DIR}/docker-compose.yml ${APP1_NAME})
	(VNFROBOT_USE_DEPLOYMENT=app1 \
	${VENV} && ${VARS} ${ROBOT_CMD} -d ${APP1_LOGS} ${APP1_DIR}) || echo true
	@docker stack rm ${APP1_NAME}
	@docker volume rm -f ${APP1_NAME}_redis_data || echo true


app1-iter-1: prepare
	(docker-compose -f ${APP1_DIR}/app1-iter-1.yml pull)
	(${VENV} && ${VARS} ${ROBOT_CMD} -d ${APP1_LOGS_ITER} ${APP1_DIR}/app1-iter-1.robot) || echo true
	@docker stack rm app1-iter-1
	@docker volume rm -f app1-iter-1_redis_data || echo true

app1-iter-2: prepare
	(docker-compose -f ${APP1_DIR}/app1-iter-2.yml pull)
	(${VENV} && ${VARS} ${ROBOT_CMD} -d ${APP1_LOGS_ITER} ${APP1_DIR}/app1-iter-2.robot) || echo true
	@docker stack rm app1-iter-2
	@docker volume rm -f app1-iter-2_redis_data || echo true

app1-iter-2-refactor: prepare
	(docker-compose -f ${APP1_DIR}/app1-iter-2-refactor.yml pull)
	(${VENV} && ${VARS} ${ROBOT_CMD} -d ${APP1_LOGS_ITER} ${APP1_DIR}/app1-iter-2-refactor.robot) || echo true
	@docker stack rm app1-iter-2-refactor
	@docker volume rm -f app1-iter-2-refactor_redis_data || echo true

app1-iter-3-1: prepare
	(docker-compose -f ${APP1_DIR}/app1-iter-3-1.yml pull)
	(${VENV} && ${VARS} ${ROBOT_CMD} -d ${APP1_LOGS_ITER} ${APP1_DIR}/app1-iter-3-1.robot) || echo true
	@docker stack rm app1-iter-3-1
	@docker volume rm -f app1-iter-3-1_redis_data || echo true

app1-iter-3-2: prepare
	(docker-compose -f ${APP1_DIR}/app1-iter-3-2.yml pull)
	(${VENV} && ${VARS} ${ROBOT_CMD} -d ${APP1_LOGS_ITER} ${APP1_DIR}/app1-iter-3-2.robot) || echo true
	@docker stack rm app1-iter-3-2
	@docker volume rm -f app1-iter-3-2_redis_data || echo true

app1-iter-4-1: prepare
	(docker-compose -f ${APP1_DIR}/app1-iter-4-1.yml pull)
	(${VENV} && ${VARS} ${ROBOT_CMD} -d ${APP1_LOGS_ITER} ${APP1_DIR}/app1-iter-4-1.robot) || echo true
	@docker stack rm app1-iter-4-1
	@docker volume rm -f app1-iter-4-1_redis_data || echo true

app1-iter-4-2: prepare
	(docker-compose -f ${APP1_DIR}/app1-iter-4-2.yml pull)
	(${VENV} && ${VARS} ${ROBOT_CMD} -d ${APP1_LOGS_ITER} ${APP1_DIR}/app1-iter-4-2.robot) || echo true
	@docker stack rm app1-iter-4-2
	@docker volume rm -f app1-iter-4-2_redis_data || echo true


# run tests for app2
app2: prepare
	(docker stack ps ${APP2_NAME} > /dev/null 2>&1 || docker stack deploy -c ${APP2_DIR}/docker-compose.yml ${APP2_NAME})
	(VNF_USE_DEPLOYMENT=app2 \
	${VENV} && ${VARS} ${ROBOT_CMD} -e 'no' -d ${APP2_LOGS} ${APP2_DIR}) || echo true
	@docker volume rm -f ${APP2_NAME}_redis_data || echo true

# run unit tests
test-unit: prepare
	${VENV} && ${VARS} ${PYTEST_CMD} --ignore='tests/fixtures' --ignore 'tests/keywords' -m 'not integration' tests

# run integration tests
test-integration: prepare
	${VENV} && ${VARS} ${PYTEST_CMD} -m 'integration' tests

# run keyword tests
test-keywords: prepare
	(docker stack ls | grep test-2svc) || (docker stack deploy -c tests/fixtures/dc-test-2svc.yml test-2svc)
	${VENV} && ${VARS} ${PYTEST_CMD} -m 'keyword' tests
	(docker stack rm test-2svc) || true

# run all tests except for the appX tests
test: test-unit test-integration test-keywords
	echo true

install-requirements:
	npm install -g live-server

serve-docs:
	python -m rfhub --root /doc apps/lang

download-tools: tools-goss

# download goss
tools-goss:
	curl -L https://github.com/aelsabbahy/goss/releases/download/v0.3.5/goss-linux-386 -o bin/goss-linux-386
	curl -L https://github.com/aelsabbahy/goss/releases/download/v0.3.5/goss-linux-amd64 -o bin/goss-linux-amd64
	chmod +x bin/*

# build a Docker image with vnf-robot
build: test-unit
	docker build -t vnfrobot .
