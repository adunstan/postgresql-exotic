import unittest

from piglatin import pig_word, translate


class PigWordTest(unittest.TestCase):
    def test_consonant_cluster(self):
        self.assertEqual(pig_word("table"), "abletay")
        self.assertEqual(pig_word("string"), "ingstray")

    def test_vowel_initial(self):
        self.assertEqual(pig_word("able"), "ableway")

    def test_qu_and_y(self):
        self.assertEqual(pig_word("query"), "eryquay")
        self.assertEqual(pig_word("squeal"), "ealsquay")
        self.assertEqual(pig_word("yellow"), "ellowyay")
        self.assertEqual(pig_word("rhythm"), "ythmrhay")

    def test_capitalization(self):
        self.assertEqual(pig_word("Table"), "Abletay")

    def test_unchanged(self):
        for w in ("the", "The", "a", "is", "not", "I", "psql"):
            self.assertEqual(pig_word(w), w)


class TranslateTest(unittest.TestCase):
    def test_backend_messages(self):
        self.assertEqual(translate("division by zero"),
                         "ivisionday by erozay")
        self.assertEqual(translate('relation "%s" does not exist'),
                         'elationray "%s" oesday not existway')
        self.assertEqual(translate("block number out of range: %<PRId64>"),
                         "ockblay umbernay outway of angeray: %<PRId64>")

    def test_protected_tokens(self):
        self.assertEqual(
            translate("could not open file \"%s\": %m"),
            "ouldcay not openway ilefay \"%s\": %m")
        self.assertEqual(translate("invalid value for parameter "
                                   "\"work_mem\": %d"),
                         "invalidway aluevay for arameterpay "
                         "\"work_mem\": %d")
        self.assertEqual(translate("SELECT failed in pg_dump --verbose -v"),
                         "SELECT ailedfay in pg_dump --verbose -v")
        self.assertEqual(translate("use \\copy for /tmp/foo and/or WAL"),
                         "useway \\copy for /tmp/foo and/or WAL")
        self.assertEqual(
            translate("  -?, --help[=options]     show this help, "
                      "then exit\n"),
            "  -?, --help[=options]     owshay isthay elphay, "
            "enthay exitway\n")
        self.assertEqual(translate("use --help=commands for more"),
                         "useway --help=commands for oremay")

    def test_whitespace_and_hyphens(self):
        self.assertEqual(translate("psql is the PostgreSQL interactive "
                                   "terminal.\n\n"),
                         "psql is the PostgreSQL interactiveway "
                         "erminaltay.\n\n")
        self.assertEqual(translate("  read-only %5.2f%%\n"),
                         "  eadray-onlyway %5.2f%%\n")


if __name__ == "__main__":
    unittest.main()
