PROJECT_NAME = $(shell poetry version|awk '{print $$1}')
MODULE_NAME = $(shell poetry version|awk '{print $$1}'|tr '-' '_')
VERSION = $(shell poetry version -s)
DOCKER_REGISTRY = registry.naga.lan
IMAGE_NAME = ${DOCKER_REGISTRY}/${PROJECT_NAME}
OUTPUT_FILENAME = ${PROJECT_NAME}-${VERSION}-bin
WHEEL_NAME = ${DIST_DIR}/${MODULE_NAME}-${VERSION}-py3-none-any.whl

SRC_DIRS := ./${MODULE_NAME}
SRCS := $(shell find $(SRC_DIRS) -name '*.py')

DIST_DIR = ./dist

all: package

build: pyproject.toml ${SRCS}
	poetry build

${WHEEL_NAME}: build

package: ${WHEEL_NAME}
	poetry run shiv --console-script ${PROJECT_NAME} --extend-pythonpath --python '/usr/bin/env python3.10' --compressed --compile-pyc --reproducible --no-modify --root /tmp/shiv --output-file ${DIST_DIR}/${OUTPUT_FILENAME} ${WHEEL_NAME}

containerize: package Dockerfile
	DOCKER_BUILDKIT=1 docker build --build-arg DIST_DIR="${DIST_DIR}" --build-arg OUTPUT_FILENAME="${OUTPUT_FILENAME}" -t ${IMAGE_NAME}:${VERSION} -t ${IMAGE_NAME}:latest .
	docker push ${IMAGE_NAME}:${VERSION}
	docker push ${IMAGE_NAME}:latest

deploy_docker_stack:
	docker service update --image ${IMAGE_NAME}:${VERSION} ${STACK_NAME}_${PROJECT_NAME}

clean: 
	rm -r ${DIST_DIR}/
