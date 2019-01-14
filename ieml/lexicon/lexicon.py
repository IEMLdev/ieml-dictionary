from typing import Dict, List, Union
from collections import namedtuple, defaultdict
import yaml
import os

from ieml.constants import LANGUAGES, LEXICONS_FOLDER
from ieml.lexicon.grammar import usl


class MultiTranslations:
    def __init__(self, fr: List[str], en: List[str]):
        self.fr = list(fr)
        self.en = list(en)

    def __getitem__(self, item):
        if item in LANGUAGES:
            return getattr(self, item)

        raise KeyError("Unknown language {}".format(item))


class Lexicon:
    @classmethod
    def load(cls, root_folder: str = LEXICONS_FOLDER, names: Union[List[str], None] = None):
        lexicon = Lexicon(root_folder=root_folder)
        if names is None:
            # add all
            names = os.listdir(root_folder)

        for n in names:
            lexicon.add_lexicon(n)

        return lexicon

    def add_lexicon(self, file: str):
        name = os.path.join(self.root_folder, file)

        if os.path.isdir(name):
            files = [os.path.join(name, f) for f in os.listdir(name)]
        else:
            files = [name]

        usls = []

        for file in files:
            with open(file) as fp:
                file = yaml.load(fp)

            words = file['Words'] if file['Words'] else []

            for w in words:
                u = usl(w['ieml'])
                self.translations[u] = w['translations']
                usls.append(u)

        self.usls = sorted(self.usls + usls)

        self.inv_translations = {l: defaultdict(list) for l in LANGUAGES}
        for l in LANGUAGES:
            for u in self.usls:
                for trs in self.translations[u][l]:
                    self.inv_translations[l][trs].append(u)

    def __init__(self, root_folder: str):
        self.root_folder = root_folder

        self.usls = []
        self.translations = {l: {} for l in LANGUAGES} #translations
        self.inv_translations = {l: defaultdict(list) for l in LANGUAGES}


if __name__ == '__main__':
    file = '/home/louis/code/ieml/ieml-dictionary/definition/lexicons/eau/ms_qualite_de_l_eau.yaml'
    lexicon = Lexicon.load()
    for u in lexicon.usls:
        print(str(u), lexicon.translations[u])
