"""TikOmni 英文字幕下载，支持同步响应和有界异步轮询。"""

import time
from typing import Any, NoReturn, TypeAlias

import requests

from jwf_common_python.parse_subtitle import parse_srt

from .result import build_subtitle_result
from .types import YoutubeSubtitleResult

# 外部 JSON 仅在适配器内部保留动态类型，公开方法始终返回 YoutubeSubtitleResult。
_TikomniData: TypeAlias = dict[str, Any] | str
_RequestParams: TypeAlias = dict[str, str]

_BASE_URL = "https://api.tikomni.com/api/u1/v1/youtube/web_v2/"
_POLL_INTERVAL = 3
_MAX_POLLS = 60


def _request_error(
    exc: requests.RequestException, response: requests.Response | None, token: str
) -> NoReturn:
    # HTTP 错误响应的布尔值为 False，必须通过 is not None 判断是否有响应。
    failed_response = exc.response if exc.response is not None else response
    if failed_response is not None:
        body = failed_response.text.replace(token, "[REDACTED]")
        raise ValueError(
            f"TikOmni 字幕请求失败: HTTP {failed_response.status_code}; 响应: {body}"
        ) from None
    reason = str(exc).replace(token, "[REDACTED]")
    raise ValueError(
        f"TikOmni 字幕请求失败: 未收到 HTTP 响应（无状态码）; "
        f"{type(exc).__name__}: {reason}"
    ) from None


def _decode_response(
    response: requests.Response, params: _RequestParams, token: str
) -> _TikomniData:
    try:
        data = response.json()
    except ValueError:
        # 同步 SRT 允许直接返回字幕文件内容。
        if params.get("language_code"):
            return response.text
        raise ValueError("TikOmni 返回了无效的字幕响应") from None
    # 真实接口在业务数据外包裹 code、message、data 等公共字段。
    # 在请求入口统一解包，字幕列表、内容和异步轮询都使用相同业务结构。
    if isinstance(data, dict) and "code" in data:
        if data["code"] != 200:
            body = response.text.replace(token, "[REDACTED]")
            raise ValueError(
                f"TikOmni 字幕请求返回业务错误: HTTP {response.status_code}; 响应: {body}"
            )
        if "data" not in data or not isinstance(data["data"], (dict, str)):
            raise ValueError("TikOmni 字幕响应缺少有效的 data")
        return data["data"]
    if not isinstance(data, (dict, str)):
        raise ValueError("TikOmni 返回了无效的字幕响应")
    return data


class TikomniSubtitleDownloader:
    """显式传入 api_token；每次 HTTP 请求最多等待 30 秒，轮询最多 180 秒。"""

    def __init__(self, api_token: str) -> None:
        if not api_token:
            raise ValueError("请传入 TikOmni api_token")
        self.api_token = api_token

    def _request(self, endpoint: str, params: _RequestParams) -> _TikomniData:
        """请求并解包上游响应；此处的 SRT 文本不会直接返回给调用方。"""
        response = None
        try:
            response = requests.get(
                _BASE_URL + endpoint,
                params=params,
                headers={"Authorization": f"Bearer {self.api_token}"},
                timeout=30,
            )
            response.raise_for_status()
        except requests.RequestException as exc:
            _request_error(exc, response, self.api_token)
        return _decode_response(response, params, self.api_token)

    def _resolve(self, data: _TikomniData) -> _TikomniData:
        """同步结果直接使用；异步任务在限定次数和截止时间内轮询。"""
        if not isinstance(data, dict) or data.get("status") != "processing":
            return data
        job_id = data.get("job_id")
        if not job_id:
            raise ValueError("TikOmni 异步字幕响应缺少 job_id")
        deadline = time.monotonic() + 180
        for _ in range(_MAX_POLLS):
            if time.monotonic() >= deadline:
                break
            time.sleep(_POLL_INTERVAL)
            data = self._request(
                "get_video_captions_result", {"job_id": job_id, "format": "srt"}
            )
            if not isinstance(data, dict):
                raise ValueError("TikOmni 异步字幕响应格式错误")
            if data.get("status") == "completed":
                return data
            if data.get("status") not in {"queued", "active"}:
                raise ValueError("TikOmni 异步字幕任务失败")
        raise ValueError("TikOmni 字幕处理超时，请稍后显式重试")

    def _get_content(self, video_id: str, data: _TikomniData, language: str) -> str:
        """优先复用列表返回的内容，避免为同一份字幕重复请求。"""
        if (
            not isinstance(data, dict)
            or data.get("language_code") != language
            or "content" not in data
        ):
            data = self._resolve(
                self._request(
                    "get_video_captions",
                    {
                        "video_id": video_id,
                        "language_code": language,
                        "format": "srt",
                    },
                )
            )
        content = data.get("content") if isinstance(data, dict) else data
        if not isinstance(content, str) or not content.strip():
            raise ValueError("TikOmni 未返回有效的字幕内容")
        return content

    def download_youtube_subtitle(self, video_id: str) -> YoutubeSubtitleResult:
        """下载并解析英文字幕，优先人工字幕；返回字典及排序后的字幕条目，不返回 SRT。"""
        data = self._resolve(
            self._request("get_video_captions", {"video_id": video_id})
        )
        language = _select_language(data)
        content = self._get_content(video_id, data, language)
        # a. 是 TikOmni 的自动字幕标记：请求时保留，返回时拆成独立布尔字段。
        return build_subtitle_result(
            video_id=video_id,
            language="English",
            language_code=language.removeprefix("a."),
            is_generated=language.startswith("a."),
            subtitles=parse_srt(content),
        )


def _select_language(data: _TikomniData) -> str:
    """返回上游请求所需的语言标识，可能含自动字幕前缀 a.。"""
    if not isinstance(data, dict):
        raise ValueError("TikOmni 字幕列表格式错误")
    # 列表请求也可能转异步，完成结果会携带语言列表及字幕内容。
    codes = data.get("available_languages")
    if codes is None:
        captions = data.get("captions", [])
        codes = [item["language_code"] for item in captions]
    english = [code for code in codes if code.removeprefix("a.").split("-")[0] == "en"]
    if not english:
        raise ValueError("该视频没有可用的英文字幕")
    # 优先人工英文，其次区域英文，最后自动生成英文。
    return min(english, key=lambda code: (code.startswith("a."), code != "en"))


def download_youtube_subtitle(
    video_id: str, *, api_token: str
) -> YoutubeSubtitleResult:
    """使用显式令牌下载字幕，不读取环境变量或应用框架设置。"""
    return TikomniSubtitleDownloader(api_token).download_youtube_subtitle(video_id)
