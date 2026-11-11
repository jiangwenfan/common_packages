import datetime

import requests


class WeatherAmap:
    def __init__(self, key: str):
        """
        city: 城市的 adcode，adcode
        extensions: base 返回实时天气, all 返回预报天气
        """
        self.key = key
        self.base_url = (
            f"https://restapi.amap.com/v3/weather/weatherInfo?key={self.key}"
        )

    def _send_request(self, url: str) -> dict:
        response = requests.get(url)
        if response.status_code != 200:
            raise Exception("请求高德地图API失败")
        res = response.json()

        # 1. 校验响应状态
        status = res["status"]
        assert status == "1", f"请求高德地图API失败，status: {status}"
        info = res.get("info")
        assert info == "OK", f"请求高德地图API失败，info: {info}"
        infocode = res.get("infocode")
        assert infocode == "10000", f"请求高德地图API失败，infocode: {infocode}"

        return res

    def get_current_weather(self, city_name: str, city_adcode: str):
        """获取实时/当前天气
        实况天气每小时更新多次，预报天气每天更新3次，分别在8、11、18点左右更新。

        返回结构:
         {
            "province": "河南",
            "city": "新安县",
            "adcode": "410323",
            "weather": "晴",
            "temperature": "19",
            "winddirection": "东南",
            "windpower": "≤3",
            "humidity": "36",
            "reporttime": "2024-10-23 14:00:05",
            "temperature_float": "19.0",
            "humidity_float": "36.0"
        }
        """
        url = f"{self.base_url}&city={city_name}&extensions=base"
        res = self._send_request(url)
        lives_data = res["lives"]

        # check1 结构检查
        assert len(lives_data) == 1
        live_data = lives_data[0]

        assert live_data["city"] == city_name
        assert live_data["adcode"] == city_adcode

        return live_data

    def get_forecast_weather(
        self, city_name: str, city_adcode: str, isTodayForecast: bool = True
    ) -> list[dict]:
        """获取预报/未来天气
        city_name: 城市名
        adcode: 城市的 adcode
        isTodayForecast: 是否获取今天的天气预报
            - True 表示只获取今天的预报天气。list长度为1,仅有今天的数据. [默认值]
            - False 表示获取未来3天的预报天气。list长度为4

        返回的数据结构:
        {
            "date": "2024-10-23",
            "week": "3",
            "dayweather": "晴",
            "nightweather": "晴",
            "daytemp": "20",
            "nighttemp": "9",
            "daywind": "东",
            "nightwind": "东",
            "daypower": "1-3",
            "nightpower": "1-3",
            "daytemp_float": "20.0",
            "nighttemp_float": "9.0"
        }
        """
        url = f"{self.base_url}&city={city_name}&extensions=all"
        res = self._send_request(url)
        forecasts_data = res["forecasts"]

        # check1 结构检查
        assert len(forecasts_data) == 1
        forecast_data = forecasts_data[0]

        # check2 数据准确性检查
        city_res = forecast_data["city"]
        assert city_res == city_name, f"请求的城市名与返回的城市名不一致: {city_res} != {city_name}"
        adcode_res = forecast_data["adcode"]
        assert (
            adcode_res == city_adcode
        ), f"请求的城市adcode与返回的城市adcode不一致: {adcode_res} != {city_adcode}"

        # 解析核心数据
        forecast_core_res = forecast_data["casts"]

        if isTodayForecast:
            # 只获取今天的天气预报

            # 1. 获取今天的日期字符串
            today_datetime: datetime.datetime = datetime.datetime.now()
            today_date: str = today_datetime.strftime("%Y-%m-%d")

            # 2. 获取今天的预报天气数据
            today_forecast_res = forecast_core_res[0]

            # 断言，校验数据获取是否准确
            today_forecast_date = today_forecast_res["date"]
            _msg = f"获取到的预报数据的日期不是今天: 预测日期:'{today_forecast_date}' 实际日期:'{today_date}'"
            assert today_date == today_forecast_date, _msg
            return [today_forecast_res]

        # 获取未来3天的预报天气
        return forecast_core_res
