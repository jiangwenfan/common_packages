import json
import sys

sys.path.append("..")
import json
import logging

from _other._tencent import TencentTranslate
from common_packages.translate._youdao import YoudaoTranslate

from .. import get_config

logging.basicConfig(level=logging.INFO)


class TestYoudaoTranslate:
    def test_translate_word(self):
        # config: dict = get_config()
        # youdao = YoudaoTranslate(**config["translate"]["youdao"])
        word_response: dict = youdao.translate(
            "apple", source_language_code="en", target_language_code="zh-CN"
        )
        assert len(word_response) > 1
        response = json.dumps(word_response, indent=4, ensure_ascii=False)
        print(f"youdao translate word: {response=}")

    def test_translate_words(self):
        """测试多个单词快速请求,触发重试"""
        config: dict = get_config()
        youdao = YoudaoTranslate(**config["translate"]["youdao"])
        for word in [
            "apple",
            "banana",
            "orange",
            "pear",
            "watermelon",
            "grape",
            "peach",
            "lemon",
            "strawberry",
            "cherry",
            "mango",
            "pineapple",
            "coconut",
            "pomegranate",
            "blueberry",
            "raspberry",
            "blackberry",
            "apricot",
            "avocado",
            "fig",
        ]:
            word_response: dict = youdao.translate(
                word, source_language_code="en", target_language_code="zh-CN"
            )
            # assert len(word_response) > 1
            # response = json.dumps(word_response, indent=4, ensure_ascii=False)
            # print(f"youdao translate word: {response=}")

    def test_translate_sentence(self):
        config: dict = get_config()
        youdao = YoudaoTranslate(**config["translate"]["youdao"])
        sentence_response: dict = youdao.translate(
            "The following quickstarts demonstrate how to create a custom Voice Assistant",
            source_language_code="en",
            target_language_code="ja",
        )
        assert len(sentence_response) > 1
        print(sentence_response)

    def test_format_word(self):
        res: dict = YoudaoTranslate.format_word_response(
            response={
                "returnPhrase": ["apple"],
                "query": "apple",
                "errorCode": "0",
                "l": "en2zh-CHS",
                "tSpeakUrl": "https://openapi.youdao.com/ttsapi?q=%E8%8B%B9%E6%9E%9C&langType=zh-CHS&sign=99EDBB223953B8F0C97E27B9CD306484&salt=1694583954151&voice=4&format=mp3&appKey=59c4b2a39ab77960&ttsVoiceStrict=false&osType=api",
                "web": [
                    {"value": ["苹果公司"], "key": "Apple"},
                    {"value": ["苹果公司", "美国苹果公司", "苹果"], "key": "apple inc"},
                    {"value": ["大苹果", "纽约", "大苹果城"], "key": "BIG APPLE"},
                ],
                "requestId": "c8e92ddd-2ee6-4508-ab57-544e6b35ea9b",
                "translation": ["苹果"],
                "mTerminalDict": {
                    "url": "https://m.youdao.com/m/result?lang=en&word=apple"
                },
                "dict": {"url": "yddict://m.youdao.com/dict?le=eng&q=apple"},
                "webdict": {"url": "http://mobile.youdao.com/dict?le=eng&q=apple"},
                "basic": {
                    "exam_type": ["初中", "高中", "CET4", "CET6", "考研"],
                    "us-phonetic": "ˈæp(ə)l",
                    "phonetic": "ˈæp(ə)l",
                    "uk-phonetic": "ˈæp(ə)l",
                    "wfs": [{"wf": {"name": "复数", "value": "apples"}}],
                    "uk-speech": "https://openapi.youdao.com/ttsapi?q=apple&langType=en&sign=842FD658CB64EE4D83E6F2DB63BD4820&salt=1694583954151&voice=5&format=mp3&appKey=59c4b2a39ab77960&ttsVoiceStrict=false&osType=api",
                    "explains": ["n. 苹果"],
                    "us-speech": "https://openapi.youdao.com/ttsapi?q=apple&langType=en&sign=842FD658CB64EE4D83E6F2DB63BD4820&salt=1694583954151&voice=6&format=mp3&appKey=59c4b2a39ab77960&ttsVoiceStrict=false&osType=api",
                },
                "isWord": True,
                "speakUrl": "https://openapi.youdao.com/ttsapi?q=apple&langType=en-USA&sign=842FD658CB64EE4D83E6F2DB63BD4820&salt=1694583954151&voice=4&format=mp3&appKey=59c4b2a39ab77960&ttsVoiceStrict=false&osType=api",
            }
        )
        print(json.dumps(res, indent=2, ensure_ascii=False))

    def test_format_sentence_response(self):
        res = YoudaoTranslate.format_sentence_response(
            response={
                "tSpeakUrl": "https://openapi.youdao.com/ttsapi?q=%E4%B8%8B%E9%9D%A2%E7%9A%84%E5%BF%AB%E9%80%9F%E5%85%A5%E9%97%A8%E6%BC%94%E7%A4%BA%E4%BA%86%E5%A6%82%E4%BD%95%E5%88%9B%E5%BB%BA%E8%87%AA%E5%AE%9A%E4%B9%89%E8%AF%AD%E9%9F%B3%E5%8A%A9%E6%89%8B&langType=zh-CHS&sign=71D7D7622AA9328FFA6B1564E5E80897&salt=1694657427689&voice=4&format=mp3&appKey=59c4b2a39ab77960&ttsVoiceStrict=false&osType=api",
                "requestId": "59149a09-25d6-4bbb-9370-e2ef9d100a88",
                "query": "The following quickstarts demonstrate how to create a custom Voice Assistant",
                "translation": ["下面的快速入门演示了如何创建自定义语音助手"],
                "mTerminalDict": {
                    "url": "https://m.youdao.com/m/result?lang=en&word=The+following+quickstarts+demonstrate+how+to+create+a+custom+Voice+Assistant"
                },
                "errorCode": "0",
                "dict": {
                    "url": "yddict://m.youdao.com/dict?le=eng&q=The+following+quickstarts+demonstrate+how+to+create+a+custom+Voice+Assistant"
                },
                "webdict": {
                    "url": "http://mobile.youdao.com/dict?le=eng&q=The+following+quickstarts+demonstrate+how+to+create+a+custom+Voice+Assistant"
                },
                "l": "en2zh-CHS",
                "isWord": False,
                "speakUrl": "https://openapi.youdao.com/ttsapi?q=The+following+quickstarts+demonstrate+how+to+create+a+custom+Voice+Assistant&langType=en-USA&sign=A4BD0BA339893EEC4922AE35BF8E04ED&salt=1694657427689&voice=4&format=mp3&appKey=59c4b2a39ab77960&ttsVoiceStrict=false&osType=api",
            }
        )
        print(json.dumps(res, indent=2, ensure_ascii=False))

    def test_generate_file_name(self):
        res = YoudaoTranslate.generate_word_audio_file_name("apple", "zh")
        print(res)
