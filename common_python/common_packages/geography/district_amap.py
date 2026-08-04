import requests


class ChinaDistrictAmap:
    """获取中国的行政区域
    使用 高德地图 获取中国的行政区域信息

    city_code: 城市编码。只有市级行政区有citycode。
        - 县/区、城镇/街道 没有自己的citycode,使用所在市的citycode
        - 省级行政区没有citycode
    adcode: 行政区域编码。
        - 省、市、区/县 的adcode是唯一的
        - 城镇/街道 使用所在区/县的adcode
    """

    def __init__(self, key: str):
        self.key = key
        self.base_url = "https://restapi.amap.com/v3/config/district"
        self.country = "中华人民共和国"
        self._ = {
            "810000": "香港特别行政区",
            "820000": "澳门特别行政区",
        }

    def _send_request(
        self,
        url: str,
        name: str | None = None,
        adcode: str | None = None,
        citycode: str | None = None,
    ) -> dict:
        """
        name,adcode,citycode 用于校验和解析有效的districts
         - 默认为None, 校验条件是districts长度是1
         - 如果不为None, districts长度大于1,则根据 name,adcode,citycode 过滤，找到唯一值
        """
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
        # count = res["count"]

        # 2. 校验响应结构
        districts = res["districts"]
        # 符合条件的有效结果
        response_data_info = []
        if (name is not None) and (adcode is not None) and (citycode is not None):
            # 3个同时不是None,进行过滤,此时districts长度 >= 1
            assert len(districts) >= 1, "districts长度必须大于等于1"
            for district in districts:
                if (
                    district["name"] == name
                    and district["adcode"] == adcode
                    and district["citycode"] == citycode
                ):
                    response_data_info.append(district)
        else:
            assert len(districts) == 1
            response_data_info = districts

        # 有效结果只能有1个
        if len(response_data_info) != 1:
            raise Exception(f"未找到符合条件的district, districts: {districts}")

        # 3. 将实际有效的内容进行提取返回
        return response_data_info[0]

    def get_privince(self) -> list[dict]:
        """获取省份

        "citycode": [],
        "adcode": "410000",
        "name": "河南省",
        "center": "113.753094,34.767052",
        "level": "province",
        "districts": []
        """
        url = f"{self.base_url}?key={self.key}&keywords={self.country}"

        china_info = self._send_request(url)

        # 获取国家信息，判断是否是中国
        china_adcode = china_info["adcode"]
        china_name = china_info["name"]
        level = china_info["level"]
        assert china_adcode == "100000"
        assert china_name == self.country
        assert level == "country"

        privinces: list[dict] = china_info["districts"]

        return privinces

    def get_city(self, privince_name: str, privince_adcode: str) -> list[dict]:
        """获取指定省份的所有城市
        privince_name: 省份名称
        privince_adcode: 省份行政区域编码

        但是会跳过:香港特别行政区,澳门特别行政区,这2个属于省单位，但是没有市直接是区
        因为这2个省级单位下面单位直接是 九龙城区 这种区，没有市所以直接跳过


        返回:
        1. 情况1
            "citycode": "0379", # 城市编码
            "adcode": "410300", # 行政区域编码
            "name": "洛阳市",
            "center": "112.453895,34.619702",
            "level": "city",
            "districts": []
        2. 情况2
            _message : "该省单位下面没有市"
        """

        # 跳过对 香港、澳门 下面的区,进行获取区下面(的区)
        if privince_adcode in self._.keys():
            print(f"跳过对 {self._.get(privince_adcode)} 获取下级(市)行政区")
            return [{"_message": "该省单位下面没有市"}]

        url = f"{self.base_url}?key={self.key}&keywords={privince_name}"
        privince_info = self._send_request(url)

        # chekc
        privince_adcode_res = privince_info["adcode"]
        privince_name_res = privince_info["name"]
        level = privince_info["level"]
        assert level == "province"
        assert privince_name_res == privince_name
        assert privince_adcode_res == privince_adcode

        city_info: list[dict] = privince_info["districts"]
        return city_info

    def get_district(
        self, city_name: str, city_code: str, city_adcode: str
    ) -> list[dict]:
        """获取指定城市的所有区/县
        city_name: 城市名称
        city_code: 城市编码
        city_adcode: 城市行政区域编码

        返回结果:
        "citycode": "0379",
        "adcode": "410323",
        "name": "新安县",
        "center": "112.13246,34.728909",
        "level": "district",
        "districts": []
        """
        url = f"{self.base_url}?key={self.key}&keywords={city_name}"
        city_info = self._send_request(
            url, name=city_name, adcode=city_adcode, citycode=city_code
        )

        # check
        city_name_res = city_info["name"]
        city_code_res = city_info["citycode"]
        city_adcode_res = city_info["adcode"]
        level = city_info["level"]

        # 如果是香港、澳门,则level为province
        # --- 暂时不对比citycode了
        if city_name in self._.values() and city_adcode in self._.keys():
            assert level == "province"
        else:
            assert level == "city"

        assert city_name_res == city_name
        assert city_code_res == city_code
        assert city_adcode_res == city_adcode

        district_info: list[dict] = city_info["districts"]
        return district_info
