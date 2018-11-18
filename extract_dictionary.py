from ieml.dictionary import Dictionary
from ieml.dictionary.table import TableSet
import re
from pykwalify.core import Core


def get_index(r, c):
    if isinstance(r, TableSet):
        for i, ts in enumerate(r.tables):
            if c in ts:
                return get_index(ts, c)
    else:
        return '[' + ', '.join(str(i) for i in r.index_of(c)) + ']'

def get_translations(c):
    clean = lambda e: re.sub('\n+', "\n", e)
    return (clean(c.translations.fr), clean(c.translations.en))

if __name__ == '__main__':

    import sys
    version = sys.argv[1]

    d = Dictionary(version)
    for root in d.roots:
        file_out = 'dictionary/{}_{}.yaml'.format(root.layer, re.sub('[^a-zA-Z0-9\-]+', '_', root.translations.en))
        with open(file_out, 'w') as fp:
            res = """RootParadigm:
    ieml: "{}"
    translations:
        fr: >
            {}
        en: >
            {}
    inhibitions: {}
""".format(str(root.script), *get_translations(root), str(d.inhibitions[root]))
            res += "Terms:"
            for c in root:
                res += """
    - ieml: "{}"
      index: {}
      translations:
          fr: >
              {}
          en: >
              {}
""".format(str(c.script), get_index(root, c), *get_translations(c))
            p = [e for e in root.relations.contains if len(e) != 1 and e != root]
            res += "Paradigms:"
            for c in p:
                res += """
    - ieml: "{}"
      translations:
          fr: >
              {}
          en: >
              {}
""".format(str(c.script), *get_translations(c))

            print(res, file=fp)
        print("Validating:", file_out)
        c = Core(source_file=file_out, schema_files=['dictionary_paradigm_schema.yaml'])
        c.validate(raise_exception=True)

