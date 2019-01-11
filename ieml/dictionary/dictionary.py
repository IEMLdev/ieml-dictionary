import hashlib
from typing import List, Dict

import dill

import sys

from ieml.constants import LANGUAGES, DICTIONARY_FOLDER
from ieml.dictionary.relation.relations import RelationsGraph
from ieml.dictionary.script import script
import numpy as np

from collections import namedtuple
import os
import yaml

from ieml.dictionary.table.table_structure import TableStructure


Translations = namedtuple('Translations', sorted(LANGUAGES))
Translations.__getitem__ = lambda self, item: self.__getattribute__(item) if item in LANGUAGES \
    else tuple.__getitem__(self, item)

Comments = namedtuple('Comments', sorted(LANGUAGES))
Comments.__getitem__ = lambda self, item: self.__getattribute__(item) if item in LANGUAGES \
    else tuple.__getitem__(self, item)


class FolderWatcherCache:
    def __init__(self, folder: str, cache_folder: str):
        """
        Cache that check if `folder` content has changed. Compute a hash of the files in the folder and
        get pruned if the content of this folder change.

        :param folder: the folder to watch
        :param cache_folder: the folder to put the cache file
        """
        self.folder = folder
        self.cache_folder = os.path.abspath(cache_folder)

    def update(self, obj) -> None:
        """
        Update the cache content, remove old cache files from the cache directory.

        :param obj: the object to pickle in the cache
        :return: None
        """
        for c in self._cache_candidates():
            os.remove(c)

        with open(self.cache_file, 'wb') as fp:
            dill.dump(obj, fp)

    def get(self) -> object:
        """
        Unpickle and return the object stored in the cache file.
        :return: the stored object
        """
        with open(self.cache_file, 'rb') as fp:
            return dill.load(fp)

    def is_pruned(self) -> bool:
        """
        Return True if the watched folder content has changed.
        :return: if the folder content changed
        """
        names = [p for p in self._cache_candidates()]
        if len(names) != 1:
            return True

        return self.cache_file != names[0]

    @property
    def cache_file(self) -> str:
        """
        :return: The cache file absolute path
        """
        res = b""
        for file in sorted(os.listdir(self.folder)):
            with open(os.path.join(self.folder, file), 'rb') as fp:
                res += file.encode('utf8') + b":" + fp.read()

        return os.path.join(self.cache_folder, ".dictionary-cache.{}".format(hashlib.md5(res).hexdigest()))

    def _cache_candidates(self) -> List[str]:
        """
        Return all the cache files from the cache folder (the pruned and the current one)
        :return: All the cache files from the cache folder
        """
        return [os.path.join(self.cache_folder, n) for n in os.listdir(self.cache_folder) if n.startswith('.dictionary-cache.')]


def get_dictionary_files(folder:str=DICTIONARY_FOLDER):
    return sorted(os.path.join(folder, f) for f in os.listdir(folder) if f.endswith('.yaml'))


class Dictionary:
    @classmethod
    def load(cls, folder:str=DICTIONARY_FOLDER, use_cache:bool=True, cache_folder:str=os.path.abspath('.')):
        """
        Load a dictionary from a dictionary folder. The folder must contains a list of paradigms
        :param folder: The folder
        :param use_cache:
        :param cache_folder:
        :return:
        """
        print("Dictionary.load: Reading dictionary at {}".format(folder), file=sys.stderr)

        if use_cache:
            cache = FolderWatcherCache(folder, cache_folder=cache_folder)
            if not cache.is_pruned():
                print("Dictionary.load: Reading cache at {}".format(cache.cache_file), file=sys.stderr)

                return cache.get()

            print("Dictionary.load: Dictionary files changed  Recomputing cache.", file=sys.stderr)

        scripts = []
        translations = {'fr': {}, 'en': {}}
        comments = {'fr': {}, 'en': {}}

        def _add_metadatas(ieml, c):
            translations['fr'][ieml] = c['translations']['fr'].strip()
            translations['en'][ieml] = c['translations']['en'].strip()
            if 'comments' in c:
                if 'fr' in c['comments']: comments['fr'][ieml] = c['comments']['fr'].strip()
                if 'en' in c['comments']: comments['en'][ieml] = c['comments']['en'].strip()

        roots = []
        inhibitions = {}

        n_ss = 0
        n_p = 0
        for f in get_dictionary_files(folder):
            with open(f) as fp:
                d = yaml.load(fp)

            try:
                root = d['RootParadigm']['ieml']
                inhibitions[root] = d['RootParadigm']['inhibitions']

                roots.append(root)

                _add_metadatas(root, d['RootParadigm'])
                scripts.append(root)

                if 'Semes' in d and d['Semes']:
                    for c in d['Semes']:
                        n_ss += 1
                        scripts.append(c['ieml'])
                        _add_metadatas(c['ieml'], c)

                if 'Paradigms' in d and d['Paradigms']:
                    for c in d['Paradigms']:
                        n_p += 1
                        scripts.append(c['ieml'])
                        _add_metadatas(c['ieml'], c)

            except (KeyError, TypeError):
                raise ValueError("'{}' is not a valid dictionary yaml file".format(f))

        print("Dictionary.load: Read {} root paradigms, {} paradigms and {} semes".format(len(roots), n_p, n_ss), file=sys.stderr)

        print("Dictionary.load: Computing table structure and relations ...", file=sys.stderr)
        dictionary = cls(scripts=scripts,
                         translations=translations,
                         root_paradigms=roots,
                         inhibitions=inhibitions,
                         comments=comments)
        print("Dictionary.load: Computing table structure and relations", file=sys.stderr)

        if use_cache:
            print("Dictionary.load: Updating cache at {}".format(cache.cache_file), file=sys.stderr)
            cache.update(dictionary)

        return dictionary

    def __init__(self,
                 scripts: List[str],
                 root_paradigms: List[str],
                 translations: Dict[str, Dict[str, str]],
                 inhibitions: Dict[str, List[str]],
                 comments: Dict[str, Dict[str, str]]):
        
        self.scripts = np.array(sorted(script(s) for s in scripts))
        self.index = {e: i for i, e in enumerate(self.scripts)}

        # list of root paradigms
        self.roots_idx = np.zeros((len(self.scripts),), dtype=int)
        self.roots_idx[[self.index[r] for r in root_paradigms]] = 1

        # scripts to translations
        self.translations = {s: Translations(fr=translations['fr'][s], en=translations['en'][s]) for s in self.scripts}

        # scripts to translations
        self.comments = {s: Comments(fr=comments['fr'][s] if s in comments['fr'] else '',
                                     en=comments['en'][s] if s in comments['en'] else '') for s in self.scripts}

        # map of root paradigm script -> inhibitions list values
        self._inhibitions = inhibitions

        # self.tables = TableStructure
        self.tables = TableStructure(self.scripts, self.roots_idx)

        self.relations = RelationsGraph(dictionary=self)

    def __len__(self):
        return self.scripts.__len__()

    # def one_hot(self, s):
    #     return np.eye(len(self), dtype=int)[self.index[s]]

    def __getitem__(self, item):
        return self.scripts[self.index[script(item)]]

    def __contains__(self, item):
        return item in self.index


if __name__ == '__main__':
    d = Dictionary.load()

    for s in d.scripts:
        print("en", d.translations[s]['en'])