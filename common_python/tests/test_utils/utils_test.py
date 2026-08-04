from common_packages.utils.utils import calculate_relative_value

from .. import get_config


def test_calculate_relative_value():
    res = calculate_relative_value(
        input_data=[1, 2, 3, 4, 5], db_data=[3, 4, 5, 6, 7, 8]
    )
    print(res)


test_calculate_relative_value()


import sys

sys.path.append("..")
from common_packages.email import SendEmail

from .. import get_config

config: dict = get_config()
content = "test content"
subject = "title123"


class TestEmail:
    def test_163(self):
        receivers = config["email"]["receivers"]
        config_163 = config["email"]["config_163"]
        e_163 = SendEmail(config_163)
        status, _ = e_163.send_txt_message(receivers, subject, content)
        assert status == True

    def test_feishu(self):
        receivers = config["email"]["receivers"]
        config_feishu = config["email"]["config_feishu"]
        e_feishu = SendEmail(config_feishu)
        status, _ = e_feishu.send_txt_message(receivers, subject, content)
        assert status == True
