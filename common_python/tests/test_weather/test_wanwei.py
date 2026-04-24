class TestWeatherWanwei:
    def test_get_weather(self, weather_wanwei):
        city_name = "新安县"
        city_adcode = "410323"
        res = weather_wanwei.get_history_weather(city_name, city_adcode, "202011")
        assert isinstance(res, list)
        r = res[0]
        # print(r)
        assert len(r["weather"]) > 0
        assert len(r["min_temperature"]) > 0
        assert len(r["max_temperature"]) > 0
