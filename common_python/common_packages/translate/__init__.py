import hashlib
import os
from abc import ABCMeta, abstractmethod
from typing import Literal, TypedDict

# 后端支持的语言代码
# PREF 优化为下面这种形式
LanguageCodeOfBackend = Literal["zh-CN", "zh-TW", "en", "fr", "ja", "de", "es", "ko"]

#  ！！！单词没有词性，只有翻译才有词性！！！
# 翻译词性对照表,用来将词性标准化统一后端实现。
#  HACK 每个提供商都需要实现这个对照表
pos_tag_table = {
    "提供商-词性1": ("Adjectives", "形容词"),
    "提供商-词性2": ("Adverbs", "副词"),
    "提供商-词性3": ("Conjunctions", "连词"),
    "提供商-词性4": ("Determiners", "限定词"),
    "提供商-词性5": ("Verbs", "动词"),
    "提供商-词性6": ("Nouns", "名词"),
    "提供商-词性7": ("Prepositions", "介词"),
    "提供商-词性8": ("Pronouns", "代词"),
    "提供商-词性9": ("Verbs", "动词"),
    "提供商-词性10": ("Other", "其他"),
}


class WordTranslation(TypedDict):
    """单词翻译结果结构"""

    # 2.1 标准化之后的翻译
    normalized: str
    # 用于常见显示的翻译
    display: str

    # 2.2 翻译词性,是 part-of-speech tag 的简写
    # 参考词性对照表.
    #  ("Adjectives", "形容词")
    pos_tag: tuple[str, str]

    # 2.3 翻译频率
    # 数据格式: 10.3 保留一位小数, 页面显示为10.3%
    frequency: float

    # 2.4 翻译的例句
    """
    该单词的翻译例句的结构:
    - 一个单词出现在多个例句中
    - 一个例句有多个翻译
    [
        {
        "sourcePrefix": "前半句",
        "sourceTerm": "关键词",
        "sourceSuffix": "后半句",
        "target": [
            {
                "targetPrefix": "翻译前半句",
                "targetTerm": "翻译关键词",
                "targetSuffix": "翻译后半句",
            }
        ],
    ]
    """
    examples: list[dict]

    # 2.4 翻译前缀
    # prefixWord: str


class WordInfo(TypedDict):
    """单词查询信息结构"""

    # 1. 传入word标准化之后的形式, word表中唯一标识
    normalized_word: str
    # 1.1 用于常见显示的的word, 通常处理大小写
    display_word: str
    # word: str

    # 2. word翻译
    translations: list[WordTranslation]

    # 3. 单词其他变体形式, 例如复数, 过去式等
    shapes: list

    # 4. word的发音数据
    audio_data: bytes
    # speak_url: dict

    # 5. 扩展信息
    extended_info: dict

    # 单词音标
    # phonetic: dict
    # 单词语法信息
    # grammar_info: list


class SentenceInfo(TypedDict):
    """句子查询信息结构"""

    # 1. 原始sentence文本
    sentence: str

    # 2. 翻译之后的文本。部分翻译提供商提供多个翻译
    translations: list[str]

    # 3. 原始sentence的发音数据
    audio_data: bytes
    # source_speak_url: str
    # translation_speak_url: str


class Translate(metaclass=ABCMeta):
    @abstractmethod
    def __init__(self, **kwargs) -> None:
        """\n
        1. 初始化全局配置
        2. 初始化相关翻译/合成对象
        """
        ...

    @abstractmethod
    def translate_word(self, word: str) -> dict:
        """获取简单处理之后的原始word翻译响应"""
        ...

    @abstractmethod
    def translate_sentence(self, sentence: str) -> dict:
        """获取简单处理之后的原始sentence翻译响应"""
        ...

    @classmethod
    def format_word_response(cls, response: dict) -> WordInfo:
        """将原始word翻译响应格式化为标准化的word查询信息"""
        ...

    @classmethod
    def format_sentence_response(cls, response: dict) -> SentenceInfo:
        """将原始sentence翻译响应格式化为标准化的sentence查询信息"""
        ...

    # DEPRE 移除youdao翻译时，删除这个
    @classmethod
    def download_audio_file(cls, url: str) -> bytes:
        ...

    # DEPRECATED youdao翻译时，移动到后端实现
    @classmethod
    def generate_word_audio_file_name(self, word: str, audio_type: str) -> str:
        file_id: str = hashlib.md5(word.encode("utf-8")).hexdigest()
        file_name: str = f"word_youdao_{audio_type}_{file_id}.mp3"
        absolute_audio_file_path = os.path.join("/opt/", file_name)
        return absolute_audio_file_path
