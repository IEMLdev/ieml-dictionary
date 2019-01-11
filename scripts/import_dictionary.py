from collections import defaultdict
from urllib.parse import urlencode, quote

from tqdm import tqdm
from requests import get

from ieml.constants import DICTIONARY_FOLDER
from ieml.dictionary import Dictionary
from scripts.normalize_dictionary import serialize_dictionary
from multiprocessing import Pool


DICTIONARY_URL = "https://dictionary.ieml.io/api/all?version={}"
INHIBITIONS_URL = "https://dictionary.ieml.io/api/relations/visibility?version={}&ieml={}"
COMMENTS_URL = "https://intlekt.io/api/comments/{}/"


def _download_comment(script):
    return get(COMMENTS_URL.format(script)).json()


def download_comments(scripts):
    p = Pool(32)
    comments = {'fr': {}, 'en': {}}

    comments_body_l = p.map(_download_comment, tqdm(scripts))

    for script, comments_body in zip(scripts, comments_body_l):
        if 'comments' in comments_body:
            if 'fr' in comments_body['comments'] and comments_body['comments']['fr'].strip():
                comments['fr'][script] = comments_body['comments']['fr'].strip()
            if 'en' in comments_body['comments'] and comments_body['comments']['en'].strip():
                comments['en'][script] = comments_body['comments']['en'].strip()

    return comments


def _download_inhibition(arg):
    script, d_version = arg
    res = get(INHIBITIONS_URL.format(quote(d_version), quote(script)))
    if res:
        return res.json()
    else:
        return []


INHIBITIONS_TRANSLATE = {
    "Ancestors in substance": "father-substance",
    "Ancestors in attribute": "father-attribute",
    "Ancestors in mode": "father-mode",
    "Twin siblings": "twin",
    "Opposed siblings": "opposed",
    "Associated siblings": "associated",
    "Crossed siblings": "crossed",
}


def download_inhibitions(scripts_root, d_version):
    p = Pool(32)

    inhibitions_body_l = p.map(_download_inhibition,
                               zip(scripts_root, [d_version] * len(scripts_root)))

    inhibitions = {}
    for root, inhibition in zip(scripts_root, inhibitions_body_l):
        inhibitions[root] = [INHIBITIONS_TRANSLATE[k] for k in inhibition]

    return inhibitions


def download_dictionary(d_version):
    scripts = []
    roots = []
    translations = {'fr': {}, 'en': {}}

    for s in tqdm(get(DICTIONARY_URL.format(quote(d_version))).json()):
        ieml = s['IEML']
        scripts.append(ieml)

        if s['ROOT_PARADIGM']:
            roots.append(ieml)

        translations['fr'][ieml] = s['FR']
        translations['en'][ieml] = s['EN']

    inhibitions = download_inhibitions(roots, d_version)
    comments = download_comments(scripts)

    return Dictionary(scripts=scripts,
                      root_paradigms=roots,
                      translations=translations,
                      inhibitions=inhibitions,
                      comments=comments)


if __name__ == '__main__':
    d = download_dictionary("dictionary_2018-09-03_20:39:39")
    serialize_dictionary(d, DICTIONARY_FOLDER+'2')
