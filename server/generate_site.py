import hashlib
import traceback
from itertools import chain
from typing import List

from jinja2 import Environment, FileSystemLoader, UndefinedError
from functools import lru_cache, singledispatch
import re
from ieml.constants import DICTIONARY_FOLDER, LEXICONS_FOLDER, LANGUAGES
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


def get_script_description_metadata(s: Script, dictionary: Dictionary):
    if s in dictionary:
        translations = {l: dictionary.translations[s][l] for l in ['fr', 'en']}
    else:
        translations = {'fr': '', 'en': ''}

    res = {
        'folder': 'scripts',

        'ieml': str(s),
        **translations,
        'translations': translations,
        'color': CLASS_TO_COLOR[s.script_class] if len(s) == 1 else CLASS_TO_COLOR_HEADER[s.script_class],
        'layer': s.layer,
        'type': s.__class__.__name__,
        'type_pretty': 'Seme' if len(s) == 1 else ('RootParadigm' if s in dictionary.tables.roots else 'Paradigm'),
        'class': I_TO_CLASS[s.script_class],
        'class_pretty': I_TO_CLASS_DISPLAY[s.script_class],
    }

    return res

@lru_cache(maxsize=10000)
def get_script_description(s: Script, dictionary: Dictionary, lexicon: Lexicon):
    _cell = lambda s: get_script_description_metadata(s, dictionary)

    if s not in dictionary:
        return _cell(s)


    t = dictionary.tables[s]
    if isinstance(t, Cell):
        cells, columns, rows = [], [], []
    elif isinstance(t, Table1D):
        cells, columns, rows = [_cell(s) for s in t.cells], [_cell(t.script)], []
    elif isinstance(t, Table2D):
        cells, columns, rows = [[_cell(s) for s in r] for r in t.cells], [_cell(c) for c in t.columns], [_cell(r) for r in t.rows]
    elif isinstance(t, TableSet):
        cells, columns, rows = {str(tt): get_script_description(tt, dictionary, lexicon) for tt in t.tables}, [], []

    relations = {
        'sibling': {
            reltype: [_cell(tt) for tt in dictionary.relations.object(s, reltype) if tt != s] for reltype in RELATIONS_CATEGORIES['sibling']
        },
        'inclusion': {
            reltype: [_cell(tt) for tt in dictionary.relations.object(s, reltype) if tt != s and len(tt) != 1] for reltype in RELATIONS_CATEGORIES['inclusion']
        },
        'father': {
            key: [_cell(tt) for tt in dictionary.relations.object(s, 'father_' + key) if tt != s] for key in SAM
        },
        'child': {
            key: [_cell(tt) for tt in dictionary.relations.object(s, 'child_' + key) if tt != s and len(tt) != 1] for key in SAM
        }
    }

    for rel, rel_v in relations.items():
        to_remove_cat = []
        for cat, cat_v in rel_v.items():
            if not cat_v:
                to_remove_cat.append(cat)
        for cat in to_remove_cat:
            del rel_v[cat]

    words_metadatas = {w: get_word_description_metadata(w, lexicon) for w in lexicon.words if s in w.semes}
    names = {name: sorted(filter(lambda w: lexicon.metadatas[w]['name'] == name, words_metadatas)) for name in lexicon.names}

    words = [
            {
                'name': name,

                'words': [get_word_description_metadata(w, lexicon) for w in names[name]] ,
                'singulars': [words_metadatas[w] for w in names[name] if w.cardinal == 1],
                'paradigms': [words_metadatas[w] for w in names[name] if w.cardinal != 1],
            } for name in lexicon.names if len(names[name])
        ]

    res = {**_cell(s),
            'size': len(s),
            'comments': {l: markdown.markdown(dictionary.comments[s][l]) for l in ['fr', 'en']},

            'words': words,

            # 'composition': [
            #         {
            #             'ieml': str(word(char)),
            #             'name': CHARACTERS_NAME[i],
            #             'semes': [get_script_description(s, dictionary, lexicon) for s in char]
            #         } for i, char in enumerate(w)],

            'tables': {
                'rank': t.rank,
                'parent': str(t.parent.script) if t.parent else 'Root',
                'dim': t.ndim,
                'shape': t.shape if not isinstance(t, TableSet) else [dictionary.tables[t].shape for t in t.tables],
                'cells': cells,
                'rows': rows,
                'columns': columns,
                'root': str(dictionary.tables.table_to_root[t]),
                'header': _cell(s)
            },
            'relations': relations,
    }

    return res

#
# def _get_script_properties(dictionary, r):
#     if r not in dictionary.scripts:
#         return {
#             'type_pretty': 'Seme' if len(r) == 1 else 'RootParadigm',
#
#             'class': I_TO_CLASS[r.script_class],
#             'class_pretty': I_TO_CLASS_DISPLAY[r.script_class],
#             'layer': r.layer,
#             'size': len(r),
#             'ieml': str(r),
#             'color': CLASS_TO_COLOR[r.script_class] if len(r) == 1 else CLASS_TO_COLOR_HEADER[r.script_class],
#
#             'translations': {'fr': '', 'en': ''}
#         }
#     # t = dictionary.tables[r]
#     #
#     # def _cell(s):
#     #
#     #         translations = {l: dictionary.translations[s][l] for l in ['fr', 'en']}
#     #     else:
#     #         translations = {}
#     #
#     #     return {
#     #         'ieml': str(s),
#     #         'translations': translations,
#     #         'color': CLASS_TO_COLOR[s.script_class] if len(s) == 1 else CLASS_TO_COLOR_HEADER[s.script_class]
#     #     }
#
#     if isinstance(t, Cell):
#         cells, columns, rows = [], [], []
#     elif isinstance(t, Table1D):
#         cells, columns, rows = [_cell(s) for s in t.cells], [_cell(t.script)], []
#     elif isinstance(t, Table2D):
#         cells, columns, rows = [[_cell(s) for s in r] for r in t.cells], [_cell(c) for c in t.columns], [_cell(r) for r in t.rows]
#     elif isinstance(t, TableSet):
#         cells, columns, rows = {str(tt): _get_script_properties(dictionary, tt) for tt in t.tables}, [], []
#
#     relations = {
#         'sibling': {
#             reltype: [_cell(tt) for tt in dictionary.relations.object(r, reltype) if tt != r] for reltype in RELATIONS_CATEGORIES['sibling']
#         },
#         'inclusion': {
#             reltype: [_cell(tt) for tt in dictionary.relations.object(r, reltype) if tt != r and len(tt) != 1] for reltype in RELATIONS_CATEGORIES['inclusion']
#         },
#         'father': {
#             key: [_cell(tt) for tt in dictionary.relations.object(r, 'father_' + key) if tt != r] for key in SAM
#         },
#         'child': {
#             key: [_cell(tt) for tt in dictionary.relations.object(r, 'child_' + key) if tt != r and len(tt) != 1] for key in SAM
#         }
#     }
#     for rel, rel_v in relations.items():
#         to_remove_cat = []
#         for cat, cat_v in rel_v.items():
#             if not cat_v:
#                 to_remove_cat.append(cat)
#         for cat in to_remove_cat:
#             del rel_v[cat]
#
#     # relations['inclusion']['table_2_4'] = [_cell(tt) for tt in t.root.relations.contained if tt.rank in [2,4]]
#
#     return {
#             # 'ieml': str(r),
#             'type': t.__class__.__name__,
#             'type_pretty': 'Seme' if len(r) == 1 else ('RootParadigm' if r in dictionary.tables.roots else 'Paradigm'),
#
#             'class': I_TO_CLASS[r.script_class],
#             'class_pretty': I_TO_CLASS_DISPLAY[r.script_class],
#             'layer': r.layer,
#             'size': len(r),
#             # 'translations': {l: dictionary.translations[r][l] for l in ['fr', 'en']},
#             'comments': {l: markdown.markdown(dictionary.comments[r][l]) for l in ['fr', 'en']},
#             # 'color': CLASS_TO_COLOR[r.script_class],
#             'tables': {
#                 'rank': t.rank,
#                 'parent': str(t.parent.script) if t.parent else 'Root',
#                 'dim': t.ndim,
#                 'shape': t.shape if not isinstance(t, TableSet) else [dictionary.tables[t].shape for t in t.tables],
#                 'cells': cells,
#                 'rows': rows,
#                 'columns': columns,
#                 'root': str(dictionary.tables.table_to_root[t]),
#                 'header': _cell(r)
#             },
#             'relations': relations,
#             **_cell(r)
#     }
#


def get_word_description_metadata(e: Word, lexicon: Lexicon):
    if e in lexicon.words:
        translations = {l: lexicon.translations[e][l][0] if lexicon.translations[e][l] else '' for l in LANGUAGES}
    else:
        translations = {'fr': '', 'en': ''}

    return {
        'folder': 'words',
        'file': lexicon.metadatas[e]['name'],
        'ieml': str(e),
        **translations,
        'color': CLASS_TO_COLOR[e.grammatical_class] if len(e.singular_sequences) == 1 else CLASS_TO_COLOR_HEADER[e.grammatical_class],
        'layer': e.layer,
        'multiplicity': e.cardinal,
        'type': e.__class__.__name__,
        'type_pretty': 'Word' if e.cardinal == 1 else 'WordParadigm',
        'class': I_TO_CLASS[e.grammatical_class],
        'class_pretty': I_TO_CLASS_DISPLAY[e.grammatical_class],
    }


def get_word_description(w: Word, dictionary: Dictionary, lexicon: Lexicon):
    return {
            'composition': [
                {
                    'ieml': str(word(char)),
                    'name': CHARACTERS_NAME[i],
                    'semes': [get_script_description(s, dictionary, lexicon) for s in char]
                } for i, char in enumerate(w)],
            'morpheme_serie': {
                'dim': sum(len(s) != 1 for s in w.semes),
                'shape': [tuple(len(s) for s in char if len(s) != 1) for char in w],
                'parents': [],
                'roots': []
            },
            'translations': {
                'fr': lexicon.translations[w]['fr'],
                'en': lexicon.translations[w]['en'],
            },
            'relations': {
                'etymology': {
                    'child': [get_word_description_metadata(wr,lexicon) for wr in lexicon.lattice[w].child],
                    'parents': [get_word_description_metadata(wr, lexicon) for wr in lexicon.lattice[w].parents]
                },
                'analogy': {
                    'contains': [get_word_description_metadata(wr,lexicon) for wr in lexicon.lattice[w].contains],
                    'contained_by': [get_word_description_metadata(wr, lexicon) for wr in lexicon.lattice[w].contained_by],
                }
            },
            **get_word_description_metadata(w, lexicon)
    }


def _script_to_filename(s):
    return "{}.html".format(re.sub(r'[,:;]', '_', str(s)))


def _usl_to_filename(u):
    return "usl_{}.html".format(hashlib.sha224(str(u).encode('utf8')).hexdigest())


# def _generate_page(queue):


def generate_script_site(dictionary, lexicon, output_folder, base_url):
    from shutil import copytree, rmtree

    if os.path.isdir(output_folder):
        rmtree(output_folder)
    os.makedirs(output_folder)

    static_folder = os.path.join(output_folder, 'static')
    local_folder = os.path.dirname(__file__)

    copytree(os.path.join(local_folder, 'static'), static_folder)

    all_semes = []
    for s in dictionary.scripts:
        all_semes.append(get_script_description_metadata(s, dictionary=dictionary))

    all_words = []
    for s in lexicon.words:
        all_words.append(get_word_description_metadata(s, lexicon=lexicon))

    all_items = all_semes + all_words

    print("Computing IEML database statistics...", file=sys.stderr)
    db_stats = {
        'dictionary': {
            'nb_roots': len(dictionary.tables.roots),
            'nb_semes': len([s for s in dictionary.scripts if len(s) == 1]),
            'nb_paradigms': len([s for s in dictionary.scripts if len(s) != 1]),
            'nb_relations': len(dictionary.relations.pandas())
        },
        'lexicon': {
            'nb_words': len([w for w in lexicon.words if len(w) == 1]),
            'nb_paradigms': len([w for w in lexicon.words if len(w) != 1]),
            'nb_semes_used': len(set(chain.from_iterable(w.semes for w in lexicon.words))),
            'nb_relations': sum(len(n.parents) + len(n.child) + len(n.contains) + len(n.contained_by)
                                for n in lexicon.lattice.words_to_latticeNode.values())
        }
    }

    def url_for(folder, filename):
        if folder == 'scripts':
            e = os.path.join('scripts', _script_to_filename(filename))
        elif folder == 'words':
            e = os.path.join('words', _usl_to_filename(filename))
        else:
            e = os.path.join(folder, filename)

        return e

    env = Environment(loader=FileSystemLoader(os.path.join(local_folder, 'templates')))
    env.globals['url_for'] = url_for

    template = env.get_template('index.html')

    with open(os.path.join(output_folder, 'index.html'), 'w') as fp:
        print(template.render(items=all_items,
                              db_stats=db_stats,
                              base_url=base_url), file=fp)

    template = env.get_template('script.html')

    scripts_folder = os.path.join(output_folder, 'scripts')
    os.makedirs(scripts_folder)

    for script in tqdm(dictionary.scripts, "Generating dictionary at {}".format(scripts_folder)):
        try:
            rendered = template.render(script=get_script_description(script, dictionary, lexicon),
                                       # all_scripts=all_scripts,
                                       db_stats=db_stats,
                                       base_url=base_url)
        except UndefinedError as e:
            traceback.print_exc()
            print(e.__repr__(), file=sys.stderr)
            print("Unable to generate templates for script: {}, no HTML generated.".format(str(script)), file=sys.stderr)
            continue

        with open(os.path.join(scripts_folder, _script_to_filename(script)), 'w') as fp:
            print(rendered, file=fp)

    template = env.get_template('word.html')

    words_folder = os.path.join(output_folder, 'words')
    os.makedirs(words_folder)

    for word in tqdm(lexicon.usls, "Generating usls at {}".format(words_folder)):
        try:
            rendered = template.render(word=get_word_description(word, dictionary, lexicon),
                                       # items=all_items,
                                       db_stats=db_stats,
                                       base_url=base_url)
        except UndefinedError as e:
            traceback.print_exc()
            print(e.__repr__(), file=sys.stderr)
            print("[error] Unable to generate templates for word: {}, no HTML generated.".format(str(word)),
                  file=sys.stderr)
            continue

        with open(os.path.join(words_folder, _usl_to_filename(word)), 'w') as fp:
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
