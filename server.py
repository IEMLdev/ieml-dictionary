import os

from ieml import dictionary
from ieml.dictionary.table.table import TableSet, Table1D, Table2D, Table3D, Cell

dictionary.USE_CACHE = False
from ieml.dictionary import Dictionary
from flask.json import jsonify

from flask import Flask, render_template

app = Flask(__name__)

os.chdir(os.path.abspath(os.path.curdir))

def get_table(d, r):
    t = d.tables[r]

    def _cell(s):
        if s in d:
            translations = {l: d.translations[s][l] for l in ['fr', 'en']}
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
        cells, columns, rows = {str(tt): get_table(d, tt) for tt in t.tables}, [], []


    return {
            'ieml': str(r),
            'layer': r.layer,
            'size': len(r),
            'translations': {l: d.translations[r][l] for l in ['fr', 'en']},
            'tables': {
                'rank': t.rank,
                'parent': str(t.parent.script) if t.parent else 'Root',
                'dim': t.ndim,
                'shape': t.shape if not isinstance(t, TableSet) else [d.tables[t].shape for t in t.tables],
                'cells': cells,
                'rows': rows,
                'columns': columns
            }
    }


d_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'dictionary')
dictionary = Dictionary.load(d_path)


@app.route('/')
def index():
    scripts = [get_table(dictionary, r) for r in dictionary.scripts]
    return render_template('index.html', scripts=scripts)


@app.route('/<s>')
def view_table(s):
    try:
        script = dictionary[s]
    except KeyError:
        return "<strong>{}</strong> not defined in dictionary".format(s)

    return render_template('table.html', script=get_table(dictionary, script))
