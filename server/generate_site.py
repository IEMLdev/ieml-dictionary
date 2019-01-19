from typing import List

from jinja2 import Environment, FileSystemLoader, UndefinedError
from functools import lru_cache
import re
from ieml.constants import DICTIONARY_FOLDER, LEXICONS_FOLDER
from ieml.dictionary import Dictionary
from ieml.dictionary.script import Script
from ieml.dictionary.table.table import TableSet, Table1D, Table2D, Cell
import os
from tqdm import tqdm
import sys
import markdown

from ieml.lexicon.grammar import Word, word
from ieml.lexicon.lexicon import Lexicon

RELATIONS_CATEGORIES = {
    'inclusion': ['contains', 'contained'],
    'etymology': ['father', 'child'],
    'sibling': ['twin', 'associated', 'crossed', 'opposed']
}

SAM = ["substance", "attribute", "mode"]
I_TO_CLASS_DISPLAY = ['Auxiliary', 'Verb', 'Noun']
I_TO_CLASS = ['aux', 'verb', 'noun']
CLASS_TO_COLOR = ['#fff1bc', '#ffe5d7', '#d9eaff']
CLASS_TO_COLOR_HEADER = ['#fff38e', '#ffd8c0', '#94ceff']
CHARACTERS_NAME = ['substance', 'attribute', 'mode']


@lru_cache(maxsize=10000)
def _get_script_properties(dictionary, r):
    t = dictionary.tables[r]

    def _cell(s):
        if s in dictionary:
            translations = {l: dictionary.translations[s][l] for l in ['fr', 'en']}
        else:
            translations = {}

        return {
            'ieml': str(s),
            'translations': translations,
            'color': CLASS_TO_COLOR[s.script_class] if len(s) == 1 else CLASS_TO_COLOR_HEADER[s.script_class]
        }

    if isinstance(t, Cell):
        cells, columns, rows = [], [], []
    elif isinstance(t, Table1D):
        cells, columns, rows = [_cell(s) for s in t.cells], [_cell(t.script)], []
    elif isinstance(t, Table2D):
        cells, columns, rows = [[_cell(s) for s in r] for r in t.cells], [_cell(c) for c in t.columns], [_cell(r) for r in t.rows]
    elif isinstance(t, TableSet):
        cells, columns, rows = {str(tt): _get_script_properties(dictionary, tt) for tt in t.tables}, [], []

    relations = {
        'sibling': {
            reltype: [_cell(tt) for tt in dictionary.relations.object(r, reltype) if tt != r] for reltype in RELATIONS_CATEGORIES['sibling']
        },
        'inclusion': {
            reltype: [_cell(tt) for tt in dictionary.relations.object(r, reltype) if tt != r and len(tt) != 1] for reltype in RELATIONS_CATEGORIES['inclusion']
        },
        'father': {
            key: [_cell(tt) for tt in dictionary.relations.object(r, 'father_' + key) if tt != r] for key in SAM
        },
        'child': {
            key: [_cell(tt) for tt in dictionary.relations.object(r, 'child_' + key) if tt != r and len(tt) != 1] for key in SAM
        }
    }
    for rel, rel_v in relations.items():
        to_remove_cat = []
        for cat, cat_v in rel_v.items():
            if not cat_v:
                to_remove_cat.append(cat)
        for cat in to_remove_cat:
            del rel_v[cat]

    # relations['inclusion']['table_2_4'] = [_cell(tt) for tt in t.root.relations.contained if tt.rank in [2,4]]

    return {
            # 'ieml': str(r),
            'type': t.__class__.__name__,
            'type_pretty': 'Seme' if len(r) == 1 else ('RootParadigm' if r in dictionary.tables.roots else 'Paradigm'),

            'class': I_TO_CLASS[r.script_class],
            'class_pretty': I_TO_CLASS_DISPLAY[r.script_class],
            'layer': r.layer,
            'size': len(r),
            # 'translations': {l: dictionary.translations[r][l] for l in ['fr', 'en']},
            'comments': {l: markdown.markdown(dictionary.comments[r][l]) for l in ['fr', 'en']},
            # 'color': CLASS_TO_COLOR[r.script_class],
            'tables': {
                'rank': t.rank,
                'parent': str(t.parent.script) if t.parent else 'Root',
                'dim': t.ndim,
                'shape': t.shape if not isinstance(t, TableSet) else [dictionary.tables[t].shape for t in t.tables],
                'cells': cells,
                'rows': rows,
                'columns': columns,
                'root': str(dictionary.tables.table_to_root[t]),
                'header': _cell(r)
            },
            'relations': relations,
            **_cell(r)
    }


def _get_character_properties(dictionary, char: List[Script], i):
    return {
        'ieml': str(word(char)),
        'name': CHARACTERS_NAME[i],
        'semes': [_get_script_properties(dictionary, s) for s in char]
    }


def _get_word_properties(dictionary: Dictionary, lexicon: Lexicon, word: Word):
    return {'ieml': str(word),
            'type': word.__class__.__name__,
            'type_pretty': 'Word',
            'class': I_TO_CLASS[word.grammatical_class],
            'class_pretty': I_TO_CLASS_DISPLAY[word.grammatical_class],
            'layer': len(word.semes),
            'multiplicty': word.cardinal,
            'composition': [_get_character_properties(dictionary, char, i) for i, char in enumerate(word)],
            'morpheme_serie': {
                'dim': sum(len(s) != 1 for s in word.semes),
                'shape': [tuple(len(s) for s in char if len(s) != 1) for char in word],
                'parents': [],
                'roots': []
            },
            'translations': {
                'fr': lexicon.translations[word]['fr'],
                'en': lexicon.translations[word]['en'],
            }}

def _script_to_filename(s):
    return "{}.html".format(re.sub(r'[,:;]', '_', str(s)))


def _usl_to_filename(u):
    return "{}.html".format(re.sub(r"[^a-zA-Z.\-*+)(\]\[]", '_', str(u)))


def generate_script_site(dictionary, lexicon, output_folder, base_url):
    from shutil import copytree, rmtree

    if os.path.isdir(output_folder):
        rmtree(output_folder)
    os.makedirs(output_folder)

    static_folder = os.path.join(output_folder, 'static')
    local_folder = os.path.dirname(__file__)

    copytree(os.path.join(local_folder, 'static'), static_folder)

    all_scripts = [{
        'ieml': str(s),
        'fr': dictionary.translations[s].fr,
        'en': dictionary.translations[s].en,
        'layer': s.layer,
        'type': 'seme' if len(s) == 1 else ('root' if s in dictionary.tables.roots else 'paradigm'),
        'type_pretty': 'Seme' if len(s) == 1 else ('RootParadigm' if s in dictionary.tables.roots else 'Paradigm'),
        'class': I_TO_CLASS[s.script_class],
        'class_pretty': I_TO_CLASS_DISPLAY[s.script_class],
    } for s in dictionary.scripts]

    dictionary_stats = {
        'nb_roots': len(dictionary.tables.roots),
        'nb_semes': len([s for s in dictionary.scripts if len(s) == 1]),
        'nb_paradigms': len([s for s in dictionary.scripts if len(s) != 1]),
        'nb_relations': len(dictionary.relations.pandas())
    }


    def url_for(folder, filename):
        if folder == 'scripts':
            e = _script_to_filename(filename)
        else:
            e = os.path.join(folder, filename)

        return e

    env = Environment(loader=FileSystemLoader(os.path.join(local_folder, 'templates')))
    env.globals['url_for'] = url_for

    template = env.get_template('index.html')

    with open(os.path.join(output_folder, 'index.html'), 'w') as fp:
        print(template.render(scripts=all_scripts,
                              dictionary_stats=dictionary_stats,
                              base_url=base_url), file=fp)

    # template = env.get_template('script.html')
    #
    # for script in tqdm(dictionary.scripts, "Generating site at {}".format(output_folder)):
    #     try:
    #         rendered = template.render(script=get_table(dictionary, script),
    #                                    all_scripts=all_scripts,
    #                                    dictionary_stats=dictionary_stats,
    #                                    base_url=base_url)
    #     except UndefinedError as e:
    #         print(e.__repr__(), file=sys.stderr)
    #         print("Unable to generate templates for script: {}, no HTML generated.".format(str(script)), file=sys.stderr)
    #         continue
    #
    #     with open(os.path.join(output_folder, _script_to_filename(script)), 'w') as fp:
    #         print(rendered, file=fp)

    template = env.get_template('word.html')

    for word in tqdm(lexicon.usls, "Generating usls"):
        try:
            rendered = template.render(word=_get_word_properties(dictionary, lexicon, word),
                                       # all_scripts=all_scripts,
                                       dictionary_stats=dictionary_stats,
                                       base_url=base_url)
        except UndefinedError as e:
            print(e.__repr__(), file=sys.stderr)
            print("[error] Unable to generate templates for word: {}, no HTML generated.".format(str(word)),
                  file=sys.stderr)
            continue

        with open(os.path.join(output_folder, _usl_to_filename(word)), 'w') as fp:
            print(rendered, file=fp)



if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Generate the dictionary static website.')

    parser.add_argument('output_folder', type=str, help='the website output folder')
    parser.add_argument('base_url', type=str, help='the website base url')

    parser.add_argument('--dictionary-folder', type=str, required=False, default=DICTIONARY_FOLDER,
                        help='the dictionary definition folder')

    parser.add_argument('--lexicon-folder', type=str, required=False, default=LEXICONS_FOLDER,
                        help='the lexicons definition folder')


    args = parser.parse_args()

    dictionary = Dictionary.load(args.dictionary_folder)
    lexicon = Lexicon.load(args.lexicon_folder)

    generate_script_site(dictionary, lexicon, args.output_folder, base_url=args.base_url)