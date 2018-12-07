import os
import sys
from logging import ERROR
from time import sleep
from pykwalify import core
core.log.level = ERROR

from pykwalify.core import Core
from pykwalify.errors import SchemaError

from ieml.dictionary.dictionary import FolderWatcherCache
from ieml.dictionary.table.table import TableSet, Table1D, Table2D, Cell
from ieml.dictionary import Dictionary
from flask import Flask, render_template
from multiprocessing import Process, Queue

current_dir = os.path.abspath(os.path.dirname(__file__))
os.chdir(current_dir)
print(current_dir)
app = Flask(__name__)

dictionary_path = os.path.join(current_dir, 'dictionary')


def check_dictionary():
    def run_check(queue, file):
        c = Core(source_file=file, schema_files=['dictionary_paradigm_schema.yaml'])
        try:
            c.validate(raise_exception=True)
        except SchemaError as e:
            queue.put([file, e.msg])

    queue = Queue()
    process = []
    for file in [os.path.join(dictionary_path, p) for p in os.listdir(dictionary_path)]:
        process.append(Process(target=run_check, args=(queue, file)))

    for p in process:
        p.start()

    for p in process:
        p.join() # this blocks until the process terminates

    sleep(0.1)

    errors = []
    while queue.qsize():
        errors.append(queue.get())

    for e in errors:
        print("Server.check_dictionary: Validation error in root paradigm file at '{}'\n* {}".format(*e), file=sys.stderr)
        return False

    return True


cache = FolderWatcherCache(dictionary_path, cache_folder=current_dir)

if cache.is_pruned() and not check_dictionary():
    print("Server: Shutting down", file=sys.stderr)
    sys.exit(1)

dictionary = Dictionary.load(dictionary_path, cache_folder=current_dir)

RELATIONS_CATEGORIES = {
    'inclusion': ['contains', 'contained'],
    'etymology': ['father', 'child'],
    'sibling': ['twin', 'associated', 'crossed', 'opposed']
}

SAM = ["substance", "attribute", "mode"]



def get_table(r):
    t = dictionary.tables[r]

    def _cell(s):
        if s in dictionary:
            translations = {l: dictionary.translations[s][l] for l in ['fr', 'en']}
        else:
            translations = {}

        return {
            'ieml': str(s),
            'translations': translations
        }

    if isinstance(t, Cell):
        cells, columns, rows = [], [], []
    elif isinstance(t, Table1D):
        cells, columns, rows = [_cell(s) for s in t.cells], [_cell(t.script)], []
    elif isinstance(t, Table2D):
        cells, columns, rows = [[_cell(s) for s in r] for r in t.cells], [_cell(c) for c in t.columns], [_cell(r) for r in t.rows]
    elif isinstance(t, TableSet):
        cells, columns, rows = {str(tt): get_table(tt) for tt in t.tables}, [], []

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
            'layer': r.layer,
            'size': len(r),
            'translations': {l: dictionary.translations[r][l] for l in ['fr', 'en']},
            'tables': {
                'rank': t.rank,
                'parent': str(t.parent.script) if t.parent else 'Root',
                'dim': t.ndim,
                'shape': t.shape if not isinstance(t, TableSet) else [dictionary.tables[t].shape for t in t.tables],
                'cells': cells,
                'rows': rows,
                'columns': columns
            },
            'relations': relations
    }


@app.route('/')
def index():
    scripts = [get_table(r) for r in dictionary.scripts]
    return render_template('index.html', scripts=scripts)


@app.route('/<s>')
def view_table(s):
    try:
        script = dictionary[s]
    except KeyError:
        return "<strong>{}</strong> not defined in dictionary".format(s)

    return render_template('table.html', script=get_table(script))
