"""欧路离线测试：使用真实 requests 请求组装和模拟响应。"""

import copy
import json
import unittest
from unittest.mock import patch
from urllib.parse import parse_qs, urlparse

import requests

from common_packages.eudic import EudicClient


def response(body, status=200):
    reply = requests.Response()
    reply.status_code = status
    reply.encoding = "utf-8"
    reply._content = json.dumps(body, ensure_ascii=False).encode("utf-8")
    reply._content_consumed = True
    return reply


class EudicTests(unittest.TestCase):
    def setUp(self):
        self.client = EudicClient("NIS test-token", language="en", timeout=5)
        self.client._session.trust_env = False
        self.addCleanup(self.client.close)
        send_patch = patch.object(self.client._session, "send")
        self.send = send_patch.start()
        self.addCleanup(send_patch.stop)

    def request_json(self):
        return json.loads(self.send.call_args.args[0].body)

    def query(self, call=None):
        call = call if call is not None else self.send.call_args
        return parse_qs(urlparse(call.args[0].url).query)

    def test_create_returns_all_fields_and_passes_token(self):
        body = {"data": {"id": "123456789012345678", "name": "新词"}, "extra": "kept"}
        self.send.return_value = response(body, 201)
        self.assertEqual(self.client.create_book("新词"), body)
        request = self.send.call_args.args[0]
        self.assertEqual(request.method, "POST")
        self.assertEqual(
            request.url, "https://api.frdic.com/api/open/v1/studylist/category"
        )
        self.assertEqual(request.headers["Authorization"], "NIS test-token")
        self.assertEqual(self.send.call_args.kwargs["timeout"], 5)
        self.assertEqual(self.request_json(), {"language": "en", "name": "新词"})

    def test_list_books_preserves_metadata_and_language(self):
        self.client.language = "fr"
        body = {"data": [{"id": "book-1", "name": "词表"}], "message": "", "extra": 1}
        self.send.return_value = response(body)
        self.assertEqual(self.client.list_books(), body)
        self.assertEqual(self.query(), {"language": ["fr"]})

    def test_explicit_token_is_not_overridden_by_netrc_credentials(self):
        self.client._session.trust_env = True
        self.send.return_value = response({"data": []})
        with patch(
            "requests.sessions.get_netrc_auth",
            return_value=("other-user", "other-secret"),
        ) as netrc:
            self.client.list_books()
        self.assertEqual(
            self.send.call_args.args[0].headers["Authorization"], "NIS test-token"
        )
        netrc.assert_not_called()

    def test_redirect_is_not_followed_as_an_api_result(self):
        reply = response({}, 302)
        reply.headers["Location"] = "https://example.com/login"
        self.send.return_value = reply
        with self.assertRaises(requests.HTTPError):
            self.client.list_books()
        self.assertFalse(self.send.call_args.kwargs["allow_redirects"])
        self.assertEqual(self.send.call_count, 1)

    def test_default_import_preserves_existing_ratings_and_input(self):
        words = [" Apple ", "apple", "a lot of"]
        original = words.copy()
        self.send.return_value = response({"message": "导入完成", "imported": 2}, 201)
        self.assertEqual(self.client.add_words("book-1", iter(words))["imported"], 2)
        self.assertEqual(
            self.request_json(),
            {
                "category_id": "book-1",
                "language": "en",
                "words": ["Apple", "apple", "a lot of"],
            },
        )
        self.assertEqual(words, original)
        self.assertEqual(self.send.call_count, 1)  # 不会隐式创建生词本

    def test_explicit_rating_uses_current_items_format_and_accepts_default_book(self):
        self.send.return_value = response({"message": "导入成功"}, 201)
        self.client.add_words(0, ["hello"], star=3)
        self.assertEqual(
            self.request_json(),
            {
                "category_id": 0,
                "language": "en",
                "items": [{"word": "hello", "star": 3}],
            },
        )

    def test_export_starts_at_zero_and_preserves_full_page_responses(self):
        pages = [
            {
                "data": [{"word": "one", "exp": "释义", "star": 3}, {"word": "two"}],
                "extra": 1,
            },
            {"data": [{"word": "three", "phon": "音标"}], "message": "done"},
        ]
        original = copy.deepcopy(pages)
        self.send.side_effect = [response(page) for page in pages]
        self.assertEqual(self.client.export_book("book-1", page_size=2), pages)
        self.assertEqual(pages, original)
        self.assertEqual(
            [self.query(call)["page"] for call in self.send.call_args_list],
            [["0"], ["1"]],
        )
        self.assertEqual(
            self.query(),
            {
                "category_id": ["book-1"],
                "language": ["en"],
                "page": ["1"],
                "page_size": ["2"],
                "sort": ["asc"],
            },
        )

    def test_exact_page_multiple_fetches_empty_terminal_page(self):
        pages = [{"data": [{"word": "one"}]}, {"data": [{"word": "two"}]}, {"data": []}]
        self.send.side_effect = [response(page) for page in pages]
        self.assertEqual(self.client.export_book(0, page_size=1), pages)
        self.assertEqual(self.send.call_count, 3)

    def test_empty_book_returns_its_response(self):
        body = {"data": [], "message": "empty"}
        self.send.return_value = response(body)
        self.assertEqual(self.client.export_book(0), [body])
        self.assertEqual(self.send.call_count, 1)

    def test_http_failure_exposes_response_and_does_not_return_partial_export(self):
        failed = response({"message": "not authorized"}, 401)
        self.send.side_effect = [response({"data": [{"word": "one"}]}), failed]
        with self.assertRaises(requests.HTTPError) as caught:
            self.client.export_book("book-1", page_size=1)
        self.assertIs(caught.exception.response, failed)
        self.assertEqual(caught.exception.response.json()["message"], "not authorized")

    def test_network_error_propagates(self):
        error = requests.Timeout("offline timeout")
        self.send.side_effect = error
        with self.assertRaises(requests.Timeout) as caught:
            self.client.list_books()
        self.assertIs(caught.exception, error)

    def test_unexpected_success_status_is_not_treated_as_created(self):
        self.send.return_value = response({"message": "not created"}, 200)
        with self.assertRaises(requests.HTTPError):
            self.client.create_book("new")

    def test_invalid_json_and_response_shapes_fail(self):
        malformed = response({})
        malformed._content = b"not-json"
        self.send.return_value = malformed
        with self.assertRaises(requests.JSONDecodeError):
            self.client.list_books()
        for body in ([], {}, {"data": None}, {"data": {}}):
            with self.subTest(body=body), self.assertRaises(ValueError):
                self.send.return_value = response(body)
                self.client.export_book(0)
        self.send.return_value = response({"data": {}}, 201)
        with self.assertRaises(ValueError):
            self.client.create_book("new")

    def test_page_limit_never_silently_truncates(self):
        self.send.side_effect = lambda *args, **kwargs: response(
            {"data": [{"word": "one"}]}
        )
        with self.assertRaisesRegex(RuntimeError, "分页上限"):
            self.client.export_book(0, page_size=1)
        self.assertEqual(self.send.call_count, 51)
        self.assertEqual(self.query()["page"], ["50"])

    def test_invalid_book_and_page_arguments_do_not_send_requests(self):
        for book_id in (None, "", " ", False, -1, []):
            with self.subTest(book_id=book_id), self.assertRaises(ValueError):
                self.client.get_words(book_id)
        for kwargs in (
            {"page": -1},
            {"page": 51},
            {"page": True},
            {"page_size": 0},
            {"page_size": 101},
            {"page_size": True},
            {"sort": "invalid"},
        ):
            with self.subTest(kwargs=kwargs), self.assertRaises(ValueError):
                self.client.get_words(0, **kwargs)
        with self.assertRaises(ValueError):
            self.client.create_book(" ")
        self.send.assert_not_called()

    def test_invalid_words_and_ratings_do_not_write(self):
        for words in ([], [" "], [None], "hello", b"hello", {"hello": 1}):
            with self.subTest(words=words), self.assertRaises((TypeError, ValueError)):
                self.client.add_words(0, words)
        for star in (0, 6, True, "3"):
            with self.subTest(star=star), self.assertRaises(ValueError):
                self.client.add_words(0, ["hello"], star=star)
        with self.assertRaisesRegex(ValueError, "1000"):
            self.client.add_words(0, (str(index) for index in range(1001)))
        self.send.assert_not_called()

    def test_invalid_configuration_does_not_create_sessions(self):
        with patch("common_packages.eudic.wordbook.requests.Session") as session:
            for config in (
                {"token": ""},
                {"language": "zh"},
                {"timeout": 0},
                {"timeout": float("nan")},
                {"timeout": float("inf")},
                {"timeout": True},
            ):
                with self.subTest(config=config), self.assertRaises(ValueError):
                    EudicClient(**{"token": "NIS test-token", **config})
            session.assert_not_called()

    def test_context_closes_session_once_even_when_caller_fails(self):
        with patch.object(
            self.client._session, "close", wraps=self.client._session.close
        ) as close:
            with self.assertRaisesRegex(ValueError, "caller failed"):
                with self.client:
                    raise ValueError("caller failed")
            self.client.close()
            close.assert_called_once()
        with self.assertRaises(RuntimeError):
            self.client.list_books()
        self.send.assert_not_called()


if __name__ == "__main__":
    unittest.main()
