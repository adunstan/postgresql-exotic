# Translator instructions (one chunk)

You are translating PostgreSQL message catalog entries into LANGUAGE
(code LANGCODE).  This is a local demo, but the output is compiled by
msgfmt and shown to users, so the mechanical rules below are strict.

Inputs:
- Chunk: CHUNK (JSON, `{"entries": [{"id", "msgid", optional "msgid_plural"}]}`)
- Glossary: /home/andrew/pgl/pg_head/results/nls-demo/glossary.tsv
  (columns: english, esperanto, klingon, note).  Read it first.  Do not
  edit it; other translators are running in parallel.

Output: write OUT with the Write tool, exactly this shape:

```json
{"translations": [
 {"id": 17, "msgstr": "..."},
 {"id": 18, "msgstr_plural": ["singular ...", "plural ..."]}
]}
```

Every id in the chunk must appear once.  Entries with `msgid_plural` need
`msgstr_plural`; all others need `msgstr`.  Never leave a translation
empty.  JSON escaping is the same as in the chunk file: `\"` for a
double quote, `\n` for a newline, `\\` for a backslash (so the psql
command `\d` is written `"\\d"`).

Then validate:

```
/home/andrew/pgl/pg_head/results/nls-demo/.venv/bin/python /home/andrew/pgl/pg_head/results/nls-demo/check_chunk.py LANGCODE CHUNK
```

Fix every problem it reports (edit OUT) and rerun until it prints `OK`.
Your final reply is just `OK CHUNK` or a one-line description of what
you could not fix.

## Rules

1. Copy every printf conversion spec exactly, in the same order and the
   same number of times: `%s %d %u %lu %lld %m %% %c %x %5.2f %*s
   %<PRId64> %<PRIu64>` and so on.  Do not add or remove a `%`.
2. Copy unchanged: anything inside double quotes (`"%s"`, `"work_mem"`);
   SQL keywords and other ALL-CAPS words; identifiers containing `_` or
   digits; command-line options (`-c`, `--verbose`); psql backslash
   commands (`\copy`); file paths; product and program names
   (PostgreSQL, psql, libpq, pg_dump, ...); configuration parameter
   names; SQL data type names (`integer`, `smallint`, `bigint`, `real`,
   `double precision`, `numeric`, `text`, `boolean`, `timestamp with
   time zone`, `jsonb`, ...) when they name the type;
   function names such as `pg_backup_start()`; SQLSTATE codes;
   URLs; email addresses.
   Exception: message severity and field labels ARE translated even
   though they are in capitals, because users see them on every error.
   These are msgids consisting only of one of DEBUG, LOG, INFO, NOTICE,
   WARNING, ERROR, FATAL, PANIC, DETAIL, HINT, QUERY, CONTEXT, LOCATION,
   STATEMENT, LINE, SCHEMA NAME, TABLE NAME, COLUMN NAME, DATATYPE
   NAME, CONSTRAINT NAME, plus optional punctuation, whitespace and
   conversion specs (e.g. `"ERROR"`, `"DETAIL:  "`, `"LINE %d: "`).
   Keep the punctuation and spacing.  Esperanto: translate in
   capitals (`ERARO`, `AVERTO`, `AVIZO`, `DETALO:  `, `SUGESTO:`,
   `KUNTEKSTO:`, `LINIO %d: `).  Klingon: do NOT capitalise, because
   case is part of Klingon spelling (q and Q are different letters);
   use normal Okrand case (`Qagh`, `ghuH`, `QIn`, `ngoD:  `, `qeS:`,
   `ghu':`, `tlhegh %d: `).
3. Preserve leading and trailing whitespace and newlines exactly, and
   keep the same number of internal newlines.
4. psql help text (lines such as `"  \\d[S+]   NAME          describe
   table, view, sequence, or index\n"`): keep everything before the
   description, including the column padding, unchanged; translate only
   the description.  Keep the indentation of continuation lines.
5. Plurals: `[singular form, plural form]`, each with the same
   conversion specs as its English counterpart.
6. If a message has no translatable words (for example `"%s: %s"`), copy
   it unchanged.
7. Use glossary terms consistently.  For a term not in the glossary,
   pick one rendering and use it consistently within your chunk.
8. Keep PostgreSQL message style: terse, no capital first letter and no
   trailing period, unless the English has them.

## Esperanto (eo)

Standard grammar, including the accusative `-n`.  Use real UTF-8
letters ĉ ĝ ĥ ĵ ŝ ŭ, never the x-system.  Example:

- `could not open file "%s": %m` → `ne povis malfermi dosieron "%s": %m`

## Klingon (tlh)

Okrand Latin orthography with exact case: lowercase except `D H I Q S`
and the `'` letter (`tlhIngan Hol`, `Qagh`, `De'`).  Not pIqaD.  Object
-verb-subject order; no articles.  Useful verb suffixes: `-laH` can,
`-be'` not, `-pu'` perfective, `-nIS` need, `-lu'` indefinite subject,
`-moH` cause.  Digits stay digits.  Example:

- `could not open file "%s": %m` → `ta "%s" poSmoHlaHbe'pu'lu': %m`
- `relation "%s" does not exist` → `Dol "%s" tu'lu'be'`
