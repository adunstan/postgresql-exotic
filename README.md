# postgresql-exotic

Message catalogs for PostgreSQL in three languages nobody asked for:
Pig Latin, Esperanto, and Klingon.

```
$ LANGUAGE=tlh LC_MESSAGES=en_US.utf8 psql -c 'SELECT 1/0'
Qagh:  pagh mI' wavlu'

$ LANGUAGE=eo LC_MESSAGES=en_US.utf8 LC_CTYPE=en_US.utf8 psql -c 'SELECT * FROM no_such_table'
ERARO:  rilato "no_such_table" ne ekzistas

$ LANGUAGE=en@piglatin LC_MESSAGES=en_US.utf8 psql -c 'SELECT 1/0'
ERROR:  ivisionday by erozay
```

This is a demo, not a submission.  PostgreSQL translations are maintained
upstream through the pgtranslation project, and I don't expect it to take
Klingon any time soon.

## What's here

| Path | Contents |
|---|---|
| `patches/` | Three `git format-patch` commits against PostgreSQL master (20devel), one per language |
| `catalogs/<domain>/<lang>.po` | The same catalogs as plain files: `postgres` (backend), `psql`, `libpq` |
| `templates/` | The `.pot` templates the catalogs were built from |
| `tools/` | Pig Latin generator, translation chunking/checking/merging tools, unit tests, smoke test |
| `docs/` | Design spec, implementation plan, progress log, glossary, translator instructions |

Each language covers every message in the three domains: 6217 backend,
1528 psql and 411 libpq messages, all passing `msgfmt -c`.

## The languages

**Pig Latin** (`en@piglatin`) is generated mechanically by
`tools/piglatin.py`.  The language code follows GNU gettext's own synthetic
English variants (`en@quot`, `en@boldquot`).  Format specifiers, quoted
text, all-caps words, identifiers, command-line options, psql backslash
commands and paths are left alone, as are a handful of very common short
words (`the`, `a`, `is`, `of` and friends), which is why the severity still
says `ERROR`.

**Esperanto** (`eo`) and **Klingon** (`tlh`) were machine translated by
parallel LLM agents, 250 messages at a time, against a shared glossary
(`docs/glossary.tsv`), then normalised for consistent terminology.
Klingon uses Okrand's Latin orthography, not pIqaD.  Klingon has
remarkably little database vocabulary, so a lot of it is coined:
`ghItlh mI'` ("writing of numbers") for table, `De' pa'` ("data room") for
database, `lo'wI' HoD` ("captain user") for superuser.  FATAL is `Hegh`
and PANIC is `Hegh'a'`, which seems about right.

Neither has been checked by a fluent speaker.  Corrections are welcome.

## Using it

Apply the patches to a PostgreSQL checkout, build with NLS enabled, and
install:

```
cd postgresql
git am /path/to/postgresql-exotic/patches/*.patch
meson setup build -Dnls=enabled
ninja -C build install
```

Or just drop the `.po` files from `catalogs/` into `src/backend/po`,
`src/bin/psql/po` and `src/interfaces/libpq/po` and add the language codes
to each `LINGUAS`.

None of these has a system locale, so select them with the `LANGUAGE`
environment variable plus any installed locale other than C/POSIX for
`LC_MESSAGES`.  gettext ignores `LANGUAGE` under the C locale.

- Client side (psql, libpq): set `LANGUAGE` and `LC_MESSAGES` in the
  environment.  Esperanto also needs a UTF-8 `LC_CTYPE`, otherwise the
  accented letters come out as `?`.
- Server side: start the postmaster with `LANGUAGE` in its environment
  and set `lc_messages` in `postgresql.conf` to a real locale such as
  `en_US.utf8`.

The regression tests are unaffected: `pg_regress` and the TAP framework
clear `LANGUAGE` and force `LC_MESSAGES=C`.

## Regenerating

The tools need Python 3 and `polib`:

```
python3 -m venv .venv
.venv/bin/pip install -r tools/requirements.txt
.venv/bin/python -m unittest discover -s tools/tests -t tools
```

- `tools/piglatin.py TEMPLATE.pot OUTPUT.po CATALOG` regenerates Pig Latin.
- `tools/make_chunks.py`, `tools/check_chunk.py` and `tools/merge.py` are the
  split / validate / reassemble steps used for the machine translations;
  `docs/translate-prompt.md` is what each translator agent was given.
- `tools/smoke.sh LANGCODE` starts a scratch server from a meson
  `tmp_install` and shows a few client and server messages in that
  language.  Point it at your tree with `PGWT=/path/to/postgresql`.

Templates come from autoconf's `make init-po` in a VPATH build, because the
meson `-pot` targets need `POTFILES`, which the PostgreSQL po directories
don't have.  The docs still contain the absolute paths from the machine
this was built on; adjust to taste.

## License

MIT, see `LICENSE`.  The message text itself comes from PostgreSQL, which
is under the PostgreSQL License.

Enjoy!
