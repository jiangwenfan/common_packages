# jwf-common-python
封装了一些通用的功能

**安装**
```bash
pip install jwf-common-python
```

仓库内开发和运行测试，请先按[开发协作](#开发协作)同步并激活本地环境。

**从旧包迁移**

从 `1.0.0` 起，安装名改为 `jwf-common-python`，导入名改为 `jwf_common_python`。
不再提供 `common_packages` 或 `common_python` 导入路径。调用项目需要更新依赖声明、锁文件及所有导入。

```bash
pip uninstall common-packages
pip install jwf-common-python
```

例如，将 `from common_packages.translate import WordInfo` 改为
`from jwf_common_python.translate import WordInfo`。

[**pypi首页**](https://pypi.org/project/jwf-common-python/#description)


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
from jwf_common_python.translate import SentenceInfo, WordInfo
from jwf_common_python.translate.microsoft import TranslateMicrosoft

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
- 兼容已有服务:
  - [x] tencent TMT 文本翻译，见下方用法及接口下线说明
- 不打算支持的:
  - youdao 翻译

### [x] 腾讯云 TMT 文本翻译（旧接口兼容）

`jwf_common_python.translate.tencent.TencentTranslate` 保留原有文本翻译接口，
补齐单词、句子翻译及标准化结果。密钥、地域、项目 ID、超时均通过参数传入；
导入模块时不加载 SDK，函数不打印、不写文件，SDK 异常直接向调用方传播。

此模块使用官方 `CommonClient` 调用已有 TMT 文本接口，无需安装 TMT 产品 SDK，
也不要求降级其他产品的 SDK。依照[腾讯云下线公告](https://cloud.tencent.com/announce/detail/2482)，
该接口计划于 2027-01-31 停止销售、2030-12-31 停止所有服务。
新项目应参考公告中的替代方案，本模块不自动切换接口。

```bash
pip install 'tencentcloud-sdk-python-common>=3.0.1042,<4'
```

```python
from jwf_common_python.translate.tencent import TencentTranslate

translator = TencentTranslate(
    secret_id="your-secret-id", secret_key="your-secret-key",
    region="ap-shanghai", project_id=0, timeout=30,
    # token="temporary-credential-token",  # 可选临时凭证
)
# 完整 Response 响应体，保留 RequestId 以及未被预定义的服务端字段。
raw = translator.translate("hello", source_language_code="auto", target_language_code="zh-CN")
word = translator.translate_word("apple")
word_info = translator.format_word_response(word)
sentence = translator.translate_sentence("Hello world!")
sentence_info = translator.format_sentence_response(sentence)
translator.close()  # 也可使用 with TencentTranslate(...) as translator:
```

`translate` 每次创建独立参数字典，支持 `untranslated_text` 指定不翻译的内容。
`zh-CN` 自动转换为腾讯的 `zh`，`zh-TW` 保持不变；目标语言不能为 `auto`。
TMT 不提供词典和音频数据，标准化结果中的词性 Other、频率 0.0 及空例句、
变体、音频均为占位值；原始单词响应保留在 `extended_info`。
`download_audio_file` 显式抛出 `NotImplementedError`，音频应由 TTS 服务提供。
支持 `with` 和可重复调用的 `close()`，关闭后不能继续翻译。

离线测试（无需真实密钥、不调用腾讯云服务）：

```bash
pytest tests/test_tencent_translate
```

## 4. tts接口
> 封装文本转语音接口

### [x] Azure（Microsoft）文本转语音

```python
from jwf_common_python.tts.azure import TTSMicrosoft

tts = TTSMicrosoft(key="your-key", location_region="eastasia", language="zh")
audio: bytes = tts.convert_text_to_speech("你好")
```

使用 `requests`，返回 24 kHz WAV 音频。`language="zh"` 使用云健，
`language="en"`（客户端默认值）使用 Andrew Multilingual。网络超时默认 30 秒，
认证或合成失败时抛出异常，不打印令牌或音频数据。

本地真实测试：将 `.env.example` 复制为根目录 `.env`，填写 `AZURE_SPEECH_KEY`
和资源所在区域 `AZURE_SPEECH_REGION`，例如 `eastasia`。可选配置
`AZURE_TTS_LANGUAGE`（手动测试默认 `zh`）和 `AZURE_TTS_TEXT`。
然后在仓库根目录运行：

```bash
pytest tests/test_tts/test_azure_manual.py -m manual -s
```

测试会真实获取令牌并合成一次，保存 `test_temp_data/azure_tts.wav`，
可直接打开试听；重复运行覆盖该测试音频。普通 pytest 默认跳过真实调用。
开发环境已包含测试依赖；该测试无需启动数据库或 Docker 服务。

离线测试（mock HTTP）：

```bash
pytest tests/test_tts/microsoft_test.py tests/test_tts/test_azure_local_config.py
```

### [x] 统一音色目录

```python
from jwf_common_python.tts import TTSVoiceCatalog

voices = TTSVoiceCatalog.get_voices()
```

目前聚合腾讯云本地维护的音色，无需密钥、SDK 或网络请求。
返回列表中每项的顶层固定包含 `name`、`voice_id`、`description`、`gender`、
`supplier`、`category` 和 `other`。六个公共字段保留供应商原始值与类型，
语言、采样率、情感等其他字段自动归入 `other` 字典；无额外字段时为 `{}`。
保持供应商返回顺序，每次返回独立副本，不影响供应商原始接口及其完整数据。

离线单元测试：

```bash
pytest tests/test_tts/test_voice_catalog.py
```

### [x] 腾讯云 TextToVoice 语音合成

依据 Apifox 项目 `8929040` 的接口 `524819309` 实现，使用腾讯云公共 SDK
处理 TC3 签名，无需安装 TTS 产品 SDK：

```bash
pip install 'tencentcloud-sdk-python-common>=3.0.1042,<4'
```

```python
from jwf_common_python.tts.tencent import TTSTencent

voices = TTSTencent.get_voices()  # 返回 tts.py 中的本地音色数据，无需密钥

with TTSTencent(secret_id="your-secret-id", secret_key="your-secret-key") as tts:
    response = tts.text_to_voice("你好", voice_type=1001)
    subtitles = response["Subtitles"]
    request_id = response["RequestId"]
```

- 语音合成只提供 `text_to_voice`，返回完整 `Response` 字典，
  保留 Base64 `Audio`、字幕和请求标识；音频由调用方按需解码。
- `get_voices()` 返回本地维护的音色列表，包含音色 ID、语言、采样率、情感等
  原始字段。返回副本，修改结果不会影响后续调用；不连接腾讯云获取音色。
- 使用长期 SecretId/SecretKey，不发送 Token。可配置 `region`（默认留空）和
  `timeout`（默认 30 秒）；未传 `session_id` 时，每次请求自动生成 UUID。
- 默认开启字幕、WAV 格式、正常语速和音量（`speed=0`、`volume=0`），
  模型 1、中文、16000 Hz。文本和音色 `voice_type` 必须传入，按需覆盖可选业务字段：
  `volume`、`speed`、`project_id`、`model_type`、`fast_voice_type`、
  `primary_language`、`sample_rate`、`codec`、`enable_subtitle`、`segment_rate`、
  `emotion_category`、`emotion_intensity`。复刻音色 200000000 必须提供 `fast_voice_type`。
- 文本长度、SSML、音色与语言/采样率/字幕/情感的兼容性由服务端判定，
  不自动拆分长文本。HTTP 200 中的业务错误也会抛出 SDK 异常，保留错误码和请求 ID。
  不打印或自动保存音频；使用 `with` 或 `close()` 释放连接。

离线单元测试（mock HTTP，不需要真实密钥）：

```bash
pytest tests/test_tts/test_tencent_tts.py tests/test_tts/test_tencent_params.py
```

`test_tencent_tts.py` 和 `test_tencent_params.py` 使用 mock，不调用真实腾讯云。

本地真实测试：先按[开发协作](#开发协作)同步 uv 环境，将根目录 `.env.example` 复制为 `.env`，
填写 `TENCENTCLOUD_SECRET_ID`、`TENCENTCLOUD_SECRET_KEY` 和必填音色
`TENCENT_TTS_VOICE_TYPE`，可修改 `TENCENT_TTS_TEXT` 指定测试文本。
`.env` 已被 Git 忽略。然后在仓库根目录执行：

```bash
source .venv/bin/activate
pytest tests/test_tts/test_tencent_manual.py -m manual -s
```

真实服务测试入口是 `test_tencent_manual.py`，`-m manual` 显式启用真实调用，
`-s` 在终端显示生成文件的路径。开发环境已包含依赖，无需添加 `--noconftest`。

这会真实调用一次腾讯云，保存 `test_temp_data/tencent_tts.wav` 和
`test_temp_data/tencent_tts_response.json`，重复运行会覆盖这两个测试文件。
可直接打开 WAV 试听，JSON 中保留音频、字幕和请求 ID。
开发环境已包含测试依赖；该测试无需启动 MySQL、Docker 等服务。
普通 pytest 默认排除 `manual`；只有显式指定 `-m manual` 才运行该测试。

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
from jwf_common_python.oauth.google import GoogleOAuth2

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
from jwf_common_python.llm.baidu_ernie import LLMBaiduErnie

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

## 英文文本与词表处理

`jwf_common_python.language_utils` 提供文本取词、章节提取、词表过滤、词频统计、
长度排序及网页取词，替代旧 `_other/_language_utils/language.py`。
导入时不扫描目录、不打印、不配置全局日志；处理结果直接返回，不写文件。

```python
from jwf_common_python.language_utils import (
    extract_words, get_chapter_words, word_frequencies, format_words,
    read_word_lists, filter_words, fetch_words_from_pages,
)

words = extract_words(
    "Apple apple banana and pear.",
    exclude_words=["and"], known_words=["pear"],
)
frequencies = word_frequencies(words)  # [("apple", 2), ("banana", 1)]
word_list_text = format_words(words, top_n=100)  # 返回逐行词表文本
chapter_words = get_chapter_words(
    "Chapter One\nHello world!\nChapter Two\nNext chapter",
    "Chapter One", "Chapter Two",
)

# 读取文件时必须显式传入路径；不会自动读取 utils/、files/ 或当前目录词表。
# known = read_word_lists(["data/known.txt", "data/local_words.txt"])
# new_words = filter_words(words, known_words=known, unique=True)
# page_words = fetch_words_from_pages(["https://example.com"], known_words=known)
```

新旧功能对应：

| 旧功能 | 新接口 |
| --- | --- |
| 文本/字幕文件取词、排除无效词和已知词 | `extract_words`、`read_words`、`filter_words` |
| 合并本地词表、读取已掌握词 | `read_word_lists(paths)`，读取并合并所有指定文件 |
| 指定章节取词 | `extract_chapter`、`get_chapter_words` |
| 按词频写词表 | `word_frequencies` 返回计数，`format_words` 返回文本 |
| 长度分组、排序 | `group_words_by_length`、`sort_words_by_length` |
| 首字母大写判断 | `is_title_case_word` |
| URL 文件读取和网页取词 | `read_urls`、`parse_urls`、`fetch_words_from_pages` |
| 数据目录菜单 | `generate_file_menu(directory, prefix="wanglu_")` |

- 保留英文 `[A-Za-z]+` 分词规则，连字符、撇号、数字等均为分隔符，不做词典
  校验或词形还原。文本函数也可接收逐行字符串的可迭代对象。
- 过滤默认忽略大小写、保留原文拼写和重复项；`unique=True` 按首次出现顺序去重，
  `case_sensitive=True` 区分大小写。频率统计默认合并大小写，同频保留首次出现顺序；
  `top_n=None` 返回全部，`top_n=0` 返回空结果。
- 章节标题按去除首尾空白后的整行匹配，默认从最后一次出现的起始标题提取，
  跳过目录中的同名标题；可用 `occurrence` 选择其他位置。只查找起始标题之后的
  结束标题，不包含标题本身；省略结束标题则提取到文末。
- `read_words`、`read_word_lists`、`read_urls` 使用显式路径，默认 UTF-8。
  `generate_file_menu` 返回相对路径列表和菜单文本，默认递归读取 `.txt` 文件，
  可传 `recursive=False` 限定首层。同名文件保留目录前缀，不会混淆。
- 网页取词返回 `{url: 单词列表}`，等待所有任务完成并保留 URL 输入顺序；
  默认 3 个线程、30 秒超时、最短 2 字母并去重。过滤标签及脚本、样式等内容，
  不执行 JavaScript；HTTP/网络错误直接抛出。排除词表支持一次性生成器。
- 已清理无实现的占位函数；词表过滤和长度处理统一由上述接口提供，
  翻译调用使用 `jwf_common_python.translate`，不自动创建输出文件或目录。

离线测试：

```bash
pytest tests/test_language_utils
```

## 有道单词本

Cookie 通过参数传入，函数不读写本地文件、不打印结果。
导出返回每页完整的 JSON 响应，保留单词、释义及其他原始字段；
请求失败时抛出异常，不返回不完整的导出结果。

```python
from jwf_common_python.youdao import fetch_all_wordbook_data, filter_new_words

pages = fetch_all_wordbook_data(cookie="你的完整 Cookie 字符串")
current_words = [
    item["word"]
    for page in pages
    for item in page["data"]["itemList"]
]
new_words = filter_new_words(existing_words=["hello", "world"], current_words=current_words)
```

`fetch_wordbook_data(cookie, limit=15, offset=0, timeout=30)` 可单独获取一页。
`fetch_all_wordbook_data(cookie, limit=15, timeout=30)` 自动分页获取全部响应。
`filter_new_words(existing_words, current_words)` 返回新增单词列表，按当前词表顺序
去重、去除首尾空白、忽略空词，大小写敏感；多行文本需先调用 `splitlines()`。

## 欧路词典生词本

`jwf_common_python.eudic.EudicClient` 提供创建生词本、列出生词本、导入单词和
分页导出功能，替代旧 `oulu.py`。使用项目已有的 `requests` 依赖。

```python
from jwf_common_python.eudic import EudicClient

# token 是完整 Authorization 值，按欧路提供的格式原样传入。
with EudicClient(token="NIS your-token", language="en", timeout=30) as client:
    books = client.list_books()
    created = client.create_book("本周新词")
    book_id = created["data"]["id"]
    imported = client.add_words(book_id, ["hello", "world"])
    pages = client.export_book(book_id)
    current_words = [item["word"] for page in pages for item in page["data"]]
```

- Token、语言、名称和生词本 ID 均由参数提供；`book_id=0` 支持默认生词本。
  创建、列表、导入和单页查询返回完整 JSON，`export_book` 返回所有页的完整响应，
  包括释义等原始字段，不打印、不写文件、不退出进程。
- `get_words(book_id, page=0, page_size=100, sort="asc")` 获取单页，
  `export_book(book_id, page_size=100, sort="asc")` 从第 0 页自动分页。
  接口页码上限为 50；到达上限仍为满页时抛出异常，避免将截断数据作为完整导出。
- `add_words` 单次接受 1～1000 个单词，不隐式创建生词本。默认使用兼容的
  `words` 格式保留已有星级；传 `star=1～5` 时使用推荐的 `items` 格式设置本批星级。
  两种模式均使用 `category_id`。详见[欧路官方 API 文档](https://my.eudic.net/OpenAPI/doc_api_study)。
- HTTP、超时及 JSON 错误直接抛出；使用 `with` 或 `close()` 释放连接。

离线测试（无需 Token、不连接欧路服务）：

```bash
pytest tests/test_eudic
```

## 消息队列

`jwf_common_python.message_queue` 封装 Kafka 和 RabbitMQ 的同步发送、阻塞消费。
按需安装后端依赖，导入模块不会自动连接服务器：

```bash
pip install 'kafka-python>=2.0.2,<3'  # 使用 Kafka
pip install 'pika>=1.3.2,<2'         # 使用 RabbitMQ
```

```python
from jwf_common_python.message_queue import KafkaQueue, RabbitmqQueue

with KafkaQueue(
    bootstrap_servers=["localhost:9092"], topic="events", group_id="workers"
) as queue:
    result = queue.enqueue(b"hello", key=b"user-1")  # 返回 topic、partition、offset
    json_result = queue.enqueue_json({"message": "你好"}, key=b"user-1")
    # queue.consumer(handle_message)  # 阻塞消费，handle_message 接收消息内容

with RabbitmqQueue(
    queue_name="jobs", host="localhost", port=5672,
    username="your-user", password="your-password",
) as queue:
    queue.enqueue(b"hello")
    # queue.consumer(handle_message)
```

- 发送内容使用 `bytes`，Kafka 消费回调也可能收到删除标记 `None`；
  异常直接向调用方传播，不打印或吞掉发送失败。
- Kafka 的 `enqueue_json` 替代旧 `aa.py` 示例，编码为 UTF-8 JSON，等待当前消息
  确认后返回 topic、partition、offset。无需每条消息全局 flush，不可序列化的数据和
  NaN/Infinity 会在连接前报错；不能同时配置 `value_serializer`，避免二次序列化。
- 回调正常返回才确认消息；抛出异常会退出消费。Kafka 仅提交已处理分区的下一条
  offset；RabbitMQ 默认将失败消息重新入队，可传 `requeue_on_error=False` 改为拒绝
  （配置了死信队列时进入死信队列，否则丢弃）。回调应能处理重复投递。
- Kafka 连接按需创建，消费必须提供 `group_id`；`producer_config` 和
  `consumer_config` 可透传 SSL/SASL 等 SDK 参数，不能覆盖消费的手动确认配置。
- RabbitMQ 默认持久化队列及消息，开启发布确认、强制路由，预取数为 1；
  迁移已有非持久化队列时传 `durable=False`。`connection_config` 可设置
  `virtual_host`、SSL 等参数。消费退出时会关闭该实例连接。
- 使用 `with` 或 `close()` 释放资源，实例不支持跨线程共享。

离线测试（需安装两个后端依赖，不需要启动服务器）：

```bash
pytest tests/test_message_queue
```

## ClickHouse 和 Elasticsearch

工具位于 `jwf_common_python.db_utils`，导入时不加载对应 SDK，不依赖 Django
或业务模型；连接配置通过参数传入。所有方法直接返回结果，SDK 异常向调用方传播。

```bash
pip install 'clickhouse-driver>=0.2.6,<0.3' 'pandas>=2.1,<3' 'numpy>=1.26,<3'
pip install 'elasticsearch>=8,<9'  # 以下示例使用 Elasticsearch 8.x 客户端
```

Elasticsearch 客户端主版本应与服务端匹配，参见[官方兼容性说明](https://www.elastic.co/docs/reference/elasticsearch/clients/python#compatibility)。

```python
from jwf_common_python.db_utils import ClickhouseOperator, ElasticsearchHandle

# ClickHouse 原生 TCP 端口为 9000，支持 secure、connect_timeout 等驱动参数。
with ClickhouseOperator(host="localhost", port=9000, database="analytics") as ck:
    tables = ck.fetch_all_tables()
    frame, columns, count = ck.fetch_specify_sql_data(
        "SELECT * FROM events WHERE name = %(name)s",
        params={"name": "example"},
        replace_nonwords=False,
    )
    converted = ck.convert_datatype_for_ck(frame)
    # inserted = ck.insert_specify_sql("INSERT INTO events VALUES", converted)

with ElasticsearchHandle(
    hosts="http://localhost:9200", index="articles",
    # basic_auth=("username", "password"),  # 也支持 api_key、TLS 和超时配置
) as es:
    # 输入可为生成器，由调用方从数据库或其他来源准备文档。
    imported = es.init_data([{"id": 1, "content": "hello world"}], refresh="wait_for")
    result = es.search_doc("hello", field="content", size=10, offset=0)
    updated = es.update_data(1, {"content": "updated"})
    # created = es.create_data(2, {"content": "new"})
    # deleted = es.delete_doc(2)
```

- ClickHouse 保留原有查询、转换、写入接口，新增 `execute(sql, params=...)`。
  category 转字符串时保留空值，返回副本，不修改传入 DataFrame。普通 SQL
  可传 `settings={"use_numpy": False}`，无需安装 pandas/NumPy。
- Elasticsearch 的 `hosts` 和 `index` 必须显式传入。`init_data(documents)`
  仅在索引不存在时创建索引，已有索引不重建；文档默认使用 `id` 字段。
  `bulk_create` 默认每批 500 条，可配置 `id_field`、`chunk_size`、`refresh`。
  重复 ID 抛出冲突，不覆盖已有文档；批量操作不是事务，部分成功不会回滚。
- Elasticsearch 增删改查返回完整响应体；`update_data` 接收部分字段字典，
  不需要再包一层 `doc`。`search` 可直接传查询 DSL，`show_info` 保留默认搜索页行为。
- 两个工具均支持 `with` 和可重复调用的 `close()`；关闭后不能继续查询。

离线测试（安装上述依赖即可，无需启动服务）：

```bash
pytest tests/test_db_utils
```

## 视频合并

`jwf_common_python.video` 使用本机 FFmpeg/ffprobe，提供视频探测和不重新编码的
合并功能，替代旧 `_merge_video.py`，无需额外 Python 依赖。
调用前需安装 FFmpeg，并确保 `ffmpeg`、`ffprobe` 位于 PATH，或通过参数传入完整路径。

```python
from jwf_common_python.video import merge_videos, merge_directory, probe_video

# 输入顺序就是合并顺序。输出父目录必须已存在，返回输出的绝对 Path。
output = merge_videos(
    ["clips/part1.mp4", "clips/part2.mp4"],
    "results/merged.mp4",
    timeout=300,
)
metadata = probe_video(output)  # 完整 ffprobe JSON，含 streams 和 format

# 也可合并目录首层 MP4，按自然文件名排序：clip2 在 clip10 之前。
# output = merge_directory("clips", "results/all.mp4", overwrite=True)
```

- `merge_videos` 保留指定顺序；重复输入表示重复该片段。
  `merge_directory` 默认选择 `.mp4`（大小写均支持），自动排除已有目标文件；
  可通过 `extensions=(".mp4", ".mkv")` 选择其他封装格式。
- 使用[FFmpeg concat demuxer](https://ffmpeg.org/ffmpeg-formats.html#concat)
  和流复制，不再逐文件生成 TS。合并前检查流数量和顺序、编码、时间基、
  分辨率、帧率、音频采样率及声道等主要参数；不兼容时抛出异常，不自动转码。
  封装和时间戳仍由 FFmpeg 处理，不保证不同来源视频的无缝音画拼接。
- 通过参数数组执行，不经过 Shell；支持空格、中文和单引号文件名。
  受 concat 清单格式限制，输入路径不能包含换行符。
- 输出格式由扩展名决定，必须支持输入流编码。默认拒绝覆盖，显式传
  `overwrite=True` 才替换已有输出；目标不能是输入文件或其别名。
  先在独立临时目录生成并探测结果，再提交输出，失败保留已有目标和源文件。
  不支持硬链接的文件系统会退回独占复制；仅清理本次产生的文件。
- 不自动创建业务目录、不打印、不配置全局日志。缺少工具、参数不一致、
  非零退出码、错误日志及超时均抛出异常。`CalledProcessError.stderr` 保留
  FFmpeg 诊断；`timeout` 对每个子进程生效，合并默认不限制总处理时间。
- 旧 `VideoMerge.change()` 的目录流程由 `merge_directory` 替代；
  TS 转换和全目录 TS 清理方法已移除。

测试（安装 FFmpeg 后会生成短视频，验证音轨、时长、帧顺序和失败清理）：

```bash
pytest tests/test_video
```

## GitHub Webhook

`jwf_common_python.github` 替代旧 `_github_hooks.py`，密钥通过参数传入，
不创建全局应用、不启动服务器、不打印签名或密钥、不配置全局日志。
验签使用标准库，不需要 Flask；可选 HTTP 接入才需要安装：

```bash
pip install 'Flask>=3,<4'
```

```python
import os
from jwf_common_python.github import create_webhook_app, verify_signature

secret = os.environ["GITHUB_WEBHOOK_SECRET"]
# 返回 Flask 应用对象，由调用方自行部署或启动。
app = create_webhook_app(secret, path="/hook")
# 也可在其他框架中调用 verify_signature(raw_body, secret, signature_header)。
```

- `verify_signature(payload, secret, signature_header)` 接收原始请求体 bytes、
  str/bytes 密钥和 `X-Hub-Signature-256` 请求头，返回 bool。缺失、格式错误或
  不匹配的签名返回 False；配置及参数类型错误抛出异常。不能先解析再序列化 JSON。
  实现及测试参考[GitHub 官方验签文档](https://docs.github.com/en/webhooks/using-webhooks/validating-webhook-deliveries)。
- `create_webhook_app` 对 POST 请求先验签。失败返回 HTTP 403，通过后返回
  `{"status": 200}`；GET 返回 405。可传 `handler(payload, event, delivery_id)`
  接收原始请求体、事件名和投递 ID，只有回调成功才返回成功响应。
  回调异常交由 Flask 处理，不被包装成成功；请求体解析由回调负责。
- event 和 delivery_id 来自请求头，签名仅保护请求体；事件筛选及投递去重由业务方处理。
  只创建应用不会向 GitHub 发请求，也不会绑定默认端口。

离线测试（HTTP 部分使用 Flask 本地测试客户端）：

```bash
pytest tests/test_github
```

## 开发协作

本地依赖管理使用 [uv](https://docs.astral.sh/uv/)，需要 Python 3.11 或更高版本。
安装 uv 后，在仓库根目录同步并激活环境；命令自动创建 `.venv`，
安装项目各模块开发和测试需要的 SDK、数据库客户端等依赖：

```bash
uv sync --locked
source .venv/bin/activate
```

`pyproject.toml` 声明依赖范围，`uv.lock` 锁定解析结果，两者均纳入版本控制。
开发依赖统一声明在 `dev` 组，`uv sync` 默认安装，包含 YouTube 字幕客户端。
每次打开新终端后执行 `source .venv/bin/activate`，即可直接使用 `python`、`pytest`。

添加依赖与更新锁文件：

```bash
uv add package-name
uv add --dev package-name
uv lock --upgrade
```

单元测试（默认排除 `manual`）：

```bash
pytest
pytest path/to/test_file.py::TestClassName::test_method_name
```

普通测试使用 mock 或临时文件，不需要真实密钥或运行中的数据库。
真实外部服务测试必须显式指定 `-m manual`；TTS 按供应商章节配置根目录 `.env`，
历史集成测试依赖 `tests/secret.toml`（格式参考 `tests/secret.toml.sample`），
其中 MySQL 集成测试还需要本地 Docker 服务。

构建源码包与 wheel：

```bash
uv build
```
