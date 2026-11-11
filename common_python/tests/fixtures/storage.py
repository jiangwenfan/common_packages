from pathlib import Path

import pytest

from jwf_common_python.file_storage import LocalStorage, TencentCos


@pytest.fixture(scope="class")
def local_config(tmp_path_factory: pytest.TempPathFactory) -> dict[str, str]:
    """本地存储使用临时目录，无需密钥配置或预先创建目录。"""
    directory: Path = tmp_path_factory.mktemp("local-storage")
    return {"storage_home_dir": str(directory)}


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
