"""文本转语音服务，腾讯云 SDK 在创建客户端时按需加载。"""

from .catalog import TTSVoiceCatalog
from .tencent import TTSTencent, TextToVoiceOptions

__all__ = ["TTSTencent", "TextToVoiceOptions", "TTSVoiceCatalog"]
