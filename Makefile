SHELL=/bin/bash
PYTHON=python3

PYTHON_ENV_ROOT=envs
PYTHON_DEV_ENV=$(PYTHON_ENV_ROOT)/$(PYTHON)-dev
PYTHON_PACKAGING_ENV=$(PYTHON_ENV_ROOT)/$(PYTHON)-packaging-env

.PHONY: clean doc sdist pytest test ci-test lint isort shell freeze

# development environment #####################################################
$(PYTHON_DEV_ENV)/.created: REQUIREMENTS.dev.txt
	rm -rf $(PYTHON_DEV_ENV) && \
	$(PYTHON) -m venv $(PYTHON_DEV_ENV) && \
	. $(PYTHON_DEV_ENV)/bin/activate && \
	pip install pip --upgrade && \
	pip install -r ./REQUIREMENTS.dev.txt && \
	date > $(PYTHON_DEV_ENV)/.created

dev-env: $(PYTHON_DEV_ENV)/.created

# packaging environment #######################################################
$(PYTHON_PACKAGING_ENV)/.created: REQUIREMENTS.packaging.txt
	rm -rf $(PYTHON_PACKAGING_ENV) && \
	$(PYTHON) -m venv $(PYTHON_PACKAGING_ENV) && \
	. $(PYTHON_PACKAGING_ENV)/bin/activate && \
	pip install --upgrade pip && \
	pip install -r REQUIREMENTS.packaging.txt
	date > $(PYTHON_PACKAGING_ENV)/.created

packaging-env: $(PYTHON_PACKAGING_ENV)/.created

# environment helper ##########################################################
clean:
	rm -rf $(PYTHON_ENV_ROOT)

shell: dev-env
	. $(PYTHON_DEV_ENV)/bin/activate && \
	rlpython

freeze: dev-env
	. $(PYTHON_DEV_ENV)/bin/activate && \
	pip freeze

# tests #######################################################################
pytest: dev-env
	. $(PYTHON_DEV_ENV)/bin/activate && \
	rm -rf htmlcov && \
	time tox $(args)

ci-test: dev-env
	. $(PYTHON_DEV_ENV)/bin/activate && \
	rm -rf htmlcov && \
	time JENKINS_URL=1 tox -r $(args)

test:
	ARGS=$(args) docker-compose -f tests/docker/docker-compose.yml run lona-tox

# linting #####################################################################
lint: dev-env
	. $(PYTHON_DEV_ENV)/bin/activate && \
	time tox -e lint

# isort #######################################################################
isort: dev-env
	. $(PYTHON_DEV_ENV)/bin/activate && \
	tox -e isort

# packaging ###################################################################
sdist: packaging-env
	. $(PYTHON_PACKAGING_ENV)/bin/activate && \
	rm -rf dist *.egg-info && \
	./setup.py sdist

_release: sdist
	. $(PYTHON_PACKAGING_ENV)/bin/activate && \
	twine upload --config-file ~/.pypirc.fscherf dist/*
