import sys

sys.path.append("..")
from jwf_common_python.sms import TencentSendSms
from jwf_common_python.utils import image_utils

from .. import get_config


class TestSms:
    def test_tencent_sms(self):
        config: dict = get_config()
        sms = TencentSendSms(**config["sms"]["tencent"])
        s = sms.send("+8618285574257", "123456")
        assert s == True
        s2 = sms.send("+86111", "123456")
        assert s2 == False
