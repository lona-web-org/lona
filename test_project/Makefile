PYTHON=python3.11
PYTHON_VENV=env

LONA_SHELL_SERVER_URL=file://../socket
LONA_DEFAULT_ARGS=--shell-server-url=$(LONA_SHELL_SERVER_URL)
CLIENT_VERSION=2

all: server

# environment #################################################################
$(PYTHON_VENV): REQUIREMENTS.txt
	rm -rf $(PYTHON_VENV) && \
	$(PYTHON) -m venv $(PYTHON_VENV) && \
	. $(PYTHON_VENV)/bin/activate && \
	pip install pip --upgrade && \
	pip install -r ./REQUIREMENTS.txt

clean:
	rm -rf $(PYTHON_VENV)

shell: | $(PYTHON_VENV)
	. $(PYTHON_VENV)/bin/activate && \
	rlpython

server: | $(PYTHON_VENV)
	. $(PYTHON_VENV)/bin/activate && \
	lona run-server $(LONA_DEFAULT_ARGS) $(args) -s settings.py \
		--settings-post-overrides CLIENT_VERSION=$(CLIENT_VERSION)

server-shell: | $(PYTHON_VENV)
	. $(PYTHON_VENV)/bin/activate && \
	rlpython $(LONA_SHELL_SERVER_URL)
