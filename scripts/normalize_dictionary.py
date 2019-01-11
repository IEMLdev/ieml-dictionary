import os
from typing import List, Dict

import yaml
import re

from ieml.constants import DICTIONARY_FOLDER
from ieml.dictionary import Dictionary
from ieml.dictionary.dictionary import get_dictionary_files
from ieml.dictionary.script import Script, script
from ieml.dictionary.table.table import table_class, TableSet

ScriptDescription = Dict[str, str]


PAD = '    '


def _clean(s, indent=3):
    indentation = PAD * indent
    s = re.sub('\n\s*', '\n' + indentation, s.strip())
    return s


def _comments(s, indent=1):
    res = ''
    if 'comments' in s and (('fr' in s['comments'] and s['comments']['fr']) or
                            ('en' in s['comments'] and s['comments']['en'])):
        res += PAD * indent + 'comments:\n'

        if 'fr' in s['comments'] and s['comments']['fr']:
            res += PAD * (indent + 1) + 'fr: |-\n'
            res += PAD * (indent + 2) + _clean(s['comments']['fr'], indent=(indent + 2)) + '\n'
        if 'en' in s['comments'] and s['comments']['en']:
            res += PAD * (indent + 1) + 'en: |-\n'
            res += PAD * (indent + 2) + _clean(s['comments']['en'], indent=(indent + 2)) + '\n'

    return res


def _serialize_root_paradigm(root: ScriptDescription,
                             root_inhibitions: List[str],
                             semes: List[ScriptDescription],
                             paradigms: List[ScriptDescription]) -> str:
    res = """RootParadigm:
    ieml: "{}"
    translations:
        fr: |-
            {}
        en: |-
            {}
    inhibitions: {}
""".format(root['ieml'],
           _clean(root['translations']['fr']),
           _clean(root['translations']['en']),
           str(sorted(root_inhibitions)))
    res += _comments(root, indent=1)

    # Semes
    if semes:
        res += "Semes:\n"
    for seme in semes:
        res += """    -   ieml: "{}"
        translations:
            fr: |-
                {}
            en: |-
                {}
""".format(seme['ieml'],
           _clean(seme['translations']['fr']),
           _clean(seme['translations']['en']))
        res += _comments(seme, indent=2)

    # Paradigms
    if paradigms:
        res += "Paradigms:\n"
    for paradigm in paradigms:
        res += """    -   ieml: "{}"
        translations:
            fr: |-
                {}
            en: |-
                {}
""".format(paradigm['ieml'],
           _clean(paradigm['translations']['fr']),
           _clean(paradigm['translations']['en']))
        res += _comments(paradigm, indent=2)

    return res


def normalize_dictionary_file(file, expand_root=False):
    with open(file) as fp:
        d = yaml.load(fp)

    d['Semes'] = d['Semes'] if 'Semes' in d and d['Semes'] else []
    d['Paradigms'] = d['Paradigms'] if 'Paradigms' in d and d['Paradigms'] else []
    d['RootParadigm']['inhibitions'] = d['RootParadigm']['inhibitions'] \
        if 'inhibitions' in d['RootParadigm'] and d['RootParadigm']['inhibitions'] else []

    script_root = script(d['RootParadigm']['ieml'])
    semes_root = {str(ss): ss for ss in script_root.singular_sequences}
    semes_file = {ss['ieml']: ss for ss in d['Semes']}
    paradigms_file = {p['ieml']: p for p in d['Paradigms']}

    if expand_root:
        # remove extra semes
        to_remove = set()
        for ss in d['Semes']:
            if ss['ieml'] not in semes_root:
                to_remove.add(ss['ieml'])

        d['Semes'] = [ss for ss in d['Semes'] if ss['ieml'] not in to_remove]

        # add missing semes
        for ss in set(semes_root) - set(semes_file):
            d['Semes'].append({'ieml': ss, 'translations': {'fr': "", 'en': ""}})

        # add table set paradigms
        table_root = table_class(script_root)(script_root, None)
        if isinstance(table_root, TableSet):
            paradigms = {str(t): t for t in table_root.tables}

            # add missing tables
            for ss in set(paradigms) - set(paradigms_file):
                d['Paradigms'].append({'ieml': ss, 'translations': {'fr': "", 'en': ""}})

    d['Semes'] = sorted(d['Semes'], key=lambda ss: semes_root[ss['ieml']])
    d['Paradigms'] = sorted(d['Paradigms'], key=lambda ss: script(ss['ieml']))

    r = _serialize_root_paradigm(d['RootParadigm'],
                                 d['RootParadigm']['inhibitions'],
                                 d['Semes'],
                                 d['Paradigms'])

    return r


def normalize_dictionary_folder(folder=DICTIONARY_FOLDER, expand_root=False):
    for f in get_dictionary_files(folder=folder):
        r = normalize_dictionary_file(f, expand_root=expand_root)

        with open(f) as fp:
            r_old = fp.read()
            if r_old == r:
                continue

        print("Normalizing {}".format(f))

        with open(f, 'w') as fp:
            fp.write(r)


def get_script_description(dictionary: Dictionary, script: Script) -> ScriptDescription:
    return {
        'ieml': str(script),
        'translations': {
            'fr': dictionary.translations[script].fr,
            'en': dictionary.translations[script].en,
        },
        'comments': {
            'fr': dictionary.comments[script].fr,
            'en': dictionary.comments[script].en,
        }
    }


def serialize_root_paradigm(dictionary: Dictionary, root: Script):
    paradigms = [e for e in dictionary.relations.object(root, 'contains') if len(e) != 1 and e != root]

    r = _serialize_root_paradigm(get_script_description(dictionary, root),
                                 dictionary._inhibitions[root],
                                 [get_script_description(dictionary, sc) for sc in root.singular_sequences],
                                 [get_script_description(dictionary, sc) for sc in paradigms])

    return r


def serialize_dictionary(dictionary: Dictionary, output_path: str):
    os.makedirs(output_path, exist_ok=True)

    for root in dictionary.tables.roots:
        r = serialize_root_paradigm(dictionary, root)

        file_out = '{}_{}.yaml'.format(root.layer,
                                       re.sub('[^a-zA-Z0-9\-]+', '_', dictionary.translations[root].en))

        with open(os.path.join(output_path, file_out), 'w') as fp:
            fp.write(r)


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Normalize the dictionary files')

    parser.add_argument('--dictionary-folder', type=str, required=False, default=DICTIONARY_FOLDER,
                        help='the dictionary definition folder')

    parser.add_argument('--expand-root', action='store_true',
                        help='Write the semes for roots paradigms if missing.')

    args = parser.parse_args()
    # path=os.path.join(os.path.dirname(__file__), 'dictionary')
    normalize_dictionary_folder(args.dictionary_folder, expand_root=args.expand_root)
    # d = Dictionary.load(path)