class TestWeatherAmap:
    def test_get_current_weather(self, weather_amap):
        res = weather_amap.get_current_weather("新安县", "410323")
        assert isinstance(res, dict)
        assert len(res["weather"]) > 0
        assert len(res["temperature"]) > 0

    def test_forecast_weather(self, weather_amap):
        # 1. 只获取当天的天气预报
        res = weather_amap.get_forecast_weather("新安县", "410323")
        assert isinstance(res, list)
        assert len(res) == 1
        for item in res:
            assert len(item["date"]) > 0
            assert len(item["dayweather"]) > 0
            assert len(item["nightweather"]) > 0

        # 2.获取未来3天的天气预报
        res = weather_amap.get_forecast_weather("新安县", "410323", isTodayForecast=False)
        assert isinstance(res, list)
        assert len(res) == 4
        for item in res:
            assert len(item["date"]) > 0
            assert len(item["dayweather"]) > 0
            assert len(item["nightweather"]) > 0
