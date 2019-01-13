from typing import Dict, List
from collections import namedtuple
import yaml

from ieml.constants import LANGUAGES
from ieml.dictionary.dictionary import Translations
from ieml.lexicon.grammar import Usl
from ieml.lexicon.morphemes_serie import SemesGroup, MorphemesSerie


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
    def parse_file(cls, file: str):
        with open(file) as fp:
            file = yaml.load(fp)

        ms = file['MorphemesSerie']
        groups = [SemesGroup(semes=sg['semes'], multiplicity=sg['multiplicity']) for sg in ms['groups']]
        constant = SemesGroup(semes=ms['constant']['semes'], multiplicity=None)
        translations = Translations(**ms['translations'])

        morphemes_serie = MorphemesSerie(groups=groups, constant=constant, translations=translations)

        return morphemes_serie

    def __init__(self, usls: List[Usl], translations: Dict[Usl, MultiTranslations]):
        self.usls = sorted(usls)
        self.translations = translations

        self.inv_translations = {l: {trans: u for trans in self.translations[u][l] for u in self.usls} for l in LANGUAGES}



if __name__ == '__main__':
    file = '/home/louis/code/ieml/ieml-dictionary/definition/lexicons/eau/ms_qualite_de_l_eau.yaml'
    ms = Lexicon.parse_file(file)
    for m in ms.morphemes:
        print(str(m))
