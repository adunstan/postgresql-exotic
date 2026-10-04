#!/usr/bin/env python3
"""Generate a Pig Latin (en@piglatin) .po file from a .pot template.

Usage: piglatin.py TEMPLATE.pot OUTPUT.po CATALOG
"""
import re
import sys

import poutil

# Extremely common short words are left in English.
STOPWORDS = frozenset("""
    a an the is are was be been of to in on at by for as or and it its if
    no not
""".split())

_TOKEN_RE = re.compile(r"""
    (?P<keep>
        # printf conversion spec, including %<PRId64> and %m
        %(?:\d+\$)?[-+\ \#0']*(?:\*|\d+)?(?:\.(?:\*|\d+))?
            (?:<PRI\w+>|(?:hh|h|ll|l|L|z|j|t|q)?[diouxXeEfFgGcsmp%])
      | "[^"\n]*"                       # double-quoted text
      | \\[A-Za-z!?][A-Za-z+]*          # psql backslash command
      | (?<![\w-])--?[A-Za-z][\w-]*(?:\[?=[^\s\]]*\]?)?  # command-line option
      | [^\s"]*/[^\s"]*                 # path-like token
      | \w*[_\d]\w*                     # identifier with _ or digit
      | [A-Za-z][a-z]*[A-Z][A-Za-z]*    # ALLCAPS or MixedCase word
    )
  | (?P<word>[A-Za-z]+)
""", re.VERBOSE)


def pig_word(word):
    """Translate one alphabetic word, preserving initial capitalization."""
    lower = word.lower()
    if len(word) == 1 or lower in STOPWORDS:
        return word
    if not re.search(r"[aeiouy]", lower):
        return word
    if lower[0] in "aeiou":
        result = lower + "way"
    else:
        i = 0
        while i < len(lower):
            c = lower[i]
            if c == "q" and lower[i + 1:i + 2] == "u":
                i += 2
                continue
            if c in "aeiou" or (c == "y" and i > 0):
                break
            i += 1
        result = lower[i:] + lower[:i] + "ay"
    if word[0].isupper():
        result = result[0].upper() + result[1:]
    return result


def translate(text):
    """Translate a whole message, leaving protected tokens untouched."""
    return _TOKEN_RE.sub(
        lambda m: pig_word(m.group("word")) if m.group("word")
        else m.group(0),
        text)


def main(argv):
    if len(argv) != 4:
        sys.exit(__doc__)
    pot_path, out_path, catalog = argv[1:]
    pot, entries = poutil.load_pot(pot_path)
    po = poutil.new_po("en@piglatin", catalog,
                       pot.metadata.get("POT-Creation-Date", ""))
    for src in entries:
        if src.msgid_plural:
            po.append(poutil.copy_entry(src, msgstr_plural={
                0: translate(src.msgid), 1: translate(src.msgid_plural)}))
        else:
            po.append(poutil.copy_entry(src, msgstr=translate(src.msgid)))
    blanked = poutil.save_checked(po, out_path)
    print("%s: %d entries, %d blanked by msgfmt -c"
          % (out_path, len(po), len(blanked)))


if __name__ == "__main__":
    main(sys.argv)
