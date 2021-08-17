PYTHON=python3
PYTHON_VENV=env

LONA_SHELL_SERVER_URL=file://socket
LONA_DEFAULT_ARGS=--shell-server-url=$(LONA_SHELL_SERVER_URL)

# environment #################################################################
$(PYTHON_VENV)/.created: REQUIREMENTS.txt
	rm -rf $(PYTHON_VENV) && \
	$(PYTHON) -m venv $(PYTHON_VENV) && \
	. $(PYTHON_VENV)/bin/activate && \
	pip install pip --upgrade && \
	pip install -r ./REQUIREMENTS.txt && \
	date > $(PYTHON_VENV)/.created

env: $(PYTHON_VENV)/.created

clean:
	rm -rf $(PYTHON_VENV)

shell: env
	. $(PYTHON_VENV)/bin/activate && \
	rlpython

server: env
	. $(PYTHON_VENV)/bin/activate && \
	lona run-server $(LONA_DEFAULT_ARGS) $(args) -s settings.py

message-broker: env
	. $(PYTHON_VENV)/bin/activate && \
	lona run-message-broker $(LONA_DEFAULT_ARGS) $(args) -s settings.py

server-shell:
	. $(PYTHON_VENV)/bin/activate && \
	rlpython $(LONA_SHELL_SERVER_URL)
