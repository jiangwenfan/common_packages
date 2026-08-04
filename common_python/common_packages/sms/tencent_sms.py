import logging

from tencentcloud.common import credential
from tencentcloud.common.exception.tencent_cloud_sdk_exception import (
    TencentCloudSDKException,
)
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile
from tencentcloud.sms.v20210111 import models, sms_client
from tencentcloud.sms.v20210111.models import SendSmsResponse, SendStatus

from common_packages.sms.interface import SendSms


class TencentSendSms(SendSms):
    def __init__(self, **kwargs) -> None:
        """
        发送成功:
        {
            "SendStatusSet": [
                {
                "SerialNo": "2640:222395940116893272585707425",
                "PhoneNumber": "+8618285574257",
                "Fee": 1,
                "SessionContext": "user session",
                "Code": "Ok",
                "Message": "send success",
                "IsoCode": "CN"
                }
            ],
            "RequestId": "bbc9e3e8-a67e-4ed0-9e85-713cda1ae041"
        }

        发送失败:
         {
            "SendStatusSet": [
                {
                "SerialNo": "",
                "PhoneNumber": "+8618285574257",
                "Fee": 0,
                "SessionContext": "user session",
                "Code": "FailedOperation.InsufficientBalanceInSmsPackage",
                "Message": "insufficient balance in SMS package",
                "IsoCode": ""
                }
            ],
            "RequestId": "a28c5e46-5209-4425-8bfe-97784d205a52"
        }
        """
        if not {
            "secret_id",
            "secret_key",
            "app_id",
            "sign_name",
            "template_id",
            "endpoint",
            "veri_code_timeout",
        }.issubset(kwargs.keys()):
            raise ValueError(
                "secret_id,secret_key,app_id,sign_name,template_id,endpoint,veri_code_timeout must be provided"
            )
        self.secret_id = kwargs["secret_id"]
        self.secret_key = kwargs["secret_key"]
        self.app_id = kwargs["app_id"]
        self.sign_name = kwargs["sign_name"]
        self.template_id = kwargs["template_id"]
        self.endpoint = kwargs["endpoint"]
        self.veri_code_timeout = kwargs["veri_code_timeout"]

    def send(self, send_phone_number: str, veri_code: str, session_context: str = ""):
        """
        +8618285574257
        2222

        session_context:
         用户的 session 内容（无需要可忽略）: 可以携带用户侧 ID 等上下文信息，server 会原样返回
        """
        try:
            cred = credential.Credential(self.secret_id, self.secret_key)
            httpProfile = HttpProfile()
            httpProfile.reqMethod = "POST"
            httpProfile.reqTimeout = 30
            httpProfile.endpoint = self.endpoint

            # 实例化一个客户端配置对象，可以指定超时时间等配置
            clientProfile = ClientProfile()
            clientProfile.signMethod = "TC3-HMAC-SHA256"  # 指定签名算法
            clientProfile.language = "en-US"
            clientProfile.httpProfile = httpProfile

            client = sms_client.SmsClient(cred, "ap-guangzhou", clientProfile)

            req = models.SendSmsRequest()

            req.SmsSdkAppId = self.app_id
            req.SignName = self.sign_name
            # req.TemplateId = "1941616"
            req.TemplateId = self.template_id
            # 模板参数: 模板参数的个数需要与 TemplateId 对应模板的变量个数保持一致，，若无模板参数，则设置为空
            req.TemplateParamSet = [veri_code, self.veri_code_timeout]
            # req.PhoneNumberSet = ["+8618285574257"]
            req.PhoneNumberSet = [send_phone_number]

            req.SessionContext = session_context

            response: SendSmsResponse = client.SendSms(req)
            response_status: SendStatus = response.SendStatusSet[0]
            assert response_status.PhoneNumber == send_phone_number, "发送号码和响应号码不一致"
            if response_status.Code != "Ok":
                logging.error(f"发送短信失败: {response_status}")
                return False
            logging.debug(f"发送短信成功: {response_status}")
            return True
        except TencentCloudSDKException as err:
            print(err)
            logging.error(f"发送短信失败: {err}")
            return False
