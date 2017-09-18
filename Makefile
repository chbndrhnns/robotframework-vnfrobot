run-logserver:
	live-server --open=logs/report.html

robot-tests:
	. .robot/bin/activate && \
	PYTHONPATH=$$PYTHONPATH:$$(pwd)/vnf-robot robot \
	-d logs \
	--timestampoutputs \
	tests/*.robot

robot-http-test:
	. .robot/bin/activate && \
	PYTHONPATH=$$PYTHONPATH:$$(pwd)/vnf-robot robot \
	-d logs \
	tests/HTTPTest.robot

socket-tests:
	. .robot/bin/activate && \
	PYTHONPATH=$$PYTHONPATH:$$(pwd)/vnf-robot robot \
	-d logs \
	tests/SocketTest.robot

install-requirements:
	npm install -g live-server