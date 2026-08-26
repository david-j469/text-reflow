import contextlib
import io
import os
import tempfile
import unittest

from reflow.cli import load_config_width, main


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


class ConfigWidthTests(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.mkdtemp()

    def tearDown(self):
        for name in os.listdir(self.dir):
            os.remove(os.path.join(self.dir, name))
        os.rmdir(self.dir)

    def _write_config(self, contents):
        with open(os.path.join(self.dir, ".reflowrc"), "w", encoding="utf-8") as f:
            f.write(contents)

    def test_missing_file_returns_none(self):
        self.assertIsNone(load_config_width(self.dir))

    def test_reads_width_setting(self):
        self._write_config("width = 60\n")
        self.assertEqual(load_config_width(self.dir), 60)

    def test_ignores_comments_and_blank_lines(self):
        self._write_config("# a comment\n\nwidth = 50\n")
        self.assertEqual(load_config_width(self.dir), 50)

    def test_unrecognized_keys_are_ignored(self):
        self._write_config("color = blue\n")
        self.assertIsNone(load_config_width(self.dir))

    def test_non_integer_width_returns_none(self):
        self._write_config("width = wide\n")
        self.assertIsNone(load_config_width(self.dir))


class ConfigPrecedenceTests(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.mkdtemp()
        with open(os.path.join(self.dir, ".reflowrc"), "w", encoding="utf-8") as f:
            f.write("width = 15\n")
        self.prev_cwd = os.getcwd()
        os.chdir(self.dir)

    def tearDown(self):
        os.chdir(self.prev_cwd)
        for name in os.listdir(self.dir):
            os.remove(os.path.join(self.dir, name))
        os.rmdir(self.dir)

    def test_config_width_used_when_flag_omitted(self):
        input_path = os.path.join(self.dir, "input.txt")
        with open(input_path, "w", encoding="utf-8") as f:
            f.write("word " * 20)
        with contextlib.redirect_stdout(io.StringIO()) as out:
            main([input_path])
        for line in out.getvalue().splitlines():
            self.assertLessEqual(len(line), 15)

    def test_explicit_flag_overrides_config(self):
        input_path = os.path.join(self.dir, "input.txt")
        with open(input_path, "w", encoding="utf-8") as f:
            f.write("word " * 20)
        with contextlib.redirect_stdout(io.StringIO()) as out:
            main(["-w", "72", input_path])
        self.assertEqual(out.getvalue().splitlines()[0], ("word " * 14).strip())


if __name__ == "__main__":
    unittest.main()
