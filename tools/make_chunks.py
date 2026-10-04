#!/usr/bin/env python3
"""Split a .pot template into JSON chunks for translation.

Usage: make_chunks.py TEMPLATE.pot WORKDIR [SIZE]

Writes WORKDIR/chunk-NNN.json (default SIZE 250 entries per chunk).
"""
import os
import sys

import poutil
import translations


def main(argv):
    if len(argv) not in (3, 4):
        sys.exit(__doc__)
    pot_path, workdir = argv[1:3]
    size = int(argv[3]) if len(argv) == 4 else 250
    os.makedirs(workdir, exist_ok=True)
    _, entries = poutil.load_pot(pot_path)
    items = [translations.entry_dict(i, e) for i, e in enumerate(entries)]
    for n, start in enumerate(range(0, len(items), size)):
        translations.write_chunk(os.path.join(workdir, "chunk-%03d.json" % n),
                                 items[start:start + size])
    print("%s: %d entries in %d chunks"
          % (workdir, len(items), (len(items) + size - 1) // size))


if __name__ == "__main__":
    main(sys.argv)
