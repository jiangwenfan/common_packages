"""签名计算不需要真实腾讯云密钥或网络。"""

from datetime import datetime, timezone
from unittest.mock import patch

from jwf_common_python.utils.tencent_utils import generate_tencent_key


def test_generate_tencent_key() -> None:
    with patch("jwf_common_python.utils.tencent_utils.datetime.datetime") as clock:
        clock.now.return_value = datetime(2024, 1, 1, tzinfo=timezone.utc)
        authorization = generate_tencent_key(
            secret_key="test-key", key="test.png", secret_id="test-id",
        )
    fields = dict(part.split("=", 1) for part in authorization.split("&"))
    assert fields["q-sign-algorithm"] == "sha1"
    assert fields["q-ak"] == "test-id"
    assert fields["q-sign-time"] == "1704067200;1704069000"
    assert fields["q-key-time"] == fields["q-sign-time"]
    assert len(fields["q-signature"]) == 40
