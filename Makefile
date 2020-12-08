SHELL=/bin/bash
PYTHON=python3
PYTHON_VENV=env

.PHONY: clean doc

# development environment #####################################################
$(PYTHON_VENV)/.created: REQUIREMENTS.dev.txt
	rm -rf $(PYTHON_VENV) && \
	$(PYTHON) -m venv $(PYTHON_VENV) && \
	. $(PYTHON_VENV)/bin/activate && \
	pip install pip --upgrade && \
	pip install -r ./REQUIREMENTS.dev.txt && \
	date > $(PYTHON_VENV)/.created

env: $(PYTHON_VENV)/.created

clean:
	rm -rf $(PYTHON_VENV)

shell: env
	. $(PYTHON_VENV)/bin/activate && \
	ipython

freeze: env
	. $(PYTHON_VENV)/bin/activate && \
	pip freeze

# tests #######################################################################
test: env
	. $(PYTHON_VENV)/bin/activate && \
	time tox $(args)

ci-test: env
	. $(PYTHON_VENV)/bin/activate && \
	time JENKINS_URL=1 tox -r $(args)

# test project ################################################################
server:
	cd test_project/ && \
	make server args="$(args)"

debug-server:
	cd test_project/ && \
	make debug-server args="$(args)"

# documentation ###############################################################
doc:
	cd doc && \
	make server args=$(args)

doc-rollout:
	cd doc && \
	make rollout

# packaging ###################################################################
sdist:
	rm -rf dist *.egg-info && \
	./setup.py sdist
