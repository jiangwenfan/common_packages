"""使用真实腾讯 SDK 进行离线测试，不发送翻译请求。"""

import copy
import io
import json
import subprocess
import sys
import unittest
from contextlib import redirect_stdout
from unittest.mock import Mock, patch

from requests import Response
from tencentcloud.common.exception.tencent_cloud_sdk_exception import (
    TencentCloudSDKException,
)

from jwf_common_python.translate import Translate
from jwf_common_python.translate.tencent import TencentTranslate


RESPONSE = {
    "TargetText": "你好",
    "Source": "en",
    "Target": "zh",
    "RequestId": "offline-request-id",
    "ExtraField": {"preserved": True},
}


def http_response(body):
    response = Response()
    response.status_code = 200
    response.headers["Content-Type"] = "application/json"
    response._content = json.dumps({"Response": body}).encode("utf-8")
    return response


class TencentTranslateTests(unittest.TestCase):
    def setUp(self):
        self.translator = TencentTranslate(
            "test-id",
            "test-key",
            region="ap-guangzhou",
            project_id=123,
            timeout=5,
            token="temporary-token",
        )
        self.addCleanup(self.translator.close)
        call_patch = patch.object(self.translator.client.request, "send_request")
        self.call = call_patch.start()
        self.addCleanup(call_patch.stop)
        self.call.return_value = http_response(RESPONSE)

    def test_concrete_interface_and_parameter_configuration(self):
        self.assertIsInstance(self.translator, Translate)
        client = self.translator.client
        self.assertEqual(client.region, "ap-guangzhou")
        self.assertEqual(client.profile.httpProfile.endpoint, "tmt.tencentcloudapi.com")
        self.assertEqual(client.profile.httpProfile.reqTimeout, 5)
        self.assertEqual(client.credential.token, "temporary-token")
        self.call.assert_not_called()

    def test_translate_returns_full_sdk_response_and_serializes_parameters(self):
        result = self.translator.translate("Hello 世界", "auto", "zh-CN")
        self.assertEqual(result, RESPONSE)
        request = self.call.call_args.args[0]
        self.assertEqual(request.header["X-TC-Action"], "TextTranslate")
        parameters = json.loads(request.data)
        self.assertEqual(
            parameters,
            {
                "SourceText": "Hello 世界",
                "Source": "auto",
                "Target": "zh",
                "ProjectId": 123,
            },
        )

    def test_requests_are_independent_and_optional_fields_do_not_leak(self):
        requests = []
        with patch.object(
            self.translator.client,
            "call_json",
            wraps=self.translator.client.call_json,
        ) as translate:
            self.translator.translate("hello", untranslated_text="hello")
            requests.append(translate.call_args.args[1])
            self.assertEqual(
                json.loads(self.call.call_args.args[0].data)["UntranslatedText"],
                "hello",
            )
            self.translator.translate("world")
            requests.append(translate.call_args.args[1])
        self.assertIsNot(requests[0], requests[1])
        self.assertEqual(requests[0]["SourceText"], "hello")
        self.assertEqual(requests[1]["SourceText"], "world")
        self.assertNotIn(
            "UntranslatedText", json.loads(self.call.call_args.args[0].data)
        )

    def test_language_alias_and_native_codes(self):
        self.translator.translate("你好", "zh-CN", "en")
        self.assertEqual(json.loads(self.call.call_args.args[0].data)["Source"], "zh")
        self.translator.translate("hello", "en", "zh-TW")
        self.assertEqual(
            json.loads(self.call.call_args.args[0].data)["Target"], "zh-TW"
        )

    def test_sdk_exception_propagates_without_printing(self):
        error = TencentCloudSDKException("LimitExceeded", "offline error")
        self.call.side_effect = error
        output = io.StringIO()
        with redirect_stdout(output), self.assertRaises(
            TencentCloudSDKException
        ) as caught:
            self.translator.translate("hello")
        self.assertIs(caught.exception, error)
        self.assertEqual(output.getvalue(), "")

    def test_word_and_sentence_methods_keep_source_context(self):
        word = self.translator.translate_word("Hello")
        sentence = self.translator.translate_sentence("Hello world!")
        self.assertEqual(word, {**RESPONSE, "word": "Hello"})
        self.assertEqual(sentence, {**RESPONSE, "sentence": "Hello world!"})

    def test_standard_word_format_does_not_mutate_response(self):
        response = {**RESPONSE, "word": "Hello"}
        original = copy.deepcopy(response)
        word = self.translator.format_word_response(response)
        self.assertEqual(word["normalized_word"], "Hello")
        self.assertEqual(word["display_word"], "Hello")
        self.assertEqual(word["translations"][0]["display"], "你好")
        self.assertEqual(word["translations"][0]["pos_tag"], ("Other", "其他"))
        self.assertEqual(word["audio_data"], b"")
        self.assertEqual(word["extended_info"]["RequestId"], RESPONSE["RequestId"])
        self.assertEqual(response, original)

    def test_standard_sentence_format_has_source_and_translation(self):
        self.assertEqual(
            self.translator.format_sentence_response(
                {**RESPONSE, "sentence": "Hello!"}
            ),
            {"sentence": "Hello!", "translations": ["你好"], "audio_data": b""},
        )

    def test_audio_is_explicitly_unsupported(self):
        with self.assertRaises(NotImplementedError):
            self.translator.download_audio_file("https://example.com/audio")
        self.call.assert_not_called()

    def test_invalid_text_and_languages_do_not_request_translation(self):
        for text in ("", " ", None, b"hello"):
            with self.subTest(text=text), self.assertRaises(ValueError):
                self.translator.translate(text)
        for source, target in (("", "en"), ("en", ""), (None, "zh"), ("en", "auto")):
            with self.subTest(source=source, target=target), self.assertRaises(
                ValueError
            ):
                self.translator.translate("hello", source, target)
        with self.assertRaises(TypeError):
            self.translator.translate("hello", untranslated_text=123)
        self.call.assert_not_called()

    def test_invalid_configuration(self):
        for config in (
            {"secret_id": ""},
            {"secret_key": ""},
            {"region": ""},
            {"endpoint": ""},
            {"project_id": -1},
            {"project_id": True},
            {"timeout": 0},
            {"token": ""},
        ):
            with self.subTest(config=config), self.assertRaises(ValueError):
                TencentTranslate(
                    **{"secret_id": "test-id", "secret_key": "test-key", **config}
                )

    def test_malformed_sdk_response_fails(self):
        self.call.return_value = http_response({"RequestId": "missing-text"})
        with self.assertRaisesRegex(ValueError, "TargetText"):
            self.translator.translate("hello")

    def test_context_releases_session_once_and_prevents_reuse(self):
        session = Mock()
        with patch.object(
            self.translator.client.request.conn, "_session", session, create=True
        ):
            with self.assertRaisesRegex(ValueError, "callback failed"):
                with self.translator:
                    raise ValueError("callback failed")
            self.translator.close()
            session.close.assert_called_once()
        with self.assertRaises(RuntimeError):
            self.translator.translate("hello")
        self.call.assert_not_called()


class DependencyTests(unittest.TestCase):
    def test_import_and_formatting_work_without_sdk(self):
        result = subprocess.run(
            [
                sys.executable,
                "-c",
                (
                    "import sys; sys.modules['tencentcloud'] = None; "
                    "from jwf_common_python.translate.tencent import TencentTranslate; "
                    "assert TencentTranslate.format_sentence_response("
                    "{'sentence': 'hello', 'TargetText': '你好'})['translations'] == ['你好']"
                ),
            ],
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, "")

    def test_missing_sdk_gives_compatible_install_command(self):
        with patch.dict(sys.modules, {"tencentcloud.common.credential": None}):
            with self.assertRaisesRegex(ImportError, "tencentcloud-sdk-python-common"):
                TencentTranslate("test-id", "test-key")

    def test_product_sdk_is_not_required(self):
        with patch.dict(sys.modules, {"tencentcloud.tmt": None}):
            translator = TencentTranslate("test-id", "test-key")
            self.assertIsInstance(translator, Translate)
            translator.close()


if __name__ == "__main__":
    unittest.main()
