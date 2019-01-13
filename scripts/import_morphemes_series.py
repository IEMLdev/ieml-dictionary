import re
from requests import get
from tqdm import tqdm

URL_ALL_MS = 'https://intlekt.io/api/morphemes_series/'
URL_MS_DETAIL = 'https://intlekt.io/api/morphemes_series/{}/'


def download_lexicons():
    all_ms = {}
    for ms in tqdm(get(URL_ALL_MS).json()):
        all_ms[ms['id']] = get(URL_MS_DETAIL.format(ms['id'])).json()

    return all_ms


INDENT = '    '

def _clean_translation(s):
    s = re.sub('"', '\"', s)
    return s

def _serialize_group(semes, multiplicity=None, indent=2):
    res = INDENT * indent + "- semes: [{}]\n".format(', '.join('"{}"'.format(s) for s in semes)) + \
          INDENT * indent + "  multiplicity: {}\n".format(multiplicity if multiplicity else -1)
    return res

def _serialize_constant(constant, indent=2):
    res = INDENT * indent + "semes: [{}]\n".format(
        ', '.join('"{}"'.format(s) for s in constant['words']) if constant else '')
    return res

def _serialize_morpheme(mrph, indent=2):
    if not mrph['id']:
        return ''
    res = INDENT * indent + '- ieml: "{}"\n'.format(mrph['ieml']) + \
          INDENT * indent + "  translations:\n" + \
          INDENT * (indent + 1) + "fr:\n" + \
          ''.join(INDENT * (indent + 2) + '- "{}"\n'.format(_clean_translation(fr)) for fr in
                  mrph['descriptors']['fr']) + \
          INDENT * (indent + 1) + "en:\n" + \
          ''.join(
              INDENT * (indent + 2) + '- "{}"\n'.format(_clean_translation(en)) for en in mrph['descriptors']['en'])

    return res

def serialize_morphemes_serie(ms_json):
    res = """MorphemesSerie:
    groups:
{}
    constants:
{}
    translations:
        fr: |-
            {}
        en: |-
            {}
    morphemes:
{}""".format(''.join(
        _serialize_group(grp['words'], grp['multiplicity'], indent=2) for grp in ms_json['groups']).rstrip(),
             _serialize_constant(ms_json['constants'], indent=2).rstrip(),
             ms_json['name'], ms_json['name'],
             ''.join(_serialize_morpheme(mrph, indent=2) for mrph in ms_json['morphemes']))

    return res


import os


def _clean_name(n):
    n = re.sub('[èéê]', 'e', n)
    n = re.sub('[ÉÉÊ]', 'E', n)
    n = re.sub('[àáâ]', 'a', n)
    return re.sub('[^a-zA-Z0-9\-]+', '_', n)


def save_morphemes_serie(all_ms, output_folder):
    for ms in all_ms.values():
        f, name = ms['name'].split(':')
        ff = os.path.join(output_folder, _clean_name(f.lower()))
        if not os.path.isdir(ff):
            os.mkdir(ff)

        file_name = os.path.join(ff, 'ms_{}.yaml'.format(_clean_name(name.strip())))

        print(ms['id'], file_name)
        with open(file_name, 'w') as fp:
            print(serialize_morphemes_serie(ms), file=fp)


if __name__ == '__main__':
    all_ms = download_lexicons()
    save_morphemes_serie(all_ms=all_ms,
                         output_folder='/home/louis/code/ieml/ieml-dictionary/definition/lexicons/')