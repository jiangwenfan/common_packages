import pytest

from common_packages.file_storage import LocalStorage, TencentCos


@pytest.fixture(scope="class")
def local_config(global_config):
    """用于在`整个LocalStorage测试类`中获取LocalStorage的配置"""
    local_config = global_config["storage"]["local"]
    return local_config


@pytest.fixture(scope="class")
def tencent_cos_config(global_config):
    """用于在`整个TencentCosStorage测试类`中获取TencentCosStorage的配置"""
    tencent_cos_config = global_config["storage"]["tencent_cos"]
    return tencent_cos_config


@pytest.fixture(scope="class")
def local_obj(local_config):
    """用于在`整个LocalStorage测试类`中初始化LocalStorage对象"""
    local = LocalStorage(**local_config)
    return local


@pytest.fixture(scope="class")
def tencent_cos_obj(tencent_cos_config):
    """用于在`整个TencentCosStorage测试类`中初始化TencentCosStorage对象"""
    tencent_cos = TencentCos(**tencent_cos_config)
    return tencent_cos
