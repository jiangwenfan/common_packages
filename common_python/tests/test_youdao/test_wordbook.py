"""使用模拟响应验证单词本工具，无需登录或网络。"""

import unittest
from unittest.mock import Mock, patch

import requests

from jwf_common_python.youdao import (
    fetch_all_wordbook_data,
    fetch_wordbook_data,
    filter_new_words,
)
from jwf_common_python.youdao.wordbook import WORDBOOK_URL


def make_page(total, *words):
    return {
        "msg": "SUCCESS",
        "code": 0,
        "data": {
            "total": total,
            "itemList": [{"word": word, "meaning": "释义"} for word in words],
            "extra": "保留的元数据",
        },
    }


class WordbookTests(unittest.TestCase):
    @patch("jwf_common_python.youdao.wordbook.requests.get")
    def test_single_page_preserves_response_and_passes_cookie(self, get):
        page = make_page(1, "hello")
        get.return_value.json.return_value = page

        self.assertEqual(
            fetch_wordbook_data("session=example; user=example", 10, 20, 5), page
        )
        get.assert_called_once_with(
            WORDBOOK_URL,
            params={"limit": 10, "offset": 20},
            headers={"Cookie": "session=example; user=example"},
            timeout=5,
        )

    @patch("jwf_common_python.youdao.wordbook.requests.get")
    def test_exports_all_pages_without_losing_fields(self, get):
        pages = [make_page(3, "one", "two"), make_page(3, "three")]
        get.side_effect = [Mock(json=Mock(return_value=page)) for page in pages]

        self.assertEqual(fetch_all_wordbook_data("session=example", limit=2), pages)
        self.assertEqual(
            [entry.kwargs["params"] for entry in get.call_args_list],
            [{"limit": 2, "offset": 0}, {"limit": 2, "offset": 2}],
        )

    @patch("jwf_common_python.youdao.wordbook.requests.get")
    def test_stops_at_total_when_last_page_is_full(self, get):
        page = make_page(2, "one", "two")
        get.return_value.json.return_value = page

        self.assertEqual(fetch_all_wordbook_data("session=example", limit=2), [page])
        get.assert_called_once()

    @patch("jwf_common_python.youdao.wordbook.requests.get")
    def test_empty_wordbook_preserves_response(self, get):
        page = make_page(0)
        get.return_value.json.return_value = page

        self.assertEqual(fetch_all_wordbook_data("session=example"), [page])
        get.assert_called_once()

    @patch("jwf_common_python.youdao.wordbook.requests.get")
    def test_server_page_cap_does_not_skip_words(self, get):
        pages = [make_page(2, "one"), make_page(2, "two")]
        get.side_effect = [Mock(json=Mock(return_value=page)) for page in pages]

        self.assertEqual(fetch_all_wordbook_data("session=example"), pages)
        self.assertEqual(get.call_args.kwargs["params"]["offset"], 1)

    @patch("jwf_common_python.youdao.wordbook.requests.get")
    def test_api_failure_raises(self, get):
        get.return_value.json.return_value = {"msg": "NOT_LOGIN"}
        with self.assertRaises(ValueError):
            fetch_all_wordbook_data("session=example")

    @patch("jwf_common_python.youdao.wordbook.requests.get")
    def test_later_http_failure_does_not_return_partial_export(self, get):
        first = Mock(json=Mock(return_value=make_page(2, "one")))
        second = Mock()
        second.raise_for_status.side_effect = requests.HTTPError("503")
        get.side_effect = [first, second]

        with self.assertRaises(requests.HTTPError):
            fetch_all_wordbook_data("session=example", limit=1)

    @patch("jwf_common_python.youdao.wordbook.requests.get")
    def test_timeout_propagates(self, get):
        get.side_effect = requests.Timeout()
        with self.assertRaises(requests.Timeout):
            fetch_all_wordbook_data("session=example")

    @patch("jwf_common_python.youdao.wordbook.requests.get")
    def test_unexpected_empty_page_does_not_return_partial_export(self, get):
        pages = [make_page(2, "one"), make_page(2)]
        get.side_effect = [Mock(json=Mock(return_value=page)) for page in pages]
        with self.assertRaises(ValueError):
            fetch_all_wordbook_data("session=example", limit=1)

    @patch("jwf_common_python.youdao.wordbook.requests.get")
    def test_invalid_arguments_do_not_send_requests(self, get):
        for kwargs in ({"cookie": " "}, {"limit": 0}, {"offset": -1}):
            arguments = {"cookie": "session=example", **kwargs}
            with self.subTest(kwargs=kwargs), self.assertRaises(ValueError):
                fetch_wordbook_data(**arguments)
        get.assert_not_called()

    @patch("jwf_common_python.youdao.wordbook.requests.get")
    def test_invalid_page_raises(self, get):
        for data in (None, {"total": 1}, {"total": -1, "itemList": []}):
            get.return_value.json.return_value = {"msg": "SUCCESS", "data": data}
            with self.subTest(data=data), self.assertRaises(ValueError):
                fetch_all_wordbook_data("session=example")

    def test_filters_normalizes_and_preserves_order_without_mutation(self):
        existing = [" apple\n", "Claim"]
        current = ["apple", " banana\n", "banana", "claim", "", "  ", "pear"]
        original = current.copy()

        self.assertEqual(
            filter_new_words(existing, current), ["banana", "claim", "pear"]
        )
        self.assertEqual(current, original)
        self.assertEqual(existing, [" apple\n", "Claim"])

    def test_filter_accepts_generators_and_empty_inputs(self):
        self.assertEqual(filter_new_words(iter(["one"]), iter(["one", "two"])), ["two"])
        self.assertEqual(filter_new_words([], []), [])
        self.assertEqual(filter_new_words(["one"], ["one"]), [])


if __name__ == "__main__":
    unittest.main()
