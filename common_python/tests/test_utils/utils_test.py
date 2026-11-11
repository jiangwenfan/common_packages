"""工具函数和邮件测试使用固定数据，SMTP 调用全部 mock。"""

import smtplib
from unittest.mock import patch

import pytest

from jwf_common_python.utils.utils import SendEmail, calculate_relative_value


@pytest.mark.parametrize("input_data,db_data,expected", [
    ([1, 2, 3, 4, 5], [3, 4, 5, 6], 0.6),
    ([1, 1, 2], [1, 1], 0.5),
    ([1, 2], [3, 4], 0.0),
])
def test_calculate_relative_value(
    input_data: list[int], db_data: list[int], expected: float,
) -> None:
    assert calculate_relative_value(input_data, db_data) == expected


@pytest.fixture
def email_client() -> SendEmail:
    return SendEmail({
        "host": "smtp.example.com", "port": 465,
        "user": "sender@example.com", "passwd": "test-password",
    })


def test_email_success(email_client: SendEmail) -> None:
    # 拦截 SMTP 客户端构造，保证测试不会连接邮件服务器。
    with patch("jwf_common_python.utils.utils.smtplib.SMTP_SSL") as smtp:
        status, message = email_client.send_txt_message(
            ["receiver@example.com"], "test subject", "test content",
        )
    assert (status, message) == (True, "success")
    smtp.assert_called_once_with("smtp.example.com", 465)
    smtp.return_value.login.assert_called_once_with(
        "sender@example.com", "test-password",
    )
    sender, receivers, body = smtp.return_value.sendmail.call_args.args
    assert sender == "sender@example.com"
    assert receivers == ["receiver@example.com"]
    assert "Subject: test subject" in body


def test_email_failure(email_client: SendEmail) -> None:
    with patch(
        "jwf_common_python.utils.utils.smtplib.SMTP_SSL",
        side_effect=smtplib.SMTPException("authentication failed"),
    ):
        assert email_client.send_txt_message(
            ["receiver@example.com"], "subject", "content",
        ) == (False, "authentication failed")
