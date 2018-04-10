ROBOT_IMAGE_ACCOUNT=registry.gitlab.com/tdd-for-vnfs
ROBOT_IMAGE_NAME=vnf-robot
ROBOT_IMAGE_VERSION=0.1.1

docker:
	cp ../requirements.txt ./gitlab/
	cd gitlab && \
	docker build -t $(ROBOT_IMAGE_ACCOUNT)/$(ROBOT_IMAGE_NAME) .
