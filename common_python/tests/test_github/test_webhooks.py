"""GitHub 官方验签向量及本地 Flask 测试客户端，不连接 GitHub。"""

import hashlib
import hmac
import io
import subprocess
import sys
import unittest
from contextlib import redirect_stdout
from unittest.mock import Mock, patch

from common_packages.github import create_webhook_app, verify_signature


def signature(payload, secret="test-secret"):
    return (
        "sha256="
        + hmac.new(secret.encode("utf-8"), payload, hashlib.sha256).hexdigest()
    )


class SignatureTests(unittest.TestCase):
    def test_official_github_reference_vector(self):
        self.assertTrue(
            verify_signature(
                b"Hello, World!",
                "It's a Secret to Everybody",
                "sha256=757107ea0eb2509fc211221cce984b8a37570b6d7586c22c46f4379c8b043e17",
            )
        )

    def test_raw_body_unicode_and_tampering(self):
        body = '{ "message": "你好" }'.encode("utf-8")
        header = signature(body, "中文密钥")
        self.assertTrue(verify_signature(body, "中文密钥".encode("utf-8"), header))
        self.assertFalse(verify_signature(body + b" ", "中文密钥", header))
        self.assertFalse(verify_signature(body, "wrong-secret", header))

    def test_missing_and_malformed_signature_headers_return_false(self):
        header = signature(b"body")
        for value in (
            None,
            "",
            "sha1=" + "a" * 40,
            "sha256=not-hex",
            "sha256=" + "a" * 63,
            "prefix" + header,
            header + " ",
            "sha256=" + "界" * 64,
            123,
        ):
            with self.subTest(value=value):
                self.assertFalse(verify_signature(b"body", "test-secret", value))

    def test_invalid_secret_and_payload_are_configuration_errors(self):
        for secret in ("", b""):
            with self.assertRaises(ValueError):
                verify_signature(b"body", secret, None)
        with self.assertRaises(TypeError):
            verify_signature(b"body", None, None)
        with self.assertRaises(TypeError):
            verify_signature("body", "test-secret", None)

    def test_verification_does_not_print_signatures(self):
        output = io.StringIO()
        with redirect_stdout(output):
            self.assertTrue(
                verify_signature(b"body", "test-secret", signature(b"body"))
            )
        self.assertEqual(output.getvalue(), "")


class WebhookAppTests(unittest.TestCase):
    def setUp(self):
        self.handler = Mock()
        self.app = create_webhook_app("test-secret", handler=self.handler)
        self.app.testing = True
        self.client = self.app.test_client()

    def test_valid_request_passes_exact_raw_body_and_delivery_metadata(self):
        body = '{ "message": "你好", "spaced": true }'.encode("utf-8")
        result = self.client.post(
            "/hook",
            data=body,
            content_type="application/json",
            headers={
                "X-Hub-Signature-256": signature(body),
                "X-GitHub-Event": "push",
                "X-GitHub-Delivery": "delivery-1",
            },
        )
        self.assertEqual(result.status_code, 200)
        self.assertEqual(result.get_json(), {"status": 200})
        self.handler.assert_called_once_with(body, "push", "delivery-1")

    def test_invalid_or_missing_signatures_never_call_handler(self):
        for header in (None, "invalid", signature(b"other")):
            with self.subTest(header=header):
                headers = {} if header is None else {"X-Hub-Signature-256": header}
                result = self.client.post("/hook", data=b"body", headers=headers)
                self.assertEqual(result.status_code, 403)
        self.handler.assert_not_called()

    def test_get_is_not_accepted(self):
        self.assertEqual(self.client.get("/hook").status_code, 405)
        self.handler.assert_not_called()

    def test_custom_path_and_no_handler_support_non_json_payloads(self):
        app = create_webhook_app(b"test-secret", path="/github/delivery")
        body = b"not a JSON document"
        result = app.test_client().post(
            "/github/delivery",
            data=body,
            headers={"X-Hub-Signature-256": signature(body)},
        )
        self.assertEqual(result.status_code, 200)
        self.assertEqual(app.test_client().post("/hook").status_code, 404)

    def test_callback_failure_does_not_return_a_success_response(self):
        self.handler.side_effect = RuntimeError("processing failed")
        with self.assertRaisesRegex(RuntimeError, "processing failed"):
            self.client.post(
                "/hook",
                data=b"body",
                headers={"X-Hub-Signature-256": signature(b"body")},
            )

    def test_instances_do_not_share_secrets(self):
        second = create_webhook_app("other-secret")
        body = b"body"
        result = second.test_client().post(
            "/hook", data=body, headers={"X-Hub-Signature-256": signature(body)}
        )
        self.assertEqual(result.status_code, 403)

    def test_invalid_factory_arguments_fail_before_app_creation(self):
        with self.assertRaises(ValueError):
            create_webhook_app("")
        for path in ("", "hook", "/hook/<value>"):
            with self.assertRaises(ValueError):
                create_webhook_app("test-secret", path=path)
        with self.assertRaises(TypeError):
            create_webhook_app("test-secret", handler="invalid")


class DependencyTests(unittest.TestCase):
    def test_signature_verification_does_not_require_flask(self):
        result = subprocess.run(
            [
                sys.executable,
                "-c",
                (
                    "import sys; sys.modules['flask'] = None; "
                    "from common_packages.github import verify_signature; "
                    "assert verify_signature(b'body', 'secret', None) is False"
                ),
            ],
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, "")

    def test_factory_explains_missing_optional_dependency(self):
        with patch.dict(sys.modules, {"flask": None}):
            with self.assertRaisesRegex(ImportError, "pip install flask"):
                create_webhook_app("test-secret")


if __name__ == "__main__":
    unittest.main()
