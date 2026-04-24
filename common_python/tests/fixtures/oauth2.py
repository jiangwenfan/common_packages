import pytest

from common_packages.oauth2.google import Oauth2Google


@pytest.fixture(scope="class")
def oauth2_google_obj(global_config):
    """用于在`每个测试用例`中初始化oauth2 google对象"""
    config = global_config["oauth2"]["google"]
    google_obj = Oauth2Google(**config)
    return google_obj
