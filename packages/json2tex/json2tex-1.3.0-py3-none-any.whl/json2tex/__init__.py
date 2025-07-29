# system modules
import functools
import itertools
import unicodedata
import re
import json
import sys
import argparse

# internal modules

# external modules
import inflect
from pylatexenc.latexencode import unicode_to_latex

INFLECT = inflect.engine()


def glyph2ascii(g: str):
    """
    Convert a single unicode glyph to an ascii representation
    """
    # σ → GREEK SMALL LETTER SIGMA
    name = unicodedata.name(g)
    # GREEK SMALL LETTER SIGMA → SIGMA
    for prefix in (
        prefixes := [
            r"^\w+\s+(?:SMALL|CAPITAL)\s+LETTER\s+",
            r"^MATHEMATICAL\s+",
            r"^COMBINING\s+",
        ]
    ):
        name = re.sub(
            prefix,
            r"",
            name,
            flags=re.IGNORECASE,
        )
    return name


def str2ascii(string, modifier=lambda s: s):
    """
    Convert all non-ascii glyphs in a string to ascii.
    The modifier is a string manipulation function for post-processing.
    """
    return re.sub(
        r"[^\x00-\x7F]", lambda m: modifier(glyph2ascii(m.group())), string
    )


def counter2words(n):
    return INFLECT.ordinal(
        re.sub(r"\W+", r" ", INFLECT.number_to_words(n, andword="", comma=""))
    )


def numbers2words(s):
    if isinstance(s, int):
        return counter2words(s)
    numbers = re.findall(r"\d+", str(s))
    outs = s
    for number in numbers:
        words = re.sub(
            r"\W+", r" ", INFLECT.number_to_words(number, andword="", comma="")
        )
        outs = outs.replace(number, " {} ".format(words), 1)
    return outs


def elements2texmaxcroname(elements):
    # TODO this screams to be implemented as pipe, but Python doesn't have one 😑
    parts = []
    for i, element in enumerate(elements, start=1):
        element = numbers2words(element)
        element = str(element)
        element = str2ascii(element, modifier="_{}_".format)
        element = element.title()
        element = re.sub(r"[^a-z]+", r" ", element, flags=re.IGNORECASE)
        parts.append(element)
    return re.sub(r"\s+", r"", " ".join(parts))


def dead_ends(d, path=tuple()):
    """
    Generator recursing into a dictionary and yielding tuples of paths and the
    value at dead ends.
    """
    if type(d) in (str, int, bool, float, type(None)):
        # print(f"Reached a dead end: {d}")
        yield path, d
        return
    elif hasattr(d, "items"):
        # print(f"recursing into dict {d}")
        for k, v in d.items():
            for x in dead_ends(v, path + (k,)):
                yield x
    else:
        try:
            it = iter(d)
            # print(f"recursing into list {d}")
            for i, e in enumerate(d):
                for x in dead_ends(e, path + (i + 1,)):
                    yield x
        except TypeError:
            # print(f"Don't know what to do with {d}. Assuming it's a dead
            # end.")
            yield sequence, d


def json2texcommands(d, escape=True):
    """
    Convert a JSON dict to LaTeX \\newcommand definitions

    Args:
        d (JSON-like object): the JSON to convert

    Yields:
        str : LaTeX \\newcommand definitions
    """
    macronames = set()
    # Traverse the merged inputs and output TeX definitions
    for name_parts, raw_value in dead_ends(d):
        name_parts = list(name_parts or ["unnamed"])
        for conflictnr in itertools.count(start=1):
            name = elements2texmaxcroname(name_parts)
            if name not in macronames:
                break
            suffix = f"collision {INFLECT.number_to_words(conflictnr,andword='',comma='')}"
            if conflictnr > 1:
                name_parts[-1] = suffix
            else:
                name_parts.append(suffix)
        macronames.add(name)
        value = unicode_to_latex(raw_value) if escape else raw_value
        latex = f"\\newcommand{{\\{name}}}{{{value}}}"
        yield latex


def json2texfile(d, path, **kwargs):
    with path if hasattr(path, "write") else open(path, "w") as fh:
        for latex in sorted(json2texcommands(d, **kwargs)):
            fh.write(f"{latex}\n")


def cli(cliargs=None):
    """
    Run :mod:`json2tex`'s command-line interface

    Args:
        cliargs (sequence of str, optional): the command-line arguments to use.
            Defaults to :any:`sys.argv`
    """
    parser = argparse.ArgumentParser(description="Convert JSON to TEX")
    parser.add_argument(
        "-i",
        "--input",
        help="input JSON file",
        nargs="+",
        type=argparse.FileType("r"),
        default=[sys.stdin],
    )
    parser.add_argument(
        "-o",
        "--output",
        help="output TEX file",
        type=argparse.FileType("w"),
        default=sys.stdout,
    )
    parser.add_argument(
        "--no-escape",
        help="Don't do any escaping of special LaTeX characters",
        action="store_true",
    )
    args = parser.parse_args(cliargs)

    # Merge all inputs
    for f in args.input:
        d = json.load(f)
        try:
            JSON
        except NameError:
            JSON = d
            continue
        if isinstance(JSON, list):
            if isinstance(d, list):
                JSON.extend(d)
            else:
                JSON.append(d)
        elif isinstance(JSON, dict):
            if isinstance(d, dict):
                JSON.update(d)
            else:
                JSON = [JSON, d]

    json2texfile(JSON, path=args.output, escape=not args.no_escape)


if __name__ == "__main__":
    cli()
