class TestSearchLocationAmap:
    def test_search(self, search_location_amap):
        keyword = "海底捞"
        city_name = "成都市"
        res = search_location_amap.search(keyword, city_name)
        assert isinstance(res, list)
        # 实际上是42个数据
        assert len(res) > 30
        # 2. 校验数据结构
        r = res[0]
        assert len(r["address"]) > 0
        assert len(r["adname"]) > 0
        assert len(r["cityname"]) > 0
