import json
import sys

sys.path.append("..")
import json
import logging

from common_packages.translate_utils.tencent import TencentTranslate
from common_packages.translate_utils.youdao import YoudaoTranslate

from . import get_config

logging.basicConfig(level=logging.INFO)


class TestTencentTranslate:
    def test_translate_sentence(self):
        config: dict = get_config()
        youdao = TencentTranslate(**config["translate"]["tencent"])
        sentence_response: dict = youdao.translate(
            "The following quickstarts demonstrate how to create a custom Voice Assistant",
            source_language_code="en",
            target_language_code="zh",
        )
        print(sentence_response)
        # assert len(sentence_response) > 1
