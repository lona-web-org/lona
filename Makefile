SHELL=/bin/bash
PYTHON=python3

PYTHON_ENV_ROOT=envs
PYTHON_DEV_ENV=$(PYTHON_ENV_ROOT)/$(PYTHON)-dev
PYTHON_PACKAGING_ENV=$(PYTHON_ENV_ROOT)/$(PYTHON)-packaging-env

.PHONY: clean doc sdist pytest test ci-test lint isort shell freeze

# development environment #####################################################
$(PYTHON_DEV_ENV): REQUIREMENTS.dev.txt
	rm -rf $(PYTHON_DEV_ENV) && \
	$(PYTHON) -m venv $(PYTHON_DEV_ENV) && \
	. $(PYTHON_DEV_ENV)/bin/activate && \
	pip install pip --upgrade && \
	pip install -r ./REQUIREMENTS.dev.txt

# packaging environment #######################################################
$(PYTHON_PACKAGING_ENV): REQUIREMENTS.packaging.txt
	rm -rf $(PYTHON_PACKAGING_ENV) && \
	$(PYTHON) -m venv $(PYTHON_PACKAGING_ENV) && \
	. $(PYTHON_PACKAGING_ENV)/bin/activate && \
	pip install --upgrade pip && \
	pip install -r REQUIREMENTS.packaging.txt

# environment helper ##########################################################
clean:
	rm -rf $(PYTHON_ENV_ROOT)

shell: | $(PYTHON_DEV_ENV)
	. $(PYTHON_DEV_ENV)/bin/activate && \
	rlpython

freeze: | $(PYTHON_DEV_ENV)
	. $(PYTHON_DEV_ENV)/bin/activate && \
	pip freeze

# tests #######################################################################
pytest: | $(PYTHON_DEV_ENV)
	. $(PYTHON_DEV_ENV)/bin/activate && \
	rm -rf htmlcov && \
	time tox $(args)

ci-test: | $(PYTHON_DEV_ENV)
	. $(PYTHON_DEV_ENV)/bin/activate && \
	rm -rf htmlcov && \
	time JENKINS_URL=1 tox -r $(args)

test:
	ARGS=$(args) docker-compose -f tests/docker/docker-compose.yml run lona-tox

# linting #####################################################################
lint: | $(PYTHON_DEV_ENV)
	. $(PYTHON_DEV_ENV)/bin/activate && \
	time tox -e lint $(args)

# isort #######################################################################
isort: | $(PYTHON_DEV_ENV)
	. $(PYTHON_DEV_ENV)/bin/activate && \
	tox -e isort $(args)

# packaging ###################################################################
sdist: | $(PYTHON_PACKAGING_ENV)
	. $(PYTHON_PACKAGING_ENV)/bin/activate && \
	rm -rf dist *.egg-info && \
	./setup.py sdist

_release: sdist
	. $(PYTHON_PACKAGING_ENV)/bin/activate && \
	twine upload --config-file ~/.pypirc.fscherf dist/*
