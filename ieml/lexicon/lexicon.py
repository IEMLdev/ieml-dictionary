import yaml


class Lexicon:
    @classmethod
    def parse_file(cls, file: str):
        with open(file) as fp:
            yaml.load(fp)

    def __init__(self):
        self.usls = []