import sys

sys.path.append("..")
from common_packages.sms import TencentSendSms
from common_packages.utils import image_utils

from .. import get_config


class TestSms:
    def test_tencent_sms(self):
        config: dict = get_config()
        sms = TencentSendSms(**config["sms"]["tencent"])
        s = sms.send("+8618285574257", "123456")
        assert s == True
        s2 = sms.send("+86111", "123456")
        assert s2 == False
