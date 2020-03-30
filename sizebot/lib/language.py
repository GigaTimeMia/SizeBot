import inflect
import toml
import importlib.resources as pkg_resources

import sizebot.data

engine = None


def load():
    global engine
    engine = inflect.engine()
    plurals = toml.loads(pkg_resources.read_text(sizebot.data, "plurals.ini"))
    print(plurals["plurals"])
    for s, p in plurals["plurals"].items():
        engine.defnoun(s, p)


load()
