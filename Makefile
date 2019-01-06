PYTHON=PYTHONPATH='$(shell pwd)' python3.5

.PHONY: all

all: site validate normalize

validate:
	$(PYTHON) scripts/validate_dictionary.py

normalize:
	$(PYTHON) scripts/normalize_dictionary.py

site: 
	$(PYTHON) server/generate_site.py docs

serve: site
	cd docs && $(PYTHON) -m http.server
