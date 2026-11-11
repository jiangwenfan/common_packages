"""聚合供应商音色，统一公共字段与供应商扩展字段。"""

from copy import deepcopy
from typing import Any

from .tencent import TTSTencent

_COMMON_FIELDS = (
    "name",
    "voice_id",
    "description",
    "gender",
    "supplier",
    "category",
)


class TTSVoiceCatalog:
    """提供统一音色目录，目前包含腾讯云本地维护的音色。"""

    @staticmethod
    def get_voices() -> list[dict[str, Any]]:
        """返回六个公共字段及 other；无需密钥，保持供应商音色顺序。"""
        voices: list[dict[str, Any]] = []
        for source in TTSTencent.get_voices():
            # 深拷贝嵌套扩展数据，避免调用方修改供应商数据或后续结果。
            source = deepcopy(source)
            voice = {field: source[field] for field in _COMMON_FIELDS}
            voice["other"] = {
                key: value
                for key, value in source.items()
                if key not in _COMMON_FIELDS
            }
            voices.append(voice)
        return voices
