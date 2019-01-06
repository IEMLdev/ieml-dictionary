PYTHON=PYTHONPATH='$(shell pwd)' venv/bin/python

.PHONY: all

all: site validate normalize

venv:
	virtualenv -ppython3.6 venv
	$(PYTHON) -m pip install -r requirements.txt

validate: venv
	$(PYTHON) scripts/validate_dictionary.py

normalize: venv
	$(PYTHON) scripts/normalize_dictionary.py

site: venv
	$(PYTHON) server/generate_site.py docs https://iemldev.github.io/ieml-dictionary/

site-debug: venv
	$(PYTHON) server/generate_site.py docs-debug http://localhost:8000/

serve: site-debug
	cd docs-debug && $(PYTHON) -m http.server 8000
