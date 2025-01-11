ENV ?= test
export ENV

NAMESPACE := dynamicalsystem
PACKAGE_NAME := halogen

.PHONY:
	publish, test

all: test build check publish

build: test
	uv build --wheel --package ${NAMESPACE}.${PACKAGE_NAME}

check: build
	uvx twine check dist/*

publish: check
	uvx twine upload dist/*

test:
	pytest --pyargs dynamicalsystem.pytests
