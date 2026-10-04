#!/usr/bin/env python3
"""Merge translated chunks into a .po file.

Usage: merge.py LANG CATALOG TEMPLATE.pot WORKDIR OUTPUT.po

Applies chunk-*.out.json, then retry.out.json (which overrides).  Entries
that are missing, unreadable, or rejected by msgfmt -c are left blank and
written to WORKDIR/retry.json for one more translation pass.
"""
import os
import sys

import poutil
import translations


def main(argv):
    if len(argv) != 6:
        sys.exit(__doc__)
    lang, catalog, pot_path, workdir, out_path = argv[1:]
    pot, entries = poutil.load_pot(pot_path)
    got = {}
    for chunk_path in translations.chunk_paths(workdir):
        expected = translations.read_chunk(chunk_path)
        try:
            got.update(translations.read_out(
                translations.out_path(chunk_path), expected))
        except translations.TranslationError as e:
            print("skipping: %s" % e)
    po = poutil.new_po(lang, catalog,
                       pot.metadata.get("POT-Creation-Date", ""))
    for i, src in enumerate(entries):
        t = got.get(i)
        if src.msgid_plural:
            po.append(poutil.copy_entry(
                src, msgstr_plural={0: t[0], 1: t[1]} if t else None))
        else:
            po.append(poutil.copy_entry(src, msgstr=t or ""))
    blanked = set(poutil.save_checked(po, out_path))
    retry = [i for i, e in enumerate(entries)
             if i not in got or e.msgid in blanked]
    retry_path = os.path.join(workdir, "retry.json")
    if retry and not os.path.exists(translations.out_path(retry_path)):
        translations.write_chunk(
            retry_path, [translations.entry_dict(i, entries[i])
                         for i in retry])
    print("%s: %d entries, %d translated, %d missing, %d blanked by "
          "msgfmt -c" % (out_path, len(entries),
                         len(entries) - len(retry),
                         len([i for i in retry if i not in got]),
                         len(blanked)))


if __name__ == "__main__":
    main(sys.argv)
