"""腾讯云旧版 TMT 文本翻译的兼容封装。"""

from __future__ import annotations

from typing import Any

from common_python.translate import SentenceInfo, Translate, WordInfo

SDK_REQUIREMENT = "tencentcloud-sdk-python-common>=3.0.1042,<4"


class TencentTranslate(Translate):
    """兼容已有 TMT 账号，SDK 在实例化时加载，请求失败直接抛出异常。

    使用官方 CommonClient 调用 TextTranslate，无需安装 TMT 产品 SDK。
    该接口已发布下线公告，状态见 README。
    """

    def __init__(
        self,
        secret_id: str,
        secret_key: str,
        *,
        region: str = "ap-shanghai",
        endpoint: str = "tmt.tencentcloudapi.com",
        project_id: int = 0,
        timeout: float = 30,
        token: str | None = None,
    ) -> None:
        for name, value in (
            ("secret_id", secret_id),
            ("secret_key", secret_key),
            ("region", region),
            ("endpoint", endpoint),
        ):
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} 不能为空")
        if (
            isinstance(project_id, bool)
            or not isinstance(project_id, int)
            or project_id < 0
        ):
            raise ValueError("project_id 必须为非负整数")
        if timeout <= 0:
            raise ValueError("timeout 必须大于 0")
        if token is not None and (not isinstance(token, str) or not token.strip()):
            raise ValueError("token 必须为非空字符串或 None")

        try:
            from tencentcloud.common.common_client import CommonClient
            from tencentcloud.common.credential import Credential
            from tencentcloud.common.profile.client_profile import ClientProfile
            from tencentcloud.common.profile.http_profile import HttpProfile
        except ImportError as exc:
            raise ImportError(f"请先安装腾讯云公共 SDK：pip install '{SDK_REQUIREMENT}'") from exc

        profile = ClientProfile()
        profile.httpProfile = HttpProfile(endpoint=endpoint, reqTimeout=timeout)
        self.client = CommonClient(
            "tmt",
            "2018-03-21",
            Credential(secret_id, secret_key, token=token),
            region,
            profile,
        )
        self.project_id = project_id
        self._closed = False

    @staticmethod
    def _language_code(code: str) -> str:
        if not isinstance(code, str) or not code.strip():
            raise ValueError("语言代码不能为空")
        return {"zh-CN": "zh"}.get(code, code)

    def translate(
        self,
        word_or_sentence: str,
        source_language_code: str = "en",
        target_language_code: str = "zh",
        *,
        untranslated_text: str | None = None,
    ) -> dict[str, Any]:
        """返回完整 Response 响应体，包括 TargetText、Source、Target、RequestId。

        支持源语言 auto、项目通用的 zh-CN 别名和原生语言代码。
        每次创建独立参数字典；不打印、不写文件、不吞异常。
        """
        if self._closed:
            raise RuntimeError("腾讯翻译客户端已关闭")
        if not isinstance(word_or_sentence, str) or not word_or_sentence.strip():
            raise ValueError("待翻译文本不能为空")
        source = self._language_code(source_language_code)
        target = self._language_code(target_language_code)
        if target == "auto":
            raise ValueError("目标语言不能为 auto")
        if untranslated_text is not None and not isinstance(untranslated_text, str):
            raise TypeError("untranslated_text 必须为字符串或 None")

        params = {
            "SourceText": word_or_sentence,
            "Source": source,
            "Target": target,
            "ProjectId": self.project_id,
        }
        if untranslated_text is not None:
            params["UntranslatedText"] = untranslated_text
        response = self.client.call_json("TextTranslate", params)
        result = response.get("Response") if isinstance(response, dict) else None
        if not isinstance(result, dict) or not isinstance(
            result.get("TargetText"), str
        ):
            raise ValueError("腾讯翻译响应缺少有效的 TargetText")
        return result

    def translate_word(
        self,
        word: str,
        source_language_code: str = "en",
        target_language_code: str = "zh",
    ) -> dict[str, Any]:
        """通过文本接口翻译单词，附带原文 word，供标准化函数使用。"""
        return {
            **self.translate(word, source_language_code, target_language_code),
            "word": word,
        }

    def translate_sentence(
        self,
        sentence: str,
        source_language_code: str = "en",
        target_language_code: str = "zh",
    ) -> dict[str, Any]:
        """翻译句子，附带原文 sentence，供标准化函数使用。"""
        return {
            **self.translate(sentence, source_language_code, target_language_code),
            "sentence": sentence,
        }

    @classmethod
    def format_word_response(cls, response: dict) -> WordInfo:
        """格式化 translate_word 的结果，保留原始响应于 extended_info。

        TMT 不提供词典元数据：词性 Other、频率 0.0、空例句/变体/音频均为
        标准结构占位值；normalized 字段使用原文和译文，不额外推断词形。
        """
        word = response["word"]
        translation = response["TargetText"]
        return {
            "normalized_word": word,
            "display_word": word,
            "translations": [
                {
                    "normalized": translation,
                    "display": translation,
                    "pos_tag": ("Other", "其他"),
                    "frequency": 0.0,
                    "examples": [],
                }
            ],
            "shapes": [],
            "audio_data": b"",
            "extended_info": dict(response),
        }

    @classmethod
    def format_sentence_response(cls, response: dict) -> SentenceInfo:
        """格式化 translate_sentence 的结果；文本接口不提供音频。"""
        return {
            "sentence": response["sentence"],
            "translations": [response["TargetText"]],
            "audio_data": b"",
        }

    @classmethod
    def download_audio_file(cls, url: str) -> bytes:
        raise NotImplementedError("TMT 文本翻译不提供音频，请使用独立的 TTS 服务")

    def close(self) -> None:
        if not self._closed:
            try:
                # SDK 没有公共 close 接口；新版使用 Session，旧版逐请求发送。
                session = getattr(self.client.request.conn, "_session", None)
                if session is not None:
                    session.close()
            finally:
                self._closed = True

    def __enter__(self):
        if self._closed:
            raise RuntimeError("腾讯翻译客户端已关闭")
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        self.close()
