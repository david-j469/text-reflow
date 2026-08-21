import unittest

from reflow.core import normalize_paragraphs, wrap_text


class NormalizeParagraphsTests(unittest.TestCase):
    def test_empty_input(self):
        self.assertEqual(normalize_paragraphs(""), [])
        self.assertEqual(normalize_paragraphs("   \n\n  "), [])

    def test_single_paragraph_collapses_internal_newlines(self):
        text = "This is a line\nthat was wrapped\nacross three lines."
        self.assertEqual(
            normalize_paragraphs(text),
            ["This is a line that was wrapped across three lines."],
        )

    def test_blank_line_separates_paragraphs(self):
        text = "First paragraph\nstill going.\n\nSecond paragraph."
        self.assertEqual(
            normalize_paragraphs(text),
            ["First paragraph still going.", "Second paragraph."],
        )

    def test_multiple_blank_lines_treated_as_one_break(self):
        text = "One.\n\n\n\nTwo."
        self.assertEqual(normalize_paragraphs(text), ["One.", "Two."])

    def test_blank_line_with_trailing_whitespace_still_splits(self):
        text = "One.\n   \nTwo."
        self.assertEqual(normalize_paragraphs(text), ["One.", "Two."])

    def test_crlf_and_cr_line_endings_normalized(self):
        text = "One.\r\n\r\nTwo.\rstill two."
        self.assertEqual(normalize_paragraphs(text), ["One.", "Two. still two."])

    def test_extra_whitespace_within_lines_collapsed(self):
        text = "Too    many   spaces\nand\ttabs."
        self.assertEqual(normalize_paragraphs(text), ["Too many spaces and tabs."])

    def test_leading_and_trailing_blank_lines_ignored(self):
        text = "\n\n  Only paragraph.  \n\n"
        self.assertEqual(normalize_paragraphs(text), ["Only paragraph."])


class WrapTextTests(unittest.TestCase):
    def test_rewraps_to_requested_width(self):
        text = "word " * 20
        result = wrap_text(text, width=20)
        for line in result.splitlines():
            self.assertLessEqual(len(line), 20)

    def test_paragraphs_separated_by_blank_line(self):
        text = "First paragraph.\n\nSecond paragraph."
        result = wrap_text(text, width=72)
        self.assertEqual(result, "First paragraph.\n\nSecond paragraph.")

    def test_empty_input_produces_empty_output(self):
        self.assertEqual(wrap_text(""), "")

    def test_does_not_break_long_words(self):
        text = "a " + "x" * 50 + " b"
        result = wrap_text(text, width=10)
        self.assertIn("x" * 50, result)

    def test_does_not_break_on_hyphens(self):
        text = "a well-established-but-long compound word here"
        result = wrap_text(text, width=15)
        self.assertIn("well-established-but-long", result)


class ListHandlingTests(unittest.TestCase):
    def test_normalize_keeps_bullet_items_separate(self):
        text = "- first item\nstill first item\n- second item"
        self.assertEqual(
            normalize_paragraphs(text),
            [[("- ", "first item still first item"), ("- ", "second item")]],
        )

    def test_normalize_keeps_numbered_items_separate(self):
        text = "1. first\n2. second\n3) third"
        self.assertEqual(
            normalize_paragraphs(text),
            [[("1. ", "first"), ("2. ", "second"), ("3) ", "third")]],
        )

    def test_normalize_splits_intro_prose_from_list(self):
        text = "Shopping list:\n- apples\n- bananas"
        self.assertEqual(
            normalize_paragraphs(text),
            ["Shopping list:", [("- ", "apples"), ("- ", "bananas")]],
        )

    def test_normalize_does_not_treat_decimal_as_list_marker(self):
        text = "3.14 is pi\nnot a list item."
        self.assertEqual(normalize_paragraphs(text), ["3.14 is pi not a list item."])

    def test_wrap_keeps_bullets_on_separate_lines(self):
        text = "- one\n- two\n- three"
        result = wrap_text(text, width=72)
        self.assertEqual(result, "- one\n- two\n- three")

    def test_wrap_uses_hanging_indent_for_long_items(self):
        text = "- " + "word " * 10
        result = wrap_text(text, width=20)
        lines = result.splitlines()
        self.assertTrue(lines[0].startswith("- "))
        for line in lines[1:]:
            self.assertTrue(line.startswith("  "))

    def test_wrap_separates_list_from_surrounding_paragraphs(self):
        text = "Intro.\n\n- one\n- two\n\nOutro."
        result = wrap_text(text, width=72)
        self.assertEqual(result, "Intro.\n\n- one\n- two\n\nOutro.")


if __name__ == "__main__":
    unittest.main()
