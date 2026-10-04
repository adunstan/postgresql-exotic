"""Shared helpers for the NLS demo catalog tools."""
import datetime
import re
import subprocess

import polib

LANG_NAMES = {
    "en@piglatin": "Pig Latin",
    "eo": "Esperanto",
    "tlh": "Klingon",
}
PLURAL_FORMS = "nplurals=2; plural=(n != 1);"


def load_pot(path):
    """Return (pot, entries) for a .pot file, skipping obsolete entries."""
    pot = polib.pofile(path)
    return pot, [e for e in pot if not e.obsolete]


def new_po(lang, catalog, pot_creation_date=""):
    """Return an empty POFile with a header suitable for msgfmt -c."""
    now = datetime.datetime.now().astimezone().strftime("%Y-%m-%d %H:%M%z")
    po = polib.POFile(wrapwidth=79)
    po.header = "%s message translation file for %s (local demo)" % (
        LANG_NAMES[lang], catalog)
    po.metadata = {
        "Project-Id-Version": "PostgreSQL 20",
        "Report-Msgid-Bugs-To": "pgsql-bugs@lists.postgresql.org",
        "POT-Creation-Date": pot_creation_date or now,
        "PO-Revision-Date": now,
        "Last-Translator": "Andrew Dunstan <andrew@dunslane.net>",
        "Language-Team": "%s (demo)" % LANG_NAMES[lang],
        "Language": lang,
        "MIME-Version": "1.0",
        "Content-Type": "text/plain; charset=UTF-8",
        "Content-Transfer-Encoding": "8bit",
        "Plural-Forms": PLURAL_FORMS,
    }
    return po


def copy_entry(src, msgstr="", msgstr_plural=None):
    """Return a new entry with src's msgid/flags/references and the given
    translation."""
    entry = polib.POEntry(
        msgid=src.msgid,
        msgid_plural=src.msgid_plural,
        msgctxt=src.msgctxt,
        occurrences=src.occurrences,
        flags=[f for f in src.flags if f != "fuzzy"],
        comment=src.comment)
    if src.msgid_plural:
        entry.msgstr_plural = msgstr_plural or {0: "", 1: ""}
    else:
        entry.msgstr = msgstr
    return entry


def blank_entry(entry):
    if entry.msgid_plural:
        entry.msgstr_plural = {0: "", 1: ""}
    else:
        entry.msgstr = ""


def bad_msgids(path):
    """Run msgfmt -c on the file at path and return the set of msgids whose
    entries it rejects.  Raises RuntimeError for errors outside any entry
    (e.g. in the header)."""
    result = subprocess.run(["msgfmt", "-c", "-o", "/dev/null", path],
                            capture_output=True, text=True)
    prefix = re.compile(r"^" + re.escape(path) + r":(\d+): ")
    lines = sorted({int(m.group(1)) for m in
                    (prefix.match(l) for l in result.stderr.splitlines())
                    if m})
    if result.returncode != 0 and not lines:
        raise RuntimeError("msgfmt failed on %s:\n%s" % (path, result.stderr))
    starts = sorted((e.linenum, e.msgid) for e in polib.pofile(path)
                    if e.msgid)
    bad = set()
    for line in lines:
        owners = [msgid for start, msgid in starts if start <= line]
        if not owners:
            raise RuntimeError("msgfmt error outside any entry in %s:\n%s"
                               % (path, result.stderr))
        bad.add(owners[-1])
    return bad


def save_checked(po, path):
    """Save po to path, blank every entry msgfmt -c rejects, save again, and
    return the sorted list of blanked msgids."""
    po.save(path)
    bad = bad_msgids(path)
    if not bad:
        return []
    for entry in po:
        if entry.msgid in bad:
            blank_entry(entry)
    po.save(path)
    still_bad = bad_msgids(path)
    if still_bad:
        raise RuntimeError("entries still rejected after blanking: %r"
                           % sorted(still_bad))
    return sorted(bad)
