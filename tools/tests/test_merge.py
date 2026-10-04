import json
import os
import subprocess
import sys
import tempfile
import unittest

import polib

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

POT = r'''msgid ""
msgstr ""
"Content-Type: text/plain; charset=UTF-8\n"

#, c-format
msgid "table \"%s\" not found"
msgstr ""

msgid "done\n"
msgstr ""

#, c-format
msgid "(%lu row)"
msgid_plural "(%lu rows)"
msgstr[0] ""
msgstr[1] ""
'''


def run(script, *args):
    return subprocess.run([sys.executable, os.path.join(HERE, script)]
                          + list(args), capture_output=True, text=True)


def write_out(path, translations):
    with open(path, "w", encoding="utf-8") as f:
        json.dump({"translations": translations}, f, ensure_ascii=False)


class MergeTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = self.tmp.name
        self.pot = os.path.join(self.dir, "t.pot")
        with open(self.pot, "w") as f:
            f.write(POT)
        self.work = os.path.join(self.dir, "work")
        self.po = os.path.join(self.dir, "eo.po")
        r = run("make_chunks.py", self.pot, self.work, "2")
        self.assertEqual(r.returncode, 0, r.stderr)

    def tearDown(self):
        self.tmp.cleanup()

    def test_check_chunk_and_merge_with_retry(self):
        chunk0 = os.path.join(self.work, "chunk-000.json")
        write_out(os.path.join(self.work, "chunk-000.out.json"), [
            {"id": 0, "msgstr": "tabelo \"%s\" ne trovita"},
            {"id": 1, "msgstr": "farita"}])          # lost trailing \n
        r = run("check_chunk.py", "eo", chunk0)
        self.assertEqual(r.returncode, 1)
        self.assertIn("id 1 rejected", r.stdout)

        # chunk-001 has no output yet: merge leaves id 2 blank, and
        # ids 1 and 2 go to retry.json.
        r = run("merge.py", "eo", "t", self.pot, self.work, self.po)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("1 translated, 1 missing, 1 blanked", r.stdout)
        with open(os.path.join(self.work, "retry.json")) as f:
            self.assertEqual([e["id"] for e in json.load(f)["entries"]],
                             [1, 2])

        write_out(os.path.join(self.work, "retry.out.json"), [
            {"id": 1, "msgstr": "farita\n"},
            {"id": 2, "msgstr_plural": ["(%lu vico)", "(%lu vicoj)"]}])
        r = run("check_chunk.py", "eo",
                os.path.join(self.work, "retry.json"))
        self.assertEqual(r.stdout.strip(), "OK")
        r = run("merge.py", "eo", "t", self.pot, self.work, self.po)
        self.assertIn("3 translated, 0 missing, 0 blanked", r.stdout)
        saved = {e.msgid: e for e in polib.pofile(self.po)}
        self.assertEqual(saved["done\n"].msgstr, "farita\n")
        self.assertEqual(saved["(%lu row)"].msgstr_plural,
                         {0: "(%lu vico)", 1: "(%lu vicoj)"})
        self.assertEqual(polib.pofile(self.po).metadata["Language"], "eo")


if __name__ == "__main__":
    unittest.main()
