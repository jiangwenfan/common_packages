import json

import pytest

from common_packages.translate.microsoft import TranslateMicrosoft

# from common_packages.translate.youdao import YoudaoTranslate

# @pytest.fixture(scope="class")
# def youdao_op(global_config):
#     """用于在`每个测试用例`中初始化有道翻译对象"""
#     config: dict = global_config()
#     youdao = YoudaoTranslate(**config["translate"]["youdao"])


@pytest.fixture(scope="class")
def translate_microsoft_obj(global_config):
    """用于在`每个测试用例`中初始化微软翻译对象"""
    config: dict = global_config["translate"]["microsoft"]
    tts_microsoft_config = global_config["tts"]["microsoft"]
    microsoft_obj = TranslateMicrosoft(
        **config, tts_microsoft_config=tts_microsoft_config
    )
    return microsoft_obj


@pytest.fixture(scope="module")
def microsoft_word_raw_response():
    """这里提供的是,单词的原始翻译结果,是_send_word_request方法的返回结果"""
    _ = {
        "normalizedSource": "fly",
        "displaySource": "fly",
        "translations": [
            {
                "normalizedTarget": "飞",
                "displayTarget": "飞",
                "posTag": "VERB",
                "confidence": 0.2898,
                "prefixWord": "",
                "backTranslations": [
                    {
                        "normalizedText": "fly",
                        "displayText": "fly",
                        "numExamples": 15,
                        "frequencyCount": 4995,
                    },
                    {
                        "normalizedText": "flying",
                        "displayText": "flying",
                        "numExamples": 15,
                        "frequencyCount": 1931,
                    },
                    {
                        "normalizedText": "flew",
                        "displayText": "flew",
                        "numExamples": 15,
                        "frequencyCount": 968,
                    },
                    {
                        "normalizedText": "flight",
                        "displayText": "flight",
                        "numExamples": 15,
                        "frequencyCount": 340,
                    },
                    {
                        "normalizedText": "flies",
                        "displayText": "flies",
                        "numExamples": 15,
                        "frequencyCount": 253,
                    },
                    {
                        "normalizedText": "fei",
                        "displayText": "Fei",
                        "numExamples": 10,
                        "frequencyCount": 237,
                    },
                    {
                        "normalizedText": "flown",
                        "displayText": "flown",
                        "numExamples": 5,
                        "frequencyCount": 127,
                    },
                ],
            },
            {
                "normalizedTarget": "飞翔",
                "displayTarget": "飞翔",
                "posTag": "VERB",
                "confidence": 0.1658,
                "prefixWord": "",
                "backTranslations": [
                    {
                        "normalizedText": "fly",
                        "displayText": "fly",
                        "numExamples": 15,
                        "frequencyCount": 937,
                    },
                    {
                        "normalizedText": "flying",
                        "displayText": "flying",
                        "numExamples": 15,
                        "frequencyCount": 408,
                    },
                    {
                        "normalizedText": "flight",
                        "displayText": "flight",
                        "numExamples": 15,
                        "frequencyCount": 105,
                    },
                    {
                        "normalizedText": "soar",
                        "displayText": "soar",
                        "numExamples": 5,
                        "frequencyCount": 35,
                    },
                    {
                        "normalizedText": "soaring",
                        "displayText": "soaring",
                        "numExamples": 5,
                        "frequencyCount": 34,
                    },
                    {
                        "normalizedText": "flies",
                        "displayText": "flies",
                        "numExamples": 6,
                        "frequencyCount": 24,
                    },
                    {
                        "normalizedText": "feixiang",
                        "displayText": "Feixiang",
                        "numExamples": 0,
                        "frequencyCount": 9,
                    },
                ],
            },
            {
                "normalizedTarget": "飞行",
                "displayTarget": "飞行",
                "posTag": "VERB",
                "confidence": 0.1114,
                "prefixWord": "",
                "backTranslations": [
                    {
                        "normalizedText": "flight",
                        "displayText": "flight",
                        "numExamples": 15,
                        "frequencyCount": 4888,
                    },
                    {
                        "normalizedText": "flying",
                        "displayText": "flying",
                        "numExamples": 15,
                        "frequencyCount": 2277,
                    },
                    {
                        "normalizedText": "fly",
                        "displayText": "fly",
                        "numExamples": 15,
                        "frequencyCount": 961,
                    },
                    {
                        "normalizedText": "flew",
                        "displayText": "flew",
                        "numExamples": 15,
                        "frequencyCount": 109,
                    },
                    {
                        "normalizedText": "flown",
                        "displayText": "flown",
                        "numExamples": 5,
                        "frequencyCount": 80,
                    },
                    {
                        "normalizedText": "flies",
                        "displayText": "flies",
                        "numExamples": 15,
                        "frequencyCount": 77,
                    },
                ],
            },
            {
                "normalizedTarget": "只 苍蝇",
                "displayTarget": "只苍蝇",
                "posTag": "NOUN",
                "confidence": 0.1062,
                "prefixWord": "",
                "backTranslations": [
                    {
                        "normalizedText": "fly",
                        "displayText": "fly",
                        "numExamples": 15,
                        "frequencyCount": 189,
                    },
                    {
                        "normalizedText": "flies",
                        "displayText": "flies",
                        "numExamples": 4,
                        "frequencyCount": 8,
                    },
                ],
            },
            {
                "normalizedTarget": "苍蝇",
                "displayTarget": "苍蝇",
                "posTag": "NOUN",
                "confidence": 0.1058,
                "prefixWord": "",
                "backTranslations": [
                    {
                        "normalizedText": "flies",
                        "displayText": "flies",
                        "numExamples": 15,
                        "frequencyCount": 583,
                    },
                    {
                        "normalizedText": "fly",
                        "displayText": "fly",
                        "numExamples": 15,
                        "frequencyCount": 356,
                    },
                ],
            },
            {
                "normalizedTarget": "乘 飞机",
                "displayTarget": "乘飞机",
                "posTag": "VERB",
                "confidence": 0.0622,
                "prefixWord": "",
                "backTranslations": [
                    {
                        "normalizedText": "fly",
                        "displayText": "fly",
                        "numExamples": 15,
                        "frequencyCount": 89,
                    },
                    {
                        "normalizedText": "flying",
                        "displayText": "flying",
                        "numExamples": 15,
                        "frequencyCount": 82,
                    },
                    {
                        "normalizedText": "flew",
                        "displayText": "flew",
                        "numExamples": 4,
                        "frequencyCount": 26,
                    },
                    {
                        "normalizedText": "flown",
                        "displayText": "flown",
                        "numExamples": 4,
                        "frequencyCount": 13,
                    },
                ],
            },
            {
                "normalizedTarget": "飞走",
                "displayTarget": "飞走",
                "posTag": "VERB",
                "confidence": 0.0615,
                "prefixWord": "",
                "backTranslations": [
                    {
                        "normalizedText": "flew",
                        "displayText": "flew",
                        "numExamples": 15,
                        "frequencyCount": 108,
                    },
                    {
                        "normalizedText": "fly",
                        "displayText": "fly",
                        "numExamples": 15,
                        "frequencyCount": 91,
                    },
                    {
                        "normalizedText": "flown",
                        "displayText": "flown",
                        "numExamples": 5,
                        "frequencyCount": 19,
                    },
                    {
                        "normalizedText": "flies away",
                        "displayText": "flies away",
                        "numExamples": 5,
                        "frequencyCount": 18,
                    },
                ],
            },
            {
                "normalizedTarget": "翱翔",
                "displayTarget": "翱翔",
                "posTag": "VERB",
                "confidence": 0.0575,
                "prefixWord": "",
                "backTranslations": [
                    {
                        "normalizedText": "fly",
                        "displayText": "fly",
                        "numExamples": 15,
                        "frequencyCount": 78,
                    },
                    {
                        "normalizedText": "soar",
                        "displayText": "soar",
                        "numExamples": 5,
                        "frequencyCount": 62,
                    },
                    {
                        "normalizedText": "flying",
                        "displayText": "flying",
                        "numExamples": 15,
                        "frequencyCount": 47,
                    },
                    {
                        "normalizedText": "soaring",
                        "displayText": "soaring",
                        "numExamples": 5,
                        "frequencyCount": 29,
                    },
                    {
                        "normalizedText": "hover",
                        "displayText": "hover",
                        "numExamples": 5,
                        "frequencyCount": 17,
                    },
                    {
                        "normalizedText": "hovering",
                        "displayText": "hovering",
                        "numExamples": 0,
                        "frequencyCount": 3,
                    },
                ],
            },
            {
                "normalizedTarget": "驾驶",
                "displayTarget": "驾驶",
                "posTag": "VERB",
                "confidence": 0.0397,
                "prefixWord": "",
                "backTranslations": [
                    {
                        "normalizedText": "driving",
                        "displayText": "driving",
                        "numExamples": 15,
                        "frequencyCount": 5109,
                    },
                    {
                        "normalizedText": "driver",
                        "displayText": "driver",
                        "numExamples": 15,
                        "frequencyCount": 699,
                    },
                    {
                        "normalizedText": "fly",
                        "displayText": "fly",
                        "numExamples": 15,
                        "frequencyCount": 153,
                    },
                    {
                        "normalizedText": "drove",
                        "displayText": "drove",
                        "numExamples": 15,
                        "frequencyCount": 104,
                    },
                    {
                        "normalizedText": "pilot",
                        "displayText": "pilot",
                        "numExamples": 15,
                        "frequencyCount": 92,
                    },
                    {
                        "normalizedText": "motorists",
                        "displayText": "motorists",
                        "numExamples": 5,
                        "frequencyCount": 88,
                    },
                    {
                        "normalizedText": "piloting",
                        "displayText": "piloting",
                        "numExamples": 5,
                        "frequencyCount": 54,
                    },
                ],
            },
        ],
    }
    return _


@pytest.fixture(scope="module")
def microsoft_word_example_data():
    """这里提供的是_send_word_examples_request方法返回的指定word的指定翻译的例句数据"""
    _ = [
        {
            "sourcePrefix": "Feeling the happiness for ",
            "sourceTerm": "fly",
            "sourceSuffix": ".",
            "targetPrefix": "感受着",
            "targetTerm": "飞翔",
            "targetSuffix": "的快乐。",
        },
        {
            "sourcePrefix": "He taught her to ",
            "sourceTerm": "fly",
            "sourceSuffix": ".",
            "targetPrefix": "他教她",
            "targetTerm": "飞翔",
            "targetSuffix": ".",
        },
        {
            "sourcePrefix": "I will turn you on, and lets ",
            "sourceTerm": "fly",
            "sourceSuffix": ".",
            "targetPrefix": "我将会唤醒你，然后一起",
            "targetTerm": "飞翔",
            "targetSuffix": "。",
        },
        {
            "sourcePrefix": "Then you'll learn to ",
            "sourceTerm": "fly",
            "sourceSuffix": ".",
            "targetPrefix": "然后你就能学会",
            "targetTerm": "飞翔",
            "targetSuffix": "。",
        },
        {
            "sourcePrefix": "Birds ",
            "sourceTerm": "fly",
            "sourceSuffix": " in the air.",
            "targetPrefix": "鸟儿在天空",
            "targetTerm": "飞翔",
            "targetSuffix": "。",
        },
        {
            "sourcePrefix": "I believe i can ",
            "sourceTerm": "fly",
            "sourceSuffix": " !",
            "targetPrefix": "我相信我可以",
            "targetTerm": "飞翔",
            "targetSuffix": "。",
        },
        {
            "sourcePrefix": "I will ",
            "sourceTerm": "fly",
            "sourceSuffix": " with you.",
            "targetPrefix": "我要和你一起",
            "targetTerm": "飞翔",
            "targetSuffix": "",
        },
        {
            "sourcePrefix": "You gave me wings and made me ",
            "sourceTerm": "fly",
            "sourceSuffix": ".",
            "targetPrefix": "你给了我翅膀使我可以",
            "targetTerm": "飞翔",
            "targetSuffix": "。",
        },
        {
            "sourcePrefix": "A man cannot ",
            "sourceTerm": "fly",
            "sourceSuffix": " just as a bird cannot speak.",
            "targetPrefix": "人不能",
            "targetTerm": "飞翔",
            "targetSuffix": "就象鸟儿不能说话一样。",
        },
        {
            "sourcePrefix": "If we can ",
            "sourceTerm": "fly",
            "sourceSuffix": ", what will you do?",
            "targetPrefix": "如果我们可以",
            "targetTerm": "飞翔",
            "targetSuffix": "，你会做什么？",
        },
        {
            "sourcePrefix": "But only in small space, ",
            "sourceTerm": "fly",
            "sourceSuffix": ".",
            "targetPrefix": "却只能在小小的空间里，",
            "targetTerm": "飞翔",
            "targetSuffix": "。",
        },
        {
            "sourcePrefix": "Men have always wanted to ",
            "sourceTerm": "fly",
            "sourceSuffix": " like birds.",
            "targetPrefix": "男人们总是希望像鸟一样",
            "targetTerm": "飞翔",
            "targetSuffix": "。",
        },
        {
            "sourcePrefix": "I hope you can ",
            "sourceTerm": "fly",
            "sourceSuffix": " in the sky freely .",
            "targetPrefix": "我希望你可以在天空自由地",
            "targetTerm": "飞翔",
            "targetSuffix": "。",
        },
        {
            "sourcePrefix": "Let me rise and ",
            "sourceTerm": "fly",
            "sourceSuffix": " away.",
            "targetPrefix": "让我起床去",
            "targetTerm": "飞翔",
            "targetSuffix": "。",
        },
        {
            "sourcePrefix": "Here you can like a kite the same ",
            "sourceTerm": "fly",
            "sourceSuffix": ".",
            "targetPrefix": "在这里你能象风筝一样的",
            "targetTerm": "飞翔",
            "targetSuffix": "。",
        },
    ]

    return _


@pytest.fixture(scope="module")
def microsoft_all_raw_backTranslations():
    """这里提供的是,所有翻译合并后的backTranslations"""
    _ = [
        {
            "normalizedText": "fly",
            "displayText": "fly",
            "numExamples": 15,
            "frequencyCount": 4995,
        },
        {
            "normalizedText": "flying",
            "displayText": "flying",
            "numExamples": 15,
            "frequencyCount": 1931,
        },
        {
            "normalizedText": "flew",
            "displayText": "flew",
            "numExamples": 15,
            "frequencyCount": 968,
        },
        {
            "normalizedText": "flight",
            "displayText": "flight",
            "numExamples": 15,
            "frequencyCount": 340,
        },
    ]
    return _


@pytest.fixture(scope="module")
def word_translate_data():
    """读取word翻译数据，来自 translate_word 方法的返回结果"""
    with open(
        "tests/fixtures/translate_data/word_translate_data.json", encoding="utf-8"
    ) as f:
        data = json.load(f)

    # 恢复 audio_data 为 bytes
    data["audio_data"] = data["audio_data"].encode("utf-8")
    return data


@pytest.fixture(scope="module")
def sentence_translate_data():
    """读取word翻译数据，来自 translate_sentence 方法的返回结果"""
    with open(
        "tests/fixtures/translate_data/sentence_translate_data.json",
        encoding="utf-8",
    ) as f:
        data = json.load(f)

    # 恢复 audio_data 为 bytes
    data["audio_data"] = data["audio_data"].encode("utf-8")
    return data
