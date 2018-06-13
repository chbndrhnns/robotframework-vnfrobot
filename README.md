# vnfrobot

## Getting started

- Fetch the Docker image: `docker pull hubby/vnfrobot`
- Run the image: `docker run --rm -v ${pwd}:/data -v /var/run/docker.sock:/var/run/docker.sock -it hubby/vnfrobot sh`

## Configuration

Configuration is done via environment variables. The following parameters exist:

- `LOG_LEVEL`: set log level, default is `DEBUG`
- `TO_CONSOLE`: output all log messages to console, default is `False`
- `USE_DEPLOYMENT`: use the specified deployment
- `SKIP_UNDEPLOY`: do not remove deployment after the test run
- `RESPECT_BREAKPOINTS`: (for development purposes only) connect to a pydev debugger instance 
and hold on break points
- `DOCKER_HOST`: set Docker engine to use with `vnf-robot`
- `DOCKER_TIMEOUT`: set timeout for connecting to the Docker engine


## Quickstart

- install Docker engine 1.17+
- install docker-compose

- `git clone https://github.com/chbndrhnns/robotframework-vnfrobot`
- `docker pull hubby/vnfrobot:1.0.1`
- `docker stack deploy -c apps/dc-haproxy/docker-compose.yml app2`
- `docker run -v <absolute-path-to-repo>/apps/dc-haproxy:/data -v /var/run/docker.sock:/var/run/docker.sock -it hubby/vnfrobot:1.0.1`


## Installation

Clone repo from `git clone https://github.com/chbndrhnns/robotframework-vnfrobot`.

See `Dockerfile` for the commands that are required to run `vnf-robot`.

Unit and integration tests can be run via `make test-unit`, `make test-integration`, and `make test-keywords`

App1 tests can be executed in the Docker container with `make app1`
App2 tests can be executed in the Docker container with `make app2`