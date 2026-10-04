#!/usr/bin/env python3
"""Validate a translator's output for one chunk.

Usage: check_chunk.py LANG WORKDIR/chunk-NNN.json

Reads chunk-NNN.out.json, checks every id is present with the right shape,
and runs msgfmt -c over the translated entries.  Prints each problem and
exits 1 if there are any; prints OK otherwise.
"""
import os
import sys

import polib

import poutil
import translations


def main(argv):
    if len(argv) != 3:
        sys.exit(__doc__)
    lang, chunk_path = argv[1:]
    expected = translations.read_chunk(chunk_path)
    try:
        got = translations.read_out(translations.out_path(chunk_path),
                                    expected)
    except translations.TranslationError as e:
        print(e)
        sys.exit(1)
    po = poutil.new_po(lang, "check")
    by_msgid = {}
    for i, src in expected.items():
        entry = polib.POEntry(msgid=src["msgid"],
                              msgid_plural=src.get("msgid_plural", ""),
                              flags=["c-format"] if "%" in src["msgid"]
                              else [])
        if entry.msgid_plural:
            entry.msgstr_plural = {0: got[i][0], 1: got[i][1]}
        else:
            entry.msgstr = got[i]
        po.append(entry)
        by_msgid[src["msgid"]] = i
    check_path = chunk_path[:-len(".json")] + ".check.po"
    po.save(check_path)
    bad = poutil.bad_msgids(check_path)
    os.unlink(check_path)
    for msgid in sorted(bad, key=by_msgid.get):
        print("id %d rejected by msgfmt -c (format specifiers or leading/"
              "trailing newlines differ): %r" % (by_msgid[msgid], msgid))
    if bad:
        sys.exit(1)
    print("OK")


if __name__ == "__main__":
    main(sys.argv)
