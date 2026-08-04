import time
import requests


class SearchLocationAmap:
    """高德地图API搜索地理位置
    - 使用2.0版本的API
    """

    def __init__(self, key: str):
        self.key = key
        self.page_size = 10
        self.types = "汽车服务|汽车销售|汽车维修|摩托车服务|餐饮服务|购物服务|生活服务\
|体育休闲服务|医疗保健服务|住宿服务|风景名胜|商务住宅|政府机构及社会团体|科教文化服务\
|交通设施服务|金融保险服务|公司企业|道路附属设施|地名地址信息|公共设施|事件活动|室内设施|虚拟数据|通行设施"
        self.base_url = f"https://restapi.amap.com/v5/place/text?key={self.key}\
&types={self.types}&city_limit=true&page_size={self.page_size}"

    def _request(self, url: str):
        response = requests.get(url)
        if response.status_code != 200:
            raise Exception(f"请求失败，状态码：{response.status_code}")

        res = response.json()
        if res["info"] != "OK":
            raise Exception(f"请求失败，错误信息：{res['info']}")
        return res

    def search(
        self,
        keyword: str,
        city_name: str,
    ) -> list[dict]:
        """搜索指定城市,指定地理位置.
        keywords: 地点关键字,需要被检索的地点文本信息。
        city_name: 搜索区划, citycode，adcode，cityname；cityname 仅支持城市级别和中文，如“北京市”。

        返回数据示例:
        {
            "parent": "",
            "address": "通衢路19号",
            "distance": "",
            "pcode": "410000",
            "adcode": "410311",
            "pname": "河南省",
            "cityname": "洛阳市",
            "type": "交通设施服务;火车站;火车站",
            "typecode": "150200",
            "adname": "洛龙区",
            "citycode": "0379",
            "name": "洛阳龙门站",
            "location": "112.456291,34.593842",
            "id": "B017B02U7H"
        },
        """
        # check
        # 文本总长度不可超过80字符，这里限制为50
        if len(keyword) > 50:
            raise ValueError("keywords长度不能超过50")

        res = []
        num = 1

        while True:
            # 1. 获取数据
            url = (
                f"{self.base_url}&keywords={keyword}&region={city_name}&page_num={num}"
            )
            response = self._request(url)

            # 2. 更新数据
            pois = response["pois"]
            res.extend(pois)

            # 3. 判断是否进行下一页的数据获取
            if int(response["count"]) != self.page_size:
                # 本次请求返回的数据个数 不等于 page_size,说明本次请求是最后一页. 数据获取完毕
                break
            else:
                # 存在下一页, 更新num
                num += 1
                # 限制请求次数,避免出现1秒超过3次的限制
                time.sleep(1)
        return res
