import pytest

from common_packages.weather.amap import WeatherAmap
from common_packages.weather.wanwei import WeatherWanwei


@pytest.fixture(scope="class")
def weather_amap(global_config):
    """用于在`每个测试用例`中获取高德天气数据查询对象"""
    config = global_config["weather"]["amap"]
    weather_amap = WeatherAmap(**config)
    return weather_amap


@pytest.fixture(scope="class")
def weather_wanwei(global_config):
    """用于在`每个测试用例`中获取万维易源历史天气数据查询对象"""
    config = global_config["weather"]["wanwei"]
    weather_wanwei = WeatherWanwei(**config)
    return weather_wanwei
