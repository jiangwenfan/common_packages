import unittest

from jwf_common_python.language_utils import (
    extract_chapter,
    extract_words,
    filter_words,
    format_words,
    get_chapter_words,
    group_words_by_length,
    is_title_case_word,
    parse_urls,
    sort_words_by_length,
    word_frequencies,
)


class TextTests(unittest.TestCase):
    def test_extraction_keeps_legacy_ascii_rules_and_repetition(self):
        self.assertEqual(
            extract_words("Dog, dog! 42 test-case don't 中文"),
            ["Dog", "dog", "test", "case", "don", "t"],
        )
        self.assertEqual(
            extract_words(iter(["One two", "Three"])), ["One", "two", "Three"]
        )
        self.assertEqual(extract_words(""), [])

    def test_filter_combines_all_exclusions_preserving_order_and_input(self):
        words = [" Apple ", "a", "banana", "BANANA", "pear", "known", ""]
        original = words.copy()
        self.assertEqual(
            filter_words(
                words,
                exclude_words=iter(["apple"]),
                known_words=["KNOWN"],
                min_length=2,
                unique=True,
            ),
            ["banana", "pear"],
        )
        self.assertEqual(words, original)
        self.assertEqual(
            filter_words(
                ["Apple", "apple"], exclude_words=["apple"], case_sensitive=True
            ),
            ["Apple"],
        )
        self.assertEqual(filter_words(["A", "a"], unique=False), ["A", "a"])

    def test_chapter_skips_toc_and_uses_next_end_title_after_start(self):
        text = "One\nTwo\n目录内容\n One \nHello world!\n Two \nWrong text"
        self.assertEqual(extract_chapter(text, "One", "Two"), "Hello world!")
        self.assertEqual(
            get_chapter_words(text, "One", "Two", known_words=["hello"]), ["world"]
        )
        self.assertEqual(extract_chapter(text, "One", "Two", occurrence=0), "")

    def test_chapter_supports_single_headings_and_last_chapter(self):
        text = "Introduction\r\nHeader\r\nbody text\r\nNext\r\nlast body"
        self.assertEqual(extract_chapter(text, "Header", "Next"), "body text")
        self.assertEqual(extract_chapter(text, "Next"), "last body")
        self.assertEqual(extract_chapter("Header\nNext", "Header", "Next"), "")

    def test_chapter_boundaries_are_exact_and_invalid_ranges_fail(self):
        for args in (
            ("Header in prose", "Header", None),
            ("End\nStart\nbody", "Start", "End"),
        ):
            with self.subTest(args=args), self.assertRaises(ValueError):
                extract_chapter(*args)
        with self.assertRaises(ValueError):
            extract_chapter("Header\nbody", "Header", occurrence=1)
        with self.assertRaises(ValueError):
            extract_chapter("Header", " ")

    def test_frequency_order_top_n_and_text_output(self):
        words = ["Pear", "apple", "pear", "banana", "apple", " "]
        self.assertEqual(
            word_frequencies(words), [("pear", 2), ("apple", 2), ("banana", 1)]
        )
        self.assertEqual(format_words(iter(words), top_n=2), "pear\napple")
        self.assertEqual(word_frequencies(words, top_n=0), [])
        self.assertEqual(
            word_frequencies(["Pear", "pear"], case_sensitive=True),
            [("Pear", 1), ("pear", 1)],
        )

    def test_length_operations_do_not_modify_input_and_keep_equal_length_order(self):
        words = ["to", "banana", "an", "a", "to"]
        self.assertEqual(
            group_words_by_length(words),
            {2: ["to", "an", "to"], 6: ["banana"], 1: ["a"]},
        )
        self.assertEqual(sort_words_by_length(words), ["banana", "to", "an", "to", "a"])
        self.assertEqual(
            sort_words_by_length(words, descending=False),
            ["a", "to", "an", "to", "banana"],
        )
        self.assertEqual(words, ["to", "banana", "an", "a", "to"])

    def test_title_case_rule(self):
        self.assertTrue(is_title_case_word("Dog"))
        for value in ("dog", "DOG", "DoG", "A", "Dog-Dog", "Dog!", None):
            self.assertFalse(is_title_case_word(value))

    def test_url_parsing_deduplicates_and_ignores_blank_lines_and_comments(self):
        self.assertEqual(
            parse_urls(
                "# sources\nhttps://example.com/a\n \nhttp://example.com/b\nhttps://example.com/a"
            ),
            ["https://example.com/a", "http://example.com/b"],
        )
        self.assertEqual(
            parse_urls(iter(["https://example.com/a"])), ["https://example.com/a"]
        )
        for value in (
            "ftp://example.com",
            "https:///missing",
            "https://example.com/a b",
            "http://example.com:bad",
        ):
            with self.subTest(value=value), self.assertRaises(ValueError):
                parse_urls(value)

    def test_invalid_word_lists_and_parameters_are_reported(self):
        for words in ("hello", [None], [1]):
            with self.subTest(words=words), self.assertRaises(TypeError):
                filter_words(words)
        with self.assertRaises(TypeError):
            filter_words([], exclude_words="hello")
        for value in (0, -1, True):
            with self.assertRaises(ValueError):
                filter_words([], min_length=value)
        with self.assertRaises(ValueError):
            word_frequencies([], top_n=-1)


if __name__ == "__main__":
    unittest.main()
