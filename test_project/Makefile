PYTHON=python3
PYTHON_VENV=env


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
	ipython

server: env
	. $(PYTHON_VENV)/bin/activate && \
	lona -s settings.py --project-root=./ $(args)

debug-server: env
	. $(PYTHON_VENV)/bin/activate && \
	lona \
		--project-root=./ \
		-s settings.py -s debug_settings.py \
		--log-level=debug \
		$(args)
