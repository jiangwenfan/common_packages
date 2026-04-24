import hashlib
import logging
import random
import time
import uuid
from typing import Literal, get_args

try:
    import requests
except ImportError:
    raise ImportError("Couldn't import requests. pip install --upgrade requests")
from requests.models import Response

from common_packages.translate import SentenceInfo, Translate, WordInfo

LanguageCodeOfYoudao = Literal["zh-CHS", "zh-CHT", "en", "fr", "ja", "de", "es", "ko"]
LanguageCodeOfBackend = Literal["zh-CN", "zh-TW", "en", "fr", "ja", "de", "es", "ko"]


class YoudaoTranslate(Translate):
    def __init__(self, **kwargs) -> None:
        if not {"YOUDAO_URL", "APP_KEY", "APP_SECRET"}.issubset(kwargs.keys()):
            raise Exception("you need to set YOUDAO_URL,APP_KEY,APP_SECRET")
        self.YOUDAO_URL = kwargs["YOUDAO_URL"]
        self.APP_KEY = kwargs["APP_KEY"]
        self.APP_SECRET = kwargs["APP_SECRET"]
        self._language_code_of_youdao = list(get_args(LanguageCodeOfYoudao))

    def _encrypt(self, salt, current_time, word):
        signStr = (
            self.APP_KEY + self._truncate(word) + salt + current_time + self.APP_SECRET
        )
        hash_algorithm = hashlib.sha256()
        hash_algorithm.update(signStr.encode("utf-8"))
        return hash_algorithm.hexdigest()

    def _truncate(self, q):
        if q is None:
            return None
        size = len(q)
        return q if size <= 20 else q[0:10] + str(size) + q[size - 10 : size]

    def change_language_code(
        self, language_code_of_backend: LanguageCodeOfBackend
    ) -> str:
        """转换语言代码,将language_backend后端的语言代码转换为youdao的语言代码"""

        match language_code_of_backend:
            case "zh-CN":
                return "zh-CHS"
            case "zh-TW":
                return "zh-CHT"
            case _:
                return language_code_of_backend

    def _send_request(
        self,
        word: str,
        source_language_code: LanguageCodeOfBackend,
        target_language_code: LanguageCodeOfBackend,
    ) -> dict:
        """_summary_

        Args:
            word (str): _description_
            source_language_code (str): 待翻译文本的语言代码
            target_language_code (str): 目标语言代码

        Raises:
            ValueError: _description_
            ValueError: _description_

        Returns:
            dict: _description_
        """
        current_time = str(int(time.time()))
        salt = str(uuid.uuid1())
        sign = self._encrypt(salt=salt, current_time=current_time, word=word)

        # 解决不同提供商对简体中文的表示问题
        source_language_code = self.change_language_code(source_language_code)
        target_language_code = self.change_language_code(target_language_code)
        assert (
            source_language_code in self._language_code_of_youdao
        ), f"youdao不支持 {source_language_code} 语言code"
        assert (
            target_language_code in self._language_code_of_youdao
        ), f"youdao不支持 {target_language_code} 语言code"

        data = {
            "from": source_language_code,
            "to": target_language_code,
            "signType": "v3",
            "curtime": current_time,
            "sign": sign,
            "appKey": self.APP_KEY,
            "salt": salt,
            "q": word,
            # 'vocabId':"您的用户词表ID"
        }

        try:
            response: Response = requests.post(
                self.YOUDAO_URL,
                data=data,
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            )
        except Exception as e:
            raise ValueError(f"youdao translate connect error: {e}")
        if response.status_code != 200:
            raise ValueError(f"youdao translate status error: {response.status_code}")
        return response.json()

    def translate(
        self,
        word: str,
        source_language_code: LanguageCodeOfBackend,
        target_language_code: LanguageCodeOfBackend,
    ) -> dict:
        response: dict = self._send_request(
            word=word,
            source_language_code=source_language_code,
            target_language_code=target_language_code,
        )
        # 频率过快时,自动重试
        num = 1
        while response["errorCode"] in ["411", "412", "2411", "3411", "4411", "11411"]:
            sleep_time: float = round(random.uniform(1, 5), 2)
            logging.warning(f"youdao请求速度过快,{sleep_time}秒后自动重试,进行第{num}次重试")
            time.sleep(sleep_time)
            response = self._send_request(
                word=word,
                source_language_code=source_language_code,
                target_language_code=target_language_code,
            )
            num += 1

        error_code: str = response["errorCode"]
        if error_code != "0":
            raise ValueError(f"youdao translate error: {word} {error_code=}")
        return response

    @classmethod
    def format_word_response(cls, response: dict) -> WordInfo:
        # only word
        basic_direction: dict | None = response.get("basic")

        word: str = response["query"]

        translation_no_class: list[str] = response["translation"]

        translation_have_class: list[str] | None = (
            basic_direction.get("explains", []) if basic_direction else []
        )
        translation = {
            "no_class": translation_no_class,
            "have_class": translation_have_class,
        }

        translation_speak_url: str = response["tSpeakUrl"]
        source_speak_url: str = response["speakUrl"]
        source_speech_uk: str | None = (
            basic_direction.get("uk-speech") if basic_direction else None
        )
        source_speech_us: str | None = (
            basic_direction.get("us-speech") if basic_direction else None
        )
        speakUrl = {
            "translation_speak_url": translation_speak_url,
            "source_speak_url": source_speak_url,
            "source_speech_uk": source_speech_uk,
            "source_speech_us": source_speech_us,
        }

        phonetic_us: str | None = (
            basic_direction.get("us-phonetic") if basic_direction else None
        )
        phonetic: str | None = (
            basic_direction.get("phonetic") if basic_direction else None
        )
        phonetic_uk: str | None = (
            basic_direction.get("uk-phonetic") if basic_direction else None
        )
        phonetic = {"us": phonetic_us, "uk": phonetic_uk, "default": phonetic}

        word_type: list[str] | None = (
            basic_direction.get("exam_type") if basic_direction else None
        )

        grammar_info: list[dict] | None = (
            basic_direction.get("wfs") if basic_direction else None
        )

        extended_info: list[dict[str, list[str]]] | None = response.get("web")

        format_response: WordInfo = {
            "word": word,
            "translation": translation,
            "speak_url": speakUrl,
            "phonetic": phonetic,
            "word_type": word_type,
            "grammar_info": grammar_info,
            "extended_info": extended_info,
        }
        # import json
        # print(json.dumps(res,indent=2,ensure_ascii=False))
        return format_response

    @classmethod
    def format_sentence_response(cls, response: dict) -> SentenceInfo:
        sentence: str = response["query"]
        translation: list[str] = response["translation"]

        source_speak_url: str = response["speakUrl"]
        translation_speak_url: str = response["tSpeakUrl"]

        response = {
            "sentence": sentence,
            "translation": translation,
            "source_speak_url": source_speak_url,
            "translation_speak_url": translation_speak_url,
        }

        return response

    @classmethod
    def download_audio_file(self, url: str) -> bytes:
        try:
            response = requests.get(url=url)
        except Exception as e:
            raise ValueError(f"youdao translate download audio file error: {e}")
        if response.status_code != 200:
            raise ValueError("download audio file,status code error")
        return response.content
