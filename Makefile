SHELL=/bin/bash
PYTHON=python3

PYTHON_ENV_ROOT=envs
PYTHON_DEV_ENV=$(PYTHON_ENV_ROOT)/$(PYTHON)-dev
PYTHON_PACKAGING_ENV=$(PYTHON_ENV_ROOT)/$(PYTHON)-packaging-env

.PHONY: clean doc dist test ci-test lint isort shell freeze

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
	pip install .[packaging]

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
test:
	./docker-compose run playwright tox $(args)

ci-test:
	./docker-compose run playwright tox -e lint,py37,py38,py39,py310,py311 $(args)

lint:
	./docker-compose run playwright tox -e lint $(args)

isort:
	./docker-compose run playwright tox -e isort $(args)

# packaging ###################################################################
dist: | $(PYTHON_PACKAGING_ENV)
	. $(PYTHON_PACKAGING_ENV)/bin/activate && \
	rm -rf dist *.egg-info && \
	python -m build

_release: dist
	. $(PYTHON_PACKAGING_ENV)/bin/activate && \
	twine upload --config-file ~/.pypirc.fscherf dist/*
