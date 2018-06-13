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
