PYTHON=PYTHONPATH='$(shell pwd)' python3.5

.PHONY: all

all: site validate normalize

validate:
	$(PYTHON) scripts/validate_dictionary.py

normalize:
	$(PYTHON) scripts/normalize_dictionary.py

site: 
	$(PYTHON) server/generate_site.py docs https://iemldev.github.io/ieml-dictionary/

site-debug: 
	$(PYTHON) server/generate_site.py docs-debug http://localhost:8000/

serve: site-debug
	cd docs-debug && $(PYTHON) -m http.server 8000
