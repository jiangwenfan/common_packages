"""SRT 文本解析，不依赖下载服务或文件存储。"""

import re

from .types import SubtitleItem


def parse_srt(content: str) -> list[SubtitleItem]:
    """将 SRT 文本解析为字幕条目，时间以秒表示；非法格式抛出 ValueError。"""
    subtitles = []
    for block in re.split(
        r"\n\s*\n", content.replace("\r\n", "\n").strip().lstrip("\ufeff")
    ):
        match = re.fullmatch(
            r"\d+\n(\d{2,}):(\d{2}):(\d{2}),(\d{3}) --> "
            r"(\d{2,}):(\d{2}):(\d{2}),(\d{3})[^\n]*\n(.+)",
            block,
            re.DOTALL,
        )
        if not match:
            raise ValueError("SRT 字幕格式错误")
        numbers = list(map(int, match.groups()[:8]))
        start = numbers[0] * 3600 + numbers[1] * 60 + numbers[2] + numbers[3] / 1000
        end = numbers[4] * 3600 + numbers[5] * 60 + numbers[6] + numbers[7] / 1000
        if end < start or any(numbers[index] >= 60 for index in (1, 2, 5, 6)):
            raise ValueError("SRT 字幕时间轴无效")
        text = match.group(9).strip()
        if text:
            subtitles.append({"text": text, "start": start, "duration": end - start})
    return subtitles
