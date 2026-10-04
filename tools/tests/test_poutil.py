import os
import tempfile
import unittest

import polib

import poutil


class SaveCheckedTest(unittest.TestCase):
    def make_po(self):
        po = poutil.new_po("eo", "test")
        po.append(polib.POEntry(msgid="file \"%s\" is missing",
                                msgstr="dosiero \"%s\" mankas",
                                flags=["c-format"]))
        po.append(polib.POEntry(msgid="%d rows lost",
                                msgstr="%s vicoj perditaj",
                                flags=["c-format"]))
        po.append(polib.POEntry(msgid="bye\n", msgstr="ĝis"))
        bad = polib.POEntry(msgid="(%lu row)", msgid_plural="(%lu rows)",
                            flags=["c-format"])
        bad.msgstr_plural = {0: "(%lu vico)", 1: "(vicoj)"}
        po.append(bad)
        return po

    def test_blanks_only_rejected_entries(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "eo.po")
            blanked = poutil.save_checked(self.make_po(), path)
            self.assertEqual(blanked,
                             ["%d rows lost", "(%lu row)", "bye\n"])
            saved = {e.msgid: e for e in polib.pofile(path)}
            self.assertEqual(saved["file \"%s\" is missing"].msgstr,
                             "dosiero \"%s\" mankas")
            self.assertEqual(saved["%d rows lost"].msgstr, "")
            self.assertEqual(saved["bye\n"].msgstr, "")
            self.assertEqual(saved["(%lu row)"].msgstr_plural,
                             {0: "", 1: ""})


if __name__ == "__main__":
    unittest.main()
