SHELL=/bin/bash
PYTHON=python3.11
PYTHON_ENV=env

.PHONY: clean doc dist build test ci-test lint isort shell freeze

define DOCKER_COMPOSE_RUN
	docker compose run \
		-it \
		--remove-orphans \
		$1 $2
endef


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
build:
	docker-compose build $(args)

test:
	$(call DOCKER_COMPOSE_RUN, playwright, tox ${args})

ci-test:
	$(call DOCKER_COMPOSE_RUN, playwright, tox -e lint,py38,py39,py310,py311 ${args})

lint:
	$(call DOCKER_COMPOSE_RUN, playwright, tox -e lint ${args})

isort:
	$(call DOCKER_COMPOSE_RUN, playwright, tox -e isort ${args})

# packaging ###################################################################
dist: | $(PYTHON_ENV)
	. $(PYTHON_ENV)/bin/activate && \
	rm -rf dist *.egg-info && \
	$(PYTHON) -m build

_release: dist
	. $(PYTHON_ENV)/bin/activate && \
	twine upload --config-file ~/.pypirc.fscherf dist/*
