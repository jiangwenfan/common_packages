# 【万维易源服务商】
import requests


class WeatherWanwei:
    """万维易源历史天气数据查询
    https://market.aliyun.com/apimarket/detail/cmapi010812
    """

    def __init__(self, key: str):
        self.key = key
        self.base_url = "https://ali-weather.showapi.com/weatherhistory"

    def get_history_weather(
        self, city_name: str, city_adcode: str, year_month: str
    ) -> list[dict]:
        """获取指定地区、月份的历史天气数据
        :param area: 地区名称，如新安县
        :param month: 年月，格式为YYYYMM， 201601

        :return: 历史天气数据
         {
                "aqiLevel": "6",
                "wind_direction": "西南风",
                "aqi": "406",
                "wind_power": "微风",
                "area": "新安",
                "time": "20160101",
                "min_temperature": "1",
                "max_temperature": "12",
                "aqiInfo": "严重",
                "weather": "晴"
        }
        """
        url = f"{self.base_url}?area={city_name}&month={year_month}"
        headers = {"Authorization": f"APPCODE {self.key}"}
        params = {"area": city_name, "month": year_month}
        response = requests.get(url, headers=headers, params=params)

        # check 1
        if response.status_code != 200:
            raise Exception(f"请求历史天气数据失败，状态码：{response.status_code}")
        res = response.json()

        # check2
        showapi_res_error = res["showapi_res_error"]
        if showapi_res_error != "":
            raise Exception(f"请求历史天气数据失败，错误码：{showapi_res_error}")

        # check3
        showapi_res_body = res["showapi_res_body"]
        remark = showapi_res_body["remark"]
        areaCode_res = showapi_res_body["areaCode"]
        if remark != "查询成功！" or areaCode_res != city_adcode:
            raise Exception(f"请求历史天气数据失败，错误信息：{remark} {areaCode_res}")

        data = showapi_res_body["list"]
        return data
