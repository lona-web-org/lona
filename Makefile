SHELL=/bin/bash
PYTHON=python3

PYTHON_ENV_ROOT=envs
PYTHON_DEV_ENV=$(PYTHON_ENV_ROOT)/$(PYTHON)-dev

.PHONY: clean doc

# development environment #####################################################
$(PYTHON_DEV_ENV)/.created: REQUIREMENTS.dev.txt
	rm -rf $(PYTHON_DEV_ENV) && \
	$(PYTHON) -m venv $(PYTHON_DEV_ENV) && \
	. $(PYTHON_DEV_ENV)/bin/activate && \
	pip install pip --upgrade && \
	pip install -r ./REQUIREMENTS.dev.txt && \
	date > $(PYTHON_DEV_ENV)/.created

dev-env: $(PYTHON_DEV_ENV)/.created

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
test: dev-env
	. $(PYTHON_DEV_ENV)/bin/activate && \
	time tox $(args)

ci-test: dev-env
	. $(PYTHON_DEV_ENV)/bin/activate && \
	time JENKINS_URL=1 tox -r $(args)

# packaging ###################################################################
sdist:
	rm -rf dist *.egg-info && \
	./setup.py sdist
