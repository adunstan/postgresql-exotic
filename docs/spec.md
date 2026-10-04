# NLS demo catalogs: Pig Latin, Esperanto, Klingon — design

Date: 2026-10-04
Status: implemented on branch nls-demo (see progress.md)

## Goal

Local demo (not for upstream/pgtranslation) of three extra message
languages for PostgreSQL:

| Language   | Code          | Method                                   |
|------------|---------------|------------------------------------------|
| Pig Latin  | `en@piglatin` | deterministic script                     |
| Esperanto  | `eo`          | glossary-driven translation (subagents)  |
| Klingon    | `tlh`         | glossary-driven translation, Okrand Latin orthography |

`en@piglatin` follows the GNU gettext precedent of synthetic English
variants (`en@quot`, `en@boldquot`).

Catalogs in scope: `src/backend/po` (postgres), `src/bin/psql/po`
(psql), `src/interfaces/libpq/po` (libpq). About 8.45k messages per
language.

Out of scope: other catalogs, upstream submission, new glibc/ICU
locales.

## Layout

- Local branch `nls-demo` in a separate git worktree (main checkout
  has many untracked files; leave it alone).
- In-tree changes only: new `en@piglatin.po`, `eo.po`, `tlh.po` in the
  three po directories, and the three codes appended to each `LINGUAS`.
- Tooling and working files in `results/nls-demo/` (outside the patch):
  - `piglatin.py` — generator
  - `glossary.tsv` — English / Esperanto / Klingon term list
  - `chunk.py` / `merge.py` — split .pot into JSON chunks for
    translation, merge results back into .po
  - this spec and the implementation plan

## Source msgids

Generate fresh templates from the cassert build with meson's gettext
targets (`postgres-19-pot`, `psql-19-pot`, `libpq-19-pot`) rather than
reusing an existing translation's msgids, so the catalogs match current
master. msgctxt, plural forms, and c-format flags are carried through.

## Pig Latin rules

Applied to each maximal run of ASCII letters that is not protected.

- Vowel-initial word: append `way` (`able` -> `ableway`).
- Consonant-initial word: move leading consonant cluster to the end
  and append `ay` (`table` -> `abletay`, `string` -> `ingstray`).
  `qu` is part of the cluster (`query` -> `eryquay`); leading `y` is a
  consonant.
- Case preserved: Capitalized stays Capitalized (`Table` -> `Abletay`).
- Plural entries: both `msgstr[0]` and `msgstr[1]` generated from their
  respective msgids.

Left unchanged:

- Stopwords — extremely common short function words:
  `a an the is are was be been of to in on at by for as or and it its
  if no not` (case-insensitive). The list lives in one constant in
  `piglatin.py` and can be tuned.
- Single letters.
- printf conversion specs (`%s`, `%1$s`, `%-*lld`, `%m`, `%%`, ...).
- ALL-CAPS words (SQL keywords, `NULL`, `SQLSTATE`).
- Identifiers containing `_` or digits (GUC names, functions).
- Command-line options (`--foo`, `-x`), psql backslash commands (`\d`),
  paths, anything inside double quotes (`"..."`, `\"...\"`).
- Escape sequences (`\n`, `\t`) and leading/trailing whitespace, so
  psql help column layout and line structure are preserved.

## Esperanto and Klingon

1. Build `glossary.tsv` first: ~150 core database terms (table, index,
   column, relation, transaction, tuple, role, schema, constraint,
   function, server, connection, file, permission denied, ...).
   Klingon coinages for missing vocabulary are recorded there so they
   are used consistently.
2. Split each .pot into chunks of ~250 entries (JSON: msgctxt, msgid,
   msgid_plural, flags). Dispatch chunks to parallel subagents with the
   glossary and the same do-not-translate rules as the Pig Latin
   generator (format specs, quoted identifiers, SQL keywords, GUC
   names, options, backslash commands, escapes, whitespace).
3. Klingon uses Okrand Latin orthography (`tlhIngan Hol`), not pIqaD.
4. Files are UTF-8 (`Content-Type: text/plain; charset=UTF-8`);
   Esperanto uses ĉ ĝ ĥ ĵ ŝ ŭ.
5. Plural-Forms: `nplurals=2; plural=(n != 1);` for all three.

## Validation

- Every .po must pass `msgfmt --check` (format specifier agreement,
  header). Failing entries are re-translated once; if still failing,
  msgstr is left empty so that message falls back to English.
- Build with `builddir-cassert` (nls currently `auto`; confirm gettext
  is found, otherwise reconfigure with `-Dnls=enabled`), install to
  tmp_install.
- Runtime checks, for each language, with
  `LANGUAGE=<code> LC_MESSAGES=en_US.utf8`:
  - psql: `\?` output and an invalid backslash command error
  - libpq: connection failure to a nonexistent socket
  - backend: server started with `LANGUAGE=<code>` and
    `lc_messages='en_US.utf8'`; `SELECT 1/0` and a missing-table query
    return translated errors
- Regression suite run on the cassert build to confirm nothing else
  changed.

## Usage (end result)

```
LANGUAGE=tlh LC_MESSAGES=en_US.utf8 psql ...
LANGUAGE=eo pg_ctl -D data start      # with lc_messages='en_US.utf8'
```
