import pytest

from common_packages.llm.baidu_ernie import LLMBaiduErnie


@pytest.fixture(scope="class")
def llm_baidu_ernie_obj(global_config):
    """用于在`每个测试用例`中初始化百度ernie大模型对象"""
    config = global_config["llm"]["baidu_ernie"]
    baidu_ernie_obj = LLMBaiduErnie(**config)
    return baidu_ernie_obj
