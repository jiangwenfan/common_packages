"""Azure Speech REST 文本转语音封装。"""

from typing import Literal
from xml.sax.saxutils import escape

import requests

LanguageType = Literal["en", "zh"]
AudioStyle = {
    "en": {
        "language_code": "en-US",
        "name": "en-US-AndrewMultilingualNeural",
    },
    "zh": {
        "language_code": "zh-CN",
        "name": "zh-CN-YunjianNeural",
    },
}


class TTSMicrosoft:
    """通过所在区域的 Azure Speech 资源获取令牌并合成 WAV 音频。"""

    def __init__(
        self, key: str, location_region: str, language: LanguageType = "en",
        *, timeout: float = 30,
    ) -> None:
        self.location_region = location_region
        self.key = key
        self.language = language
        self.timeout = timeout
        self.user_agent = "language_backend"
        self.access_token_url = (
            f"https://{location_region}.api.cognitive.microsoft.com/sts/v1.0/issueToken"
        )
        self.txt_to_speech_url = (
            f"https://{location_region}.tts.speech.microsoft.com/cognitiveservices/v1"
        )
        # 默认输出单声道、24 kHz、16 bit PCM 的 WAV 音频。
        self.output_format = "riff-24khz-16bit-mono-pcm"
        self.gender = "Male"
        self.language_code = AudioStyle[language]["language_code"]
        self.name = AudioStyle[language]["name"]

    def fetch_access_token(self) -> str:
        """获取访问令牌；认证失败时直接抛出 HTTP 异常。"""
        response = requests.post(
            self.access_token_url,
            headers={"Ocp-Apim-Subscription-Key": self.key},
            timeout=self.timeout,
        )
        response.raise_for_status()
        return response.text

    def generate_xml_data(self, text: str) -> str:
        """将普通文本转成 SSML，转义 XML 特殊字符。"""
        return (
            f"<speak version='1.0' xml:lang='{self.language_code}'>"
            f"<voice xml:lang='{self.language_code}' xml:gender='{self.gender}' "
            f"name='{self.name}'>{escape(text)}</voice></speak>"
        )

    def convert_text_to_speech(self, text: str) -> bytes:
        """返回 WAV 音频 bytes，不打印或保存音频；网络及 HTTP 错误直接抛出。"""
        response = requests.post(
            self.txt_to_speech_url,
            headers={
                "Content-Type": "application/ssml+xml",
                "X-Microsoft-OutputFormat": self.output_format,
                "User-Agent": self.user_agent,
                "Authorization": f"Bearer {self.fetch_access_token()}",
            },
            data=self.generate_xml_data(text).encode("utf-8"),
            timeout=self.timeout,
        )
        response.raise_for_status()
        return response.content
