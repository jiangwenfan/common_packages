# ------ 百度出品 ------:
# 千帆是百度推出的一站式大模型平台，支持多种大模型:
#   - 包括ERNIE模型
#   - 可以接入其他大模型如Llama2、ChatGLM2等
# ERNIE（Enhanced Representation through kNowledge IntEgration）是一种深度语义表示模型,基于Transformer架构
# 文心一言是基于ERNIE模型开发的生成式对话产品，能够进行文学创作、商业文案创作、数理逻辑推理等多种任务
import datetime

import requests


class LLMBaiduErnie:
    """百度出品的ERNIE模型"""

    def __init__(self, client_id: str, client_secret: str):
        self.client_id = client_id
        self.client_secret = client_secret
        self.grant_type = "client_credentials"

    def get_token_info(self) -> dict:
        """获取百度大模型token

        - access_token: 使用大模型的access_token
        - expire_time: token过期时间,通常是30天
        """
        url = f"https://aip.baidubce.com/oauth/2.0/token?grant_type\
={self.grant_type}&client_id={self.client_id}&client_secret={self.client_secret}"
        response = requests.post(url, headers={"Content-Type": "application/json"})
        if response.status_code != 200:
            raise Exception(
                f"百度大模型登录获取token失败: status code: {response.status_code}, response: {response.text}"
            )
        res = response.json()

        # 1. 获取access_token
        access_token = res["access_token"]

        # 当前时间 xxx 秒后到期
        expires_in = res["expires_in"]
        # 当前时间
        current_time = datetime.datetime.now()
        # 2. 过期时间
        expire_time = current_time + datetime.timedelta(seconds=expires_in)

        self.token_info = {"access_token": access_token, "expire_time": expire_time}
        return self.token_info

    def send_model_request(self, text: str, temperature: float = 0.95):
        """发送模型请求
        温度越低,生成的文本越保守,
        温度越高,生成的文本越有创意
        """
        # check1
        if not hasattr(self, "token_info"):
            # 当 token没有被获取时 重新获取token
            self.get_token_info()

        # check2
        access_token = self.token_info["access_token"]
        _expire_time = self.token_info["expire_time"]
        if _expire_time <= datetime.datetime.now():
            # 当 token过期时 重新获取token
            self.get_token_info()
            access_token = self.token_info["access_token"]

        # 3. 构造请求参数
        url = f"https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/chat/\
completions_pro?access_token={access_token}"
        json_data = {
            "messages": [{"role": "user", "content": text}],
            "temperature": temperature,
            "top_p": 0.8,
            "penalty_score": 1,
            "enable_system_memory": False,
            "disable_search": False,
            "enable_citation": False,
        }

        # 4. 发送模型请求
        response = requests.post(
            url,
            headers={"Content-Type": "application/json"},
            json=json_data,
        )
        if response.status_code != 200:
            raise Exception(
                f"百度大模型请求失败: status code: {response.status_code}, response: {response.text}"
            )

        # 5. 返回结果
        res = response.json()
        msg = res["result"]
        return msg

    def is_natural_language(self, text: str) -> bool:
        """判断文本是自然语言还是非自然语言

        True: 自然语言
        False: 非自然语言
        """
        prompt = f"""请判断以下文本是普通自然语言还是代码、配置文件等非自然语言.
如果是自然语言那就返回字符串 "Natural Language",如果是非自然语言,那就返回字符串 "Non-Natural Language",但是不要返回包裹字符串的引号.
需要判断的文本:\n {text} """

        res_status = self.send_model_request(prompt, temperature=0.1)
        match res_status:
            case "Natural Language":
                return True
            case "Non-Natural Language":
                return False
            case _:
                raise Exception(f"未知的返回值: {res_status}")
