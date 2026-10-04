"""Chunk and translation-output files exchanged with translators.

A chunk (chunk-NNN.json, retry.json) is {"entries": [{"id", "msgid",
optional "msgid_plural"}]}, where id is the entry's index in the template.
Its output (chunk-NNN.out.json, retry.out.json) is {"translations": [{"id",
"msgstr"} or {"id", "msgstr_plural": [singular, plural]}]}.
"""
import glob
import json
import os


class TranslationError(Exception):
    pass


def entry_dict(index, src):
    d = {"id": index, "msgid": src.msgid}
    if src.msgid_plural:
        d["msgid_plural"] = src.msgid_plural
    return d


def write_chunk(path, items):
    with open(path, "w", encoding="utf-8") as f:
        json.dump({"entries": items}, f, ensure_ascii=False, indent=1)
        f.write("\n")


def read_chunk(path):
    with open(path, encoding="utf-8") as f:
        return {e["id"]: e for e in json.load(f)["entries"]}


def out_path(chunk_path):
    return chunk_path[:-len(".json")] + ".out.json"


def chunk_paths(workdir):
    """Chunks that have output, in apply order: chunk-NNN.json, then
    retry.json."""
    paths = sorted(glob.glob(os.path.join(workdir, "chunk-[0-9][0-9][0-9].json")))
    paths.append(os.path.join(workdir, "retry.json"))
    return [p for p in paths if os.path.exists(out_path(p))]


def read_out(path, expected):
    """Read one output file and return {id: translation}, where a
    translation is a str or a [singular, plural] list.  expected maps id to
    the chunk entry; every expected id must be present with the right
    shape."""
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
    except (OSError, ValueError) as e:
        raise TranslationError("%s: %s" % (path, e))
    result = {}
    problems = []
    for t in data.get("translations", []):
        i = t.get("id")
        if i not in expected:
            problems.append("unexpected id %r" % i)
        elif "msgid_plural" in expected[i]:
            p = t.get("msgstr_plural")
            if not (isinstance(p, list) and len(p) == 2
                    and all(isinstance(s, str) for s in p)):
                problems.append("id %d: need msgstr_plural [str, str]" % i)
            else:
                result[i] = p
        elif not isinstance(t.get("msgstr"), str):
            problems.append("id %d: need msgstr string" % i)
        else:
            result[i] = t["msgstr"]
    missing = sorted(set(expected) - set(result))
    if missing:
        problems.append("missing ids: %s" % missing)
    if problems:
        raise TranslationError("%s: %s" % (path, "; ".join(problems)))
    return result
