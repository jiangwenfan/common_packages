"""使用真实 SDK 数据类型，mock 客户端，避免发送真实短信。"""

from unittest.mock import patch

import pytest
from tencentcloud.common.exception.tencent_cloud_sdk_exception import (
    TencentCloudSDKException,
)
from tencentcloud.sms.v20210111 import models

from jwf_common_python.sms import TencentSendSms


@pytest.fixture
def sms() -> TencentSendSms:
    return TencentSendSms(
        secret_id="test-id", secret_key="test-key", app_id="test-app",
        sign_name="test-sign", template_id="test-template",
        endpoint="sms.tencentcloudapi.com", veri_code_timeout="5",
    )


@pytest.mark.parametrize("code,expected", [
    ("Ok", True), ("FailedOperation.InsufficientBalanceInSmsPackage", False),
])
def test_tencent_sms(sms: TencentSendSms, code: str, expected: bool) -> None:
    status = models.SendStatus()
    status.PhoneNumber, status.Code = "+8613800000000", code
    response = models.SendSmsResponse()
    response.SendStatusSet = [status]
    with patch("jwf_common_python.sms.tencent_sms.sms_client.SmsClient") as client:
        client.return_value.SendSms.return_value = response
        assert sms.send(status.PhoneNumber, "123456", "test-session") is expected
    request = client.return_value.SendSms.call_args.args[0]
    assert request.PhoneNumberSet == [status.PhoneNumber]
    assert request.TemplateParamSet == ["123456", "5"]
    assert request.TemplateId == "test-template"
    assert request.SessionContext == "test-session"


def test_tencent_sms_sdk_error(sms: TencentSendSms) -> None:
    with patch("jwf_common_python.sms.tencent_sms.sms_client.SmsClient") as client:
        client.return_value.SendSms.side_effect = TencentCloudSDKException(
            "ClientNetworkError", "offline test error",
        )
        assert sms.send("+8613800000000", "123456") is False
