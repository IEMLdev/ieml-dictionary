PYTHON=PYTHONPATH='$(shell pwd)' "$(shell pwd)/venv/bin/python"
DICTIONARY_FOLDER=definition/dictionary

.PHONY: all

all: site validate normalize

venv:
	virtualenv -ppython3.6 venv
	$(PYTHON) -m pip install -r requirements.txt

validate: venv
	$(PYTHON) scripts/validate_dictionary.py --dictionary-folder $(DICTIONARY_FOLDER)

normalize: venv
	$(PYTHON) scripts/normalize_dictionary.py --dictionary-folder $(DICTIONARY_FOLDER)

expand_semes: venv
	$(PYTHON) scripts/normalize_dictionary.py --dictionary-folder $(DICTIONARY_FOLDER) --expand-root

site: venv
	$(PYTHON) server/generate_site.py docs https://iemldev.github.io/ieml-dictionary/ --dictionary-folder $(DICTIONARY_FOLDER)

site-debug: venv
	$(PYTHON) server/generate_site.py docs-debug http://localhost:8000/ --dictionary-folder $(DICTIONARY_FOLDER)

serve: site-debug
	cd docs-debug && $(PYTHON) -m http.server 8000
