import pytest

from common_packages.geography.district_amap import ChinaDistrictAmap
from common_packages.geography.search_amap import SearchLocationAmap


@pytest.fixture(scope="class")
def china_district_amap(global_config):
    """用于在`每个测试用例`中高德地图区获取中国行政区划信息对象"""
    config = global_config["geography"]["amap"]
    china_dis_obj = ChinaDistrictAmap(**config)
    return china_dis_obj


@pytest.fixture(scope="class")
def search_location_amap(global_config):
    """用于在`每个测试用例`中使用高德地图搜索指定对象"""
    config = global_config["geography"]["amap"]
    search_loc_obj = SearchLocationAmap(**config)
    return search_loc_obj
