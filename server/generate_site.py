from jinja2 import Environment, FileSystemLoader, UndefinedError
from functools import lru_cache
from urllib.parse import quote
from ieml.constants import DICTIONARY_FOLDER
from ieml.dictionary import Dictionary
from ieml.dictionary.table.table import TableSet, Table1D, Table2D, Cell
import os
from tqdm import tqdm
import sys

RELATIONS_CATEGORIES = {
    'inclusion': ['contains', 'contained'],
    'etymology': ['father', 'child'],
    'sibling': ['twin', 'associated', 'crossed', 'opposed']
}

SAM = ["substance", "attribute", "mode"]
I_TO_CLASS_DISPLAY = ['Auxiliary', 'Verb', 'Noun']
CLASS_TO_COLOR = ['#fff1bc', '#ffe5d7', '#d9eaff']


@lru_cache(maxsize=10000)
def get_table(dictionary, r):
    t = dictionary.tables[r]

    def _cell(s):
        if s in dictionary:
            translations = {l: dictionary.translations[s][l] for l in ['fr', 'en']}
        else:
            translations = {}

        return {
            'ieml': str(s),
            'translations': translations,
            'color': CLASS_TO_COLOR[s.script_class]
        }

    if isinstance(t, Cell):
        cells, columns, rows = [], [], []
    elif isinstance(t, Table1D):
        cells, columns, rows = [_cell(s) for s in t.cells], [_cell(t.script)], []
    elif isinstance(t, Table2D):
        cells, columns, rows = [[_cell(s) for s in r] for r in t.cells], [_cell(c) for c in t.columns], [_cell(r) for r in t.rows]
    elif isinstance(t, TableSet):
        cells, columns, rows = {str(tt): get_table(dictionary, tt) for tt in t.tables}, [], []

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
            'ieml': str(r),
            'type': t.__class__.__name__,
            'class': I_TO_CLASS_DISPLAY[r.script_class],
            'layer': r.layer,
            'size': len(r),
            'translations': {l: dictionary.translations[r][l] for l in ['fr', 'en']},
            'color': CLASS_TO_COLOR[r.script_class],
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
    }


def url_for(folder, filename):
    if folder == 'scripts':
        e = quote(filename) + '.html'
    else:
        e = os.path.join(folder, filename)

    return e


I_TO_CLASS = ['aux', 'verb', 'noun']


def generate_script_site(dictionary, output_folder, base_url):
    from shutil import copytree, rmtree

    if os.path.isdir(output_folder):
        rmtree(output_folder)
    os.makedirs(output_folder)

    static_folder = os.path.join(output_folder, 'static')
    local_folder = os.path.dirname(__file__)

    copytree(os.path.join(local_folder, 'static'), static_folder)

    env = Environment(loader=FileSystemLoader(os.path.join(local_folder, 'templates')))
    env.globals['url_for'] = url_for

    all_scripts = [{
        'ieml': str(s),
        'fr': dictionary.translations[s].fr,
        'en': dictionary.translations[s].en,
        'layer': s.layer,
        'type': 'seme' if len(s) == 1 else ('root' if s in dictionary.tables.roots else 'paradigm'),
        'class': I_TO_CLASS[s.script_class]
    } for s in dictionary.scripts]

    dictionary_stats = {
        'nb_roots': len(dictionary.tables.roots),
        'nb_semes': len([s for s in dictionary.scripts if len(s) == 1]),
        'nb_paradigms': len([s for s in dictionary.scripts if len(s) != 1]),
        'nb_relations': len(dictionary.relations.pandas())
    }

    template = env.get_template('index.html')

    with open(os.path.join(output_folder, 'index.html'), 'w') as fp:
        print(template.render(scripts=all_scripts,
                              dictionary_stats=dictionary_stats,
                              base_url=base_url), file=fp)

    template = env.get_template('script.html')

    for script in tqdm(dictionary.scripts):
        try:
            rendered = template.render(script=get_table(dictionary, script),
                                       all_scripts=all_scripts,
                                       dictionary_stats=dictionary_stats,
                                       base_url=base_url)
        except UndefinedError as e:
            print(e.__repr__(), file=sys.stderr)
            print("Unable to generate templates for script: {}, no HTML generated.".format(str(script)), file=sys.stderr)
            continue

        with open(os.path.join(output_folder, str(script) + '.html'), 'w') as fp:
            print(rendered, file=fp)


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Generate the dictionary static website.')

    parser.add_argument('output_folder', type=str, help='the website output folder')
    parser.add_argument('base_url', type=str, help='the website base url')

    parser.add_argument('--dictionary-folder', type=str, required=False, default=DICTIONARY_FOLDER,
                        help='the dictionary definition folder')


    args = parser.parse_args()

    dictionary = Dictionary.load(args.dictionary_folder)
    generate_script_site(dictionary, args.output_folder, base_url=args.base_url)