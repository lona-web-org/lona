FROM mcr.microsoft.com/playwright:v1.45.1-jammy

ARG DEBIAN_FRONTEND=noninteractive
ARG PYTHON_VERSIONS="3.8 3.9 3.10 3.11"
ARG PYTHON_VERSION="3.10"

ENV PYTHONUNBUFFERED=1

RUN apt update && \
	apt install -y software-properties-common && \
	add-apt-repository ppa:deadsnakes/ppa && \
	apt update && \
	apt install -y python3-pip && \
	for version in ${PYTHON_VERSIONS}; do \
		apt install -y \
			python${version} \
			python${version}-dev \
			python${version}-venv && \
		python${version} -m ensurepip --upgrade \
	; done && \
	ln -s $(which python${PYTHON_VERSION}) /usr/local/bin/python && \
	ln -s $(which python${PYTHON_VERSION}) /usr/local/bin/python3

RUN pip3 install --upgrade \
	pip \
	tox
