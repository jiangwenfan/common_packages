import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from jwf_common_python.language_utils import (
    filter_words,
    generate_file_menu,
    read_urls,
    read_word_lists,
    read_words,
)


class FileTests(unittest.TestCase):
    def setUp(self):
        folder = tempfile.TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        self.root = Path(folder.name)

    def test_explicit_file_paths_and_multiple_word_lists(self):
        first = self.root / "first.txt"
        second = self.root / "second.txt"
        first.write_text("Apple\npear\n", encoding="utf-8")
        second.write_text("banana\nAPPLE\n", encoding="utf-8")
        self.assertEqual(read_words(first, exclude_words=["apple"]), ["pear"])
        known = read_word_lists([first, second])
        self.assertEqual(known, ["Apple", "pear", "banana"])
        self.assertEqual(
            filter_words(["APPLE", "PEAR", "BANANA", "new"], known_words=known), ["new"]
        )
        self.assertEqual(first.read_text(encoding="utf-8"), "Apple\npear\n")

    def test_read_urls_uses_the_supplied_file(self):
        path = self.root / "custom_sources.txt"
        path.write_text(
            "https://example.com/one\n# ignored\nhttps://example.com/two",
            encoding="utf-8",
        )
        self.assertEqual(
            read_urls(path), ["https://example.com/one", "https://example.com/two"]
        )

    def test_menu_preserves_relative_paths_for_duplicate_file_names(self):
        for name in ("wanglu_first", "wanglu_second", "other"):
            (self.root / name).mkdir()
            (self.root / name / "same.txt").write_text("words", encoding="utf-8")
        (self.root / "top.txt").write_text("top", encoding="utf-8")
        (self.root / "image.png").write_bytes(b"")
        paths, message = generate_file_menu(self.root, prefix="wanglu_")
        self.assertEqual(paths, ["wanglu_first/same.txt", "wanglu_second/same.txt"])
        self.assertEqual(message, "wanglu_first/same.txt\nwanglu_second/same.txt")
        self.assertEqual(
            generate_file_menu(self.root, recursive=False), (["top.txt"], "top.txt")
        )

    def test_missing_paths_and_invalid_path_collection_fail(self):
        missing = self.root / "missing"
        with self.assertRaises(FileNotFoundError):
            read_words(missing)
        with self.assertRaises(FileNotFoundError):
            generate_file_menu(missing)
        file = self.root / "words.txt"
        file.write_text("", encoding="utf-8")
        with self.assertRaises(NotADirectoryError):
            generate_file_menu(file)
        with self.assertRaises(TypeError):
            read_word_lists(file)

    def test_import_is_quiet_and_does_not_scan_cwd_or_change_root_logging(self):
        repository = Path(__file__).resolve().parents[2]
        result = subprocess.run(
            [
                sys.executable,
                "-c",
                (
                    f"import sys; sys.path.insert(0, {str(repository)!r}); "
                    "import logging; root = logging.getLogger(); "
                    "level = root.level; handlers = root.handlers.copy(); "
                    "import jwf_common_python.language_utils; "
                    "assert root.level == level and root.handlers == handlers"
                ),
            ],
            cwd=self.root,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, "")
        self.assertEqual(list(self.root.iterdir()), [])


if __name__ == "__main__":
    unittest.main()
