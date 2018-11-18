run:
	FLASK_APP=server.py flask run

extract:
	python extract_dictionary.py dictionary_2018-09-03_20:39:39

check:
	find dictionary/* | xargs -I % -t pykwalify -s dictionary_paradigm_schema.yaml -d %
