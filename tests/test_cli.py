import contextlib
import io
import os
import tempfile
import unittest

from reflow.cli import main


class InPlaceTests(unittest.TestCase):
    def setUp(self):
        fd, self.path = tempfile.mkstemp()
        os.close(fd)

    def tearDown(self):
        os.remove(self.path)

    def _write(self, text):
        with open(self.path, "w", encoding="utf-8") as f:
            f.write(text)

    def _read(self):
        with open(self.path, "r", encoding="utf-8") as f:
            return f.read()

    def test_rewrites_file_to_requested_width(self):
        self._write("word " * 20)
        with contextlib.redirect_stdout(io.StringIO()) as out:
            status = main(["-i", "-w", "20", self.path])
        self.assertEqual(status, 0)
        self.assertEqual(out.getvalue(), "")
        for line in self._read().splitlines():
            self.assertLessEqual(len(line), 20)

    def test_prints_nothing_to_stdout(self):
        self._write("First.\n\nSecond.")
        with contextlib.redirect_stdout(io.StringIO()) as out:
            main(["--in-place", self.path])
        self.assertEqual(out.getvalue(), "")

    def test_rejects_stdin_placeholder(self):
        with self.assertRaises(SystemExit):
            main(["-i", "-"])

    def test_rejects_no_files(self):
        with self.assertRaises(SystemExit):
            main(["-i"])


if __name__ == "__main__":
    unittest.main()
