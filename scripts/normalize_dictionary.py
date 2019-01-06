import os
from typing import List, Dict

import yaml
import re

from ieml.constants import DICTIONARY_FOLDER
from ieml.dictionary import Dictionary
from ieml.dictionary.dictionary import get_dictionary_files
from ieml.dictionary.script import Script


ScriptDescription = Dict[str, str]


def _clean(s):
    s = re.sub('\n+', "", s)
    return s.strip()


def _serialize_root_paradigm(root: ScriptDescription,
                            root_inhibitions: List[str],
                            semes: List[ScriptDescription],
                            paradigms: List[ScriptDescription]) -> str:
    res = """RootParadigm:
    ieml: "{}"
    translations:
        fr: >
            {}
        en: >
            {}
    inhibitions: {}""".format(root['ieml'],
           _clean(root['translations']['fr']),
           _clean(root['translations']['en']),
           str(sorted(root_inhibitions)))

    # Semes
    res += "\nSemes:"
    for seme in semes:
        res += """
    -   ieml: "{}"
        translations:
            fr: >
                {}
            en: >
                {}""".format(seme['ieml'],
                             _clean(seme['translations']['fr']),
                             _clean(seme['translations']['en']))

    # Paradigms
    res += "\nParadigms:"
    for paradigm in paradigms:
       res += """
    -   ieml: "{}"
        translations:
            fr: >
                {}
            en: >
                {}""".format(paradigm['ieml'],
                             _clean(paradigm['translations']['fr']),
                             _clean(paradigm['translations']['en']))

    return res


def normalize_dictionary_file(file):
    with open(file) as fp:
        d = yaml.load(fp)

    r = _serialize_root_paradigm(d['RootParadigm'],
                                 d['RootParadigm']['inhibitions'],
                                 d['Semes'],
                                 d['Paradigms'] if d['Paradigms'] else [])

    return r


def normalize_dictionary_folder(folder=DICTIONARY_FOLDER):
    for f in get_dictionary_files(folder=folder):
        r = normalize_dictionary_file(f)
        with open(f, 'w') as fp:
            fp.write(r)


def get_script_description(dictionary: Dictionary, script: Script) -> ScriptDescription:
    return {
        'ieml': str(script),
        'translations': {
            'fr': dictionary.translations[script].fr,
            'en': dictionary.translations[script].en,
        }
    }


def serialize_root_paradigm(dictionary: Dictionary, root: Script):
    paradigms = [e for e in dictionary.relations.object(root, 'contains') if len(e) != 1 and e != root]

    r = _serialize_root_paradigm(get_script_description(dictionary, root),
                                 dictionary._inhibitions[root],
                                 [get_script_description(dictionary, sc) for sc in root.singular_sequences],
                                 [get_script_description(dictionary, sc) for sc in paradigms])

    return r


def serialize_dictionary(dictionary: Dictionary):
    os.makedirs('dictionary')

    for root in dictionary.tables.roots:
        r = serialize_root_paradigm(dictionary, root)

        file_out = 'dictionary/{}_{}.yaml'.format(root.layer, re.sub('[^a-zA-Z0-9\-]+',
                                                                     '_',
                                                                     dictionary.translations[root].en))

        with open(file_out, 'w') as fp:
            fp.write(r)


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Normalize the dictionary files')

    parser.add_argument('--dictionary-folder', type=str, required=False, default=DICTIONARY_FOLDER,
                        help='the dictionary definition folder')
    args = parser.parse_args()

    normalize_dictionary_folder(args.dictionary_folder)