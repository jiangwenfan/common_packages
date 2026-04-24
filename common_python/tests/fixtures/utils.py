import docker

import tomllib

import pytest


@pytest.fixture(scope="session")
def global_config():
    """用于在`整个测试会话`中获取全局配置"""
    # TODO validate config

    # read config
    with open("tests/secret.toml", "rb") as f:
        try:
            config: dict = tomllib.load(f)
        except Exception as e:
            raise f"load config failed, error: {e}"
    return config


def parse_container_status(container_name) -> str:
    """解析容器状态"""

    client = docker.from_env()

    # 获取容器对象
    container = client.containers.get(container_name)

    container_info = container.attrs  # 获取容器的详细信息

    # 获取容器的健康检查状态
    health_status = (
        container_info.get("State", {})
        .get("Health", {})
        .get("Status", "No health check")
    )
    return health_status
