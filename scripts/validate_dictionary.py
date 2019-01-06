import sys

from queue import Queue
from multiprocessing import Process

from logging import ERROR
from pykwalify import core

from ieml.dictionary import Dictionary
from scripts.normalize_dictionary import normalize_dictionary_file

core.log.level = ERROR

from pykwalify.core import Core
from pykwalify.errors import SchemaError

from ieml.constants import DICTIONARY_SCHEMA_FILE, DICTIONARY_FOLDER
from ieml.dictionary.dictionary import get_dictionary_files


def validate_schema(folder=DICTIONARY_FOLDER):
    def run_check(queue, file):
        # print(file)
        c = Core(source_file=file, schema_files=[DICTIONARY_SCHEMA_FILE])
        try:
            c.validate(raise_exception=True)
        except SchemaError as e:
            queue.put([file, e.msg])

    queue = Queue()
    process = []
    for file in get_dictionary_files(folder=folder):
        # print(file)
        process.append(Process(target=run_check, args=(queue, file)))

    for p in process:
        p.start()

    for p in process:
        p.join()  # this blocks until the process terminates

    errors = []
    while queue.qsize():
        errors.append(queue.get())

    for e in errors:
        print("Server.check_dictionary: Validation error in root paradigm file at '{}'\n* {}".format(*e),
              file=sys.stderr)
        return False

    return True


def validate_normalization(folder=DICTIONARY_FOLDER):
    for f in get_dictionary_files(folder=folder):
        with open(f) as fp:
            content_f = fp.read()

        content = normalize_dictionary_file(f)
        if content != content_f:
            print("Validation error: File '{}' is not normalized".format(f), file=sys.stderr)
            return False

    return True


def validate_dictionary(folder=DICTIONARY_FOLDER):
    try:
        Dictionary.load(folder=folder, use_cache=False)
        return True
    except Exception as e:
        print(e.__repr__(), file=sys.stderr)
        return False


def validate(folder=DICTIONARY_FOLDER):
    if not validate_schema(folder):
        print("A dictionary file is not well-formed. File must conform to yaml schema file at "
              "{} ".format(DICTIONARY_SCHEMA_FILE),
              file=sys.stderr)
        return False

    if not validate_normalization(folder):
        print("A dictionary file is not normalized, it has inconsistent indentation or fields order. Please run "
              "'python script/normalize_dictionary.py' to fix this error",
              file=sys.stderr)
        return False

    if not validate_dictionary(folder):
        print("Inconsistent dictionary structure.",
              file=sys.stderr)
        return False

    return True


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Validate the dictionary files')

    parser.add_argument('--dictionary-folder', type=str, required=False, default=DICTIONARY_FOLDER,
                        help='the dictionary definition folder')
    args = parser.parse_args()

    if not validate(args.dictionary_folder):
        sys.exit(1)