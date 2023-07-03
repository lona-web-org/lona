SHELL=/bin/bash
PYTHON=python3.10
PYTHON_ENV=env

.PHONY: clean doc dist test ci-test lint isort shell freeze

# python env ##################################################################
$(PYTHON_ENV): pyproject.toml
	rm -rf $(PYTHON_ENV) && \
	$(PYTHON) -m venv $(PYTHON_ENV) && \
	. $(PYTHON_ENV)/bin/activate && \
	pip install pip --upgrade && \
	pip install -e .[dev,packaging]

clean:
	rm -rf $(PYTHON_ENV)

shell: | $(PYTHON_ENV)
	. $(PYTHON_ENV)/bin/activate && \
	rlpython

freeze: | $(PYTHON_ENV)
	. $(PYTHON_ENV)/bin/activate && \
	pip freeze

# tests #######################################################################
test:
	docker-compose run playwright tox $(args)

ci-test:
	docker-compose run playwright tox -e lint,py38,py39,py310,py311 $(args)

lint:
	docker-compose run playwright tox -e lint $(args)

isort:
	docker-compose run playwright tox -e isort $(args)

# packaging ###################################################################
dist: | $(PYTHON_ENV)
	. $(PYTHON_ENV)/bin/activate && \
	rm -rf dist *.egg-info && \
	$(PYTHON) -m build

_release: dist
	. $(PYTHON_ENV)/bin/activate && \
	twine upload --config-file ~/.pypirc.fscherf dist/*
