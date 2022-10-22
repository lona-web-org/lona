PYTHON=python3.9
PYTHON_VENV=env
FLAMINGO_ARGS=-s settings.py

all: html

$(PYTHON_VENV):
	rm -rf $(PYTHON_VENV) && \
	$(PYTHON) -m venv $(PYTHON_VENV) && \
	. $(PYTHON_VENV)/bin/activate && \
	pip install --upgrade pip && \
	pip install -r ./REQUIREMENTS.txt

clean:
	rm -rf output

distclean:
	rm -rf $(PYTHON_VENV)

html: | $(PYTHON_VENV)
	. $(PYTHON_VENV)/bin/activate && \
	flamingo build $(FLAMINGO_ARGS) $(args)

server: | $(PYTHON_VENV)
	. $(PYTHON_VENV)/bin/activate && \
	flamingo server $(FLAMINGO_ARGS) $(args)

shell: | $(PYTHON_VENV)
	. $(PYTHON_VENV)/bin/activate && \
	flamingo shell $(FLAMINGO_ARGS) $(args)

_release: $(PYTHON_VENV)
	rm -rf output/ && \
	. $(PYTHON_VENV)/bin/activate && \
	flamingo build $(FLAMINGO_ARGS) $(args) && \
	rsync -avh --recursive --delete \
		output/* lona-web.org:/var/www/virtual/fscherf/lona-web.org
