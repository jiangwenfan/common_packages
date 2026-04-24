# common_packages
封装了一些通用的功能

**安装**
```bash
pip install common_packages-0.1.0.tar.gz
```

[**pypi首页**](https://pypi.org/project/common-packages/#description)


> 可以 README 使用右边的目录进行快速浏览



## 1. db utils
### [x] mysql
**安装依赖**
```bash
```
**使用**
```python
# mysql配置
mysql_config = {
  "host": "xxx"
  "port": xxx
  "user" : "xxx"
  "password" :"xxx"
  "database" : "xxx"
}

mysql_op = MysqlOperator(**mysql_config)

# 接口1: 获取所有表名
tables: set[str] = mysql_op.fetch_all_tables()

# 接口2: 执行`查询sql`,返回执行结果
data: DataFrame, columns: list[str] = mysql_op.fetch_specify_sql_data("SELECT * FROM customers")

# 接口3: 执行`插入sql`，使用指定dataframe数据，指定表名
need_insert_data = [
    {"customer_name": "test1", "email": "test1@gmail.com"},
    {"customer_name": "test2", "email": "test2@gmail.com"},
]
need_insert_dataframe = pd.DataFrame(need_insert_data)
rows: int = mysql_op.insert_database_mysql(need_insert_dataframe, "customers")
```
## 2. file storage
### [x] local storage
```python
# 接口对象
local_config = {
  "storage_home_dir" = "xxx"
}
local = LocalStorage(**local_config)

# 接口1: 写入本地文件内容
file_name: str = "test_save_file.txt"
content: bytes = "abc测试123!@!@".encode()

# file_path 是路径
status: bool, file_path: str = local_obj.save(file_name, content)

# 接口2: 读取本地文件内容
file_name: str = "test_save_file.txt"
content: bytes = "abc测试123!@!@".encode()

status: bool, actual_content: str = local_obj.load(file_name)
```
### [x] tencent cos storage
```python
# 接口对象
tencent_cos_config = {
    "bucket": "xxx",
    "region": "xxx",
    "secret_key": "xxx",
    "secret_id": "xxx"
}
tencent_cos = TencentCos(**tencent_cos_config)

# 接口1: 写入cos文件内容
file_name: str = "test_save_file.txt"
content: bytes = "abc测试123!@!@".encode()

status: bool, actual_file_name: str = tencent_cos_obj.save(
    filename=file_name, content=content
)

# 接口2: 读取cos文件内容
file_name: str = "test_save_file.txt"

status: bool, actual_content: bytes = tencent_cos_obj.load(file_name)
```
## 3. translation
> 封装翻译接口
>

### [x] mircrosoft 翻译
```python
from common_packages.translate import SentenceInfo, WordInfo
from common_packages.translate.microsoft import TranslateMicrosoft

# -------  初始化 -------
config: dict = {
  "text_endpoint": "xxx",
  "word_endpoint": "xxx",
  "word_sample_endpoint": "xxx",
  "location_region": "xxx",
  "key": "xxx",
  "tts_microsoft_config": {
    "key": "xxx",
    "location_region": "xxx",
  }
}
microsoft_obj = TranslateMicrosoft(**config)

# ------- 1. 单词api -------
# 获取原生单词翻译结果
raw_word_translate_res = translate_microsoft_obj.translate_word(
    word="fly",
    source_language_code="en",
    target_language_code="zh-CN",
)
# 格式化为标准结果
res: WordInfo = translate_microsoft_obj.format_word_response(raw_word_translate_res)


# ------- 2. 句子api -------
# 获取原生句子翻译结果
res_tran: dict = translate_microsoft_obj.translate_sentence(
    text=self.text,
    source_language_code=self.source_language_code,
    target_language_code=self.target_language_code,
)
# 格式化为标准结果
res: SentenceInfo = translate_microsoft_obj.format_sentence_response(sentence_translate_data)
```
- 参考：
  - []()
    - 创建文本翻译服务
  - [tts文档](https://learn.microsoft.com/en-us/azure/ai-services/speech-service/index-text-to-speech)
    - 创建tts服务：在`Azure` --> `Azure AI services` --> `语音服务`

- 将要支持的:
  - [ ] google 翻译
  - [ ] Deepl 翻译
  - [ ] openAI 翻译
- 不打算支持的:
  - tencent 翻译,翻译质量较差
  - youdao 翻译

## 4. tts接口
> 封装文本转语音接口

### [x] mircrosoft 文本转语音
依赖:
- import requests
```python
tts_config = {
   key: "xx",
   location_region: "xx",
   language: "en|zh"
}
tts = TTSMicrosoft(tts_config)
audio: bytes = tts.convert_text_to_speech("hello 123")
```

## 5. Ai接口
> 解释句子,分析长难句
- [ ] openAI 翻译
- [ ] gemini 翻译

## 6. sms
腾讯云
```python

```

- [x] 可选导入模块,未安装时,提示安装!
## 7. oauth
[google文档](https://developers.google.com/identity/protocols/oauth2)
- 1. [访问控制台](https://console.developers.google.com/) , 创建相关平台的凭据,选择`OAuth 2.0 客户端 ID`
- 2. [调试范围支持的api](https://developers.google.com/oauthplayground/)
- 3. [范围支持的api](https://developers.google.com/identity/protocols/oauth2/scopes)

google oauth2:
配置文件:
```toml
[oauth2.google]
client_id = "xxx"
client_secret = "xxx"
# 认证完成之后的回调地址,必须与google console中配置的一致
redirect_uri = "http://localhost:9080/aaa"
# 访问权限
scope = "https://www.googleapis.com/auth/userinfo.email https://www.googleapis.com/auth/userinfo.profile"
```
使用:
```python
from common_packages.oauth.google import GoogleOAuth2

config = global_config["oauth2"]["google"]
google_oauth2_obj = GoogleOAuth2(**config)

# 1. 获取授权地址
url = oauth2_google_obj.get_web_auth_url()

# 2. 获取用户信息
user_info = oauth2_google_obj.get_user_info("code 123")
```

## 6. llm 大模型
百度的ernie大模型
配置文件:
```toml
[llm.baidu_ernie]
client_id = "xxxx"
client_secret = "xxxx"
```
使用:
```python
from common_packages.llm.baidu_ernie import LLMBaiduErnie

config = global_config["llm"]["baidu_ernie"]
llm_baidu_ernie_obj =  LLMBaiduErnie(**config)

# 1. 获取大模型回答结果
res: str = llm_baidu_ernie_obj.send_model_request(text)

# 2. 使用大模型判断是否为自然语言
status: bool = llm_baidu_ernie_obj.is_natural_language(text)
```

## 7. geography 地理位置
- [创建高德app](https://console.amap.com/dev/key/app)
- [api文档](https://lbs.amap.com/api/webservice/guide/api/district)
type分类
```
汽车服务
汽车销售
汽车维修
摩托车服务
餐饮服务
购物服务
生活服务
体育休闲服务
医疗保健服务
住宿服务
风景名胜
商务住宅
政府机构及社会团体
科教文化服务
交通设施服务
金融保险服务
公司企业
道路附属设施
地名地址信息
公共设施
事件活动
室内设施
虚拟数据
通行设施

汽车服务|汽车销售|汽车维修|摩托车服务|餐饮服务|购物服务|生活服务|体育休闲服务|医疗保健服务|住宿服务|风景名胜|商务住宅|政府机构及社会团体|科教文化服务|交通设施服务|金融保险服务|公司企业|道路附属设施|地名地址信息|公共设施|事件活动|室内设施|虚拟数据|通行设施
```
使用,查看单元测试文件
- 获取中国中国行政区
- 获取指定位置
```python
```

## 开发协作
打包
```bash
python -m build
```
单元测试:
```bash
pytest
pytest path/to/test_file.py::TestClassName::test_method_name
```