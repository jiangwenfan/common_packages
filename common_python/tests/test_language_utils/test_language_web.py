import threading
import unittest
from unittest.mock import patch

import requests

from jwf_common_python.language_utils import fetch_words_from_pages


def response(text, status=200):
    result = requests.Response()
    result.status_code = status
    result.encoding = "utf-8"
    result._content = text.encode("utf-8")
    result._content_consumed = True
    return result


class WebTests(unittest.TestCase):
    @patch("jwf_common_python.language_utils.web.requests.get")
    def test_extracts_html_text_and_ignores_scripts_styles_and_comments(self, get):
        get.return_value = response(
            "<style>BadCss</style><script>BadScript()</script>"
            "<template>HiddenWord</template><noscript>HiddenText</noscript>"
            "<!-- CommentWord --><p>Hel<b>lo</b> &amp; world!</p><p>A hello</p>"
        )
        self.assertEqual(
            fetch_words_from_pages(["https://example.com"]),
            {"https://example.com": ["Hello", "world"]},
        )
        get.assert_called_once_with("https://example.com", timeout=30)

    @patch("jwf_common_python.language_utils.web.requests.get")
    def test_waits_for_workers_and_returns_results_in_input_order(self, get):
        second_started = threading.Event()

        def fetch(url, **kwargs):
            if url.endswith("first"):
                if not second_started.wait(2):
                    raise RuntimeError("second worker never started")
                return response("first page")
            second_started.set()
            return response("second page")

        get.side_effect = fetch
        urls = ["https://example.com/first", "https://example.com/second"]
        result = fetch_words_from_pages(urls, max_workers=2)
        self.assertEqual(list(result), urls)
        self.assertEqual(result[urls[0]], ["first", "page"])
        self.assertEqual(result[urls[1]], ["second", "page"])

    @patch("jwf_common_python.language_utils.web.requests.get")
    def test_generator_exclusions_are_shared_by_all_pages_without_consumption(
        self, get
    ):
        get.side_effect = lambda *args, **kwargs: response("Hello known fresh fresh")
        result = fetch_words_from_pages(
            ["https://example.com/a", "https://example.com/b", "https://example.com/a"],
            exclude_words=iter(["hello"]),
            known_words=iter(["known"]),
            unique=False,
        )
        self.assertEqual(
            list(result.values()), [["fresh", "fresh"], ["fresh", "fresh"]]
        )
        self.assertEqual(get.call_count, 2)

    @patch("jwf_common_python.language_utils.web.requests.get")
    def test_http_errors_propagate_instead_of_silent_empty_results(self, get):
        get.return_value = response("failed", 503)
        with self.assertRaises(requests.HTTPError):
            fetch_words_from_pages(["https://example.com/fail"])

    @patch("jwf_common_python.language_utils.web.requests.get")
    def test_network_error_propagates(self, get):
        error = requests.Timeout("offline error")
        get.side_effect = error
        with self.assertRaises(requests.Timeout) as caught:
            fetch_words_from_pages(["https://example.com"])
        self.assertIs(caught.exception, error)

    @patch("jwf_common_python.language_utils.web.requests.get")
    def test_invalid_arguments_fail_before_network_access(self, get):
        for options in (
            {"max_workers": 0},
            {"max_workers": True},
            {"timeout": 0},
            {"timeout": float("inf")},
            {"min_length": 0},
        ):
            with self.subTest(options=options), self.assertRaises(ValueError):
                fetch_words_from_pages(["https://example.com"], **options)
        with self.assertRaises(ValueError):
            fetch_words_from_pages(["https://example.com", "file:///tmp/words"])
        self.assertEqual(fetch_words_from_pages([]), {})
        get.assert_not_called()


if __name__ == "__main__":
    unittest.main()
