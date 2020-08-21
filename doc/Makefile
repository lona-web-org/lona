PYTHON=python3
PYTHON_VENV=env
FLAMINGO_ARGS=-s settings.py

$(PYTHON_VENV)/.created: REQUIREMENTS.txt
	rm -rf $(PYTHON_VENV) && \
	$(PYTHON) -m venv $(PYTHON_VENV) && \
	. $(PYTHON_VENV)/bin/activate && \
	pip install --upgrade pip && \
	pip install -r ./REQUIREMENTS.txt && \
	date > $(PYTHON_VENV)/.created

env: $(PYTHON_VENV)/.created

clean:
	rm -rf $(PYTHON_VENV) output

html: env
	. $(PYTHON_VENV)/bin/activate && \
	flamingo build $(FLAMINGO_ARGS) $(args)

server: env
	. $(PYTHON_VENV)/bin/activate && \
	flamingo server $(FLAMINGO_ARGS) $(args)

shell: env
	. $(PYTHON_VENV)/bin/activate && \
	flamingo shell $(FLAMINGO_ARGS) $(args)

rollout: env
	. $(PYTHON_VENV)/bin/activate && \
	flamingo build $(FLAMINGO_ARGS) rollout_settings.py
