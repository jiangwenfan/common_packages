import uuid

import requests

from common_packages.translate import LanguageCodeOfBackend, SentenceInfo, WordInfo
from common_packages.tts.microsoft import TTSMicrosoft

pos_tag_table = {
    "ADJ": ("Adjectives", "形容词"),
    "ADV": ("Adverbs", "副词"),
    "CONJ": ("Conjunctions", "连词"),
    "DET": ("Determiners", "限定词"),
    "MODAL": ("Verbs", "动词"),
    "NOUN": ("Nouns", "名词"),
    "PREP": ("Prepositions", "介词"),
    "PRON": ("Pronouns", "代词"),
    "VERB": ("Verbs", "动词"),
    "OTHER": ("Other", "其他"),
}


class TranslateMicrosoft:
    def __init__(
        self,
        text_endpoint: str,
        word_endpoint: str,
        word_sample_endpoint: str,
        location_region: str,
        key: str,
        tts_microsoft_config: dict,
    ):
        self.text_endpoint = text_endpoint
        self.word_endpoint = word_endpoint
        self.word_samples_endpoint = word_sample_endpoint
        self.location_region = location_region
        self.key = key
        # 这个由配置文件传入
        # self.part_params = {"api-version": "3.0"}
        self.part_params = {}
        self.tts_microsoft_obj = TTSMicrosoft(**tts_microsoft_config)

    def translate_word(
        self,
        word: str,
        source_language_code: LanguageCodeOfBackend,
        target_language_code: LanguageCodeOfBackend,
    ) -> dict:
        """翻译word,使用字典接口查询"""
        # 1. 获取sentence原生响应
        raw_response: dict = self._send_word_request(
            word, source_language_code, target_language_code
        )
        normalized_word = raw_response["normalizedSource"]

        # 2. 获取word的tts结果
        word_audio: bytes = self._send_tts_request(normalized_word, None)
        # 补充word单词发音
        raw_response["audio_data"] = word_audio

        # 3. 获取word翻译的所有例句，返回一个新的翻译结果
        new_translations = self._get_word_translation_all_examples(
            raw_response, source_language_code, target_language_code
        )
        # 替换原始翻译结果
        raw_response["translations"] = new_translations

        # 返回最终结果
        return raw_response

    def translate_sentence(
        self,
        text: str,
        source_language_code: LanguageCodeOfBackend,
        target_language_code: LanguageCodeOfBackend,
    ) -> dict:
        """翻译句子,使用文本翻译接口查询
        返回:
            {
                "text":"xxx",
                "to":"xxx",
                "audio_data": bytes
                "sentence": "xxx"
            }
        """

        # 1. 获取sentence原生响应
        # text 是翻译后的文本, to 是目标语言代码
        raw_result: dict = self._send_sentence_request(
            text, source_language_code, target_language_code
        )

        # 2.1 获取text的tts结果
        text_audio: bytes = self._send_tts_request(text, None)
        # 2.2 增加text的发音
        raw_result["audio_data"] = text_audio

        # 3. 增加原始文本
        raw_result["sentence"] = text

        return raw_result

    # ############################ [类方法]格式化响应结果 ############################
    @classmethod
    def format_word_response(cls, response: dict) -> WordInfo:
        """将相应结果处理为了WordInfo
        raw_response: 单词的补充处理之后的翻译结果,来自 translate_word 方法返回值
        """
        normalized_word = response["normalizedSource"]
        display_word = response["displaySource"]

        # 所有变体.
        _ = {
            "normalizedText": "fly",
            "displayText": "fly",
            "numExamples": 15,
            "frequencyCount": 4995,
        }
        raw_shapes: list[dict] = []

        # 翻译结果
        translations: list[dict] = []

        all_raw_translations: list[dict] = response["translations"]
        for raw_translation in all_raw_translations:
            # 添加翻译
            item = {
                "normalized": raw_translation["normalizedTarget"],
                "display": raw_translation["displayTarget"],
                "pos_tag": cls._change_pos_tag(raw_translation["posTag"]),
                "frequency": cls._change_frequency(raw_translation["confidence"]),
                "examples": raw_translation["examples"],
            }
            translations.append(item)

            # 其他变体
            shape = raw_translation["backTranslations"]
            raw_shapes.extend(shape)

        # 单词其他形式.变体排序
        sorted_shapes = cls._sort_shapes(raw_shapes)

        res = {
            "normalized_word": normalized_word,
            "display_word": display_word,
            "translations": translations,
            "shapes": sorted_shapes,
            "audio_data": response["audio_data"],
            "extended_info": {},
        }
        return res

    @classmethod
    def format_sentence_response(cls, response: dict) -> SentenceInfo:
        """将相应结果处理为了SentenceInfo"""
        sentence = response["sentence"]
        translation = [response["text"]]
        audio_data = response["audio_data"]

        res = {
            "sentence": sentence,
            "translations": translation,
            "audio_data": audio_data,
        }
        return res

    # ############################ [私有方法] 发送word请求 ############################
    def _send_word_request(
        self,
        word: str,
        source_language_code: LanguageCodeOfBackend,
        target_language_code: LanguageCodeOfBackend,
    ) -> dict:
        """发送单词翻译请求
        [文档](https://learn.microsoft.com/en-us/azure/ai-services/translator/reference/v3-0-dictionary-lookup)
        [词典示例](https://learn.microsoft.com/en-us/azure/ai-services/translator/reference/v3-0-dictionary-examples)
        """
        # 1. 转换语言代码
        source_language_code = self._change_language_code(source_language_code)
        target_language_code = self._change_language_code(target_language_code)

        # 2. 构造请求查询参数: 源语言,目标语言
        params = self.part_params | {
            "from": source_language_code,
            "to": target_language_code,
        }

        # 3.1 获取 access_token
        access_token = self.tts_microsoft_obj.fetch_access_token()

        # 3. 构造请求头: key,location,content-type
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Ocp-Apim-Subscription-Key": self.key,
            "Ocp-Apim-Subscription-Region": self.location_region,
            "Content-type": "application/json",
            "X-ClientTraceId": str(uuid.uuid4()),
        }

        # 4. 构造请求体: 要翻译的word
        body = [{"Text": word}]

        # 5. 发送请求
        try:
            response = requests.post(
                self.word_endpoint, params=params, headers=headers, json=body
            )
        except Exception as e:
            _ = f"microsoft 词典翻译请求连接失败: {self.text_endpoint} {params} {headers} {body}"
            raise ValueError(_ + e)
        if response.status_code != 200:
            raise ValueError(
                f"microsoft 词典翻译响应状态: {response.status_code}; 响应具体错误: {response.text};\
                请求参数: {headers} {body}; 实际请求url: {response.url}"
            )

        # 6.返回原生响应
        response: list[dict] = response.json()

        # 7. 断言必须只有一个翻译结果
        assert len(response) == 1, f"microsoft词典翻译响应格式错误: {response}"
        # 返回的结果
        res = response[0]
        _ = {
            # 直接翻译的结果
            "normalizedSource": "fly",
            # 润色之后的结果
            "displaySource": "fly",
            "translations": [
                {
                    # 相当于直接翻译的结果
                    "normalizedTarget": "飞",
                    # 润色之后的
                    # 以最适合最终用户显示的形式提供源术语
                    "displayTarget": "飞",
                    "posTag": "VERB",
                    # 一个介于 0.0 和 1.0 之间的值，“训练数据中的概率”
                    # 翻译的词频。保留1位,四舍五入进位。
                    # round(n*100,1)
                    "confidence": 0.2898,
                    "prefixWord": "",
                    # 单词的其他
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
                    ],
                },
            ],
        }
        return res

    def _send_word_examples_request(
        self,
        normalized_word: str,
        normalized_translation: str,
        source_language_code: LanguageCodeOfBackend,
        target_language_code: LanguageCodeOfBackend,
    ) -> list[dict]:
        """获取单词的例句
        normalized_word: 单词的标准化形式
        normalized_translation: 单词翻译的标准化形式
        """
        # 1. 转换语言代码
        source_language_code = self._change_language_code(source_language_code)
        target_language_code = self._change_language_code(target_language_code)

        # 2. 构造请求查询参数: 源语言,目标语言
        params = self.part_params | {
            "from": source_language_code,
            "to": target_language_code,
        }

        # 3.1 获取 access_token
        access_token = self.tts_microsoft_obj.fetch_access_token()

        # 3. 构造请求头: key,location,content-type
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Ocp-Apim-Subscription-Key": self.key,
            "Ocp-Apim-Subscription-Region": self.location_region,
            "Content-type": "application/json",
            "X-ClientTraceId": str(uuid.uuid4()),
        }

        # 4. 构造请求体: 要翻译的word
        body = [{"Text": normalized_word, "Translation": normalized_translation}]

        # 5. 发送请求
        try:
            response = requests.post(
                self.word_samples_endpoint, params=params, headers=headers, json=body
            )
        except Exception as e:
            _ = f"microsoft 词典示例请求连接失败: {self.text_endpoint} {params} {headers} {body}"
            raise ValueError(_ + e)
        if response.status_code != 200:
            raise ValueError(
                f"microsoft 词典示例响应状态: {response.status_code}; 响应具体错误: {response.text};\
                请求参数: {headers} {body};\
                实际请求url: {response.url}"
            )

        # 6.返回原生响应
        response: list[dict] = response.json()

        # 7. 断言必须只有一个翻译结果
        assert len(response) == 1, f"microsoft词典翻译响应格式错误: {response}"
        # 返回的结果
        _ = [
            {
                "normalizedSource": "fly",
                "normalizedTarget": "乘 飞机",
                "examples": [
                    {
                        "sourcePrefix": "Tomorrow we're going to ",
                        "sourceTerm": "fly",
                        "sourceSuffix": " home.",
                        "targetPrefix": "明天我们将",
                        "targetTerm": "乘飞机",
                        "targetSuffix": "回家",
                    },
                    {
                        "sourcePrefix": "Tomorrow we're going to ",
                        "sourceTerm": "fly",
                        "sourceSuffix": " home.",
                        "targetPrefix": "明天我们就",
                        "targetTerm": "乘飞机",
                        "targetSuffix": "回家了。",
                    },
                    {
                        "sourcePrefix": "No students ",
                        "sourceTerm": "fly",
                        "sourceSuffix": " to school.",
                        "targetPrefix": "没有学生",
                        "targetTerm": "乘飞机",
                        "targetSuffix": "上学。",
                    },
                ],
            }
        ]

        # 获取示例响应
        sample_response: dict = response[0]
        assert (
            sample_response["normalizedSource"] == normalized_word
        ), f"microsoft词典示例响应格式错误: {sample_response}"
        assert (
            sample_response["normalizedTarget"] == normalized_translation
        ), f"microsoft词典示例响应格式错误: {sample_response}"

        # 获取示例结果
        examples: list[dict] = sample_response["examples"]
        _ = (
            [
                {
                    "sourcePrefix": "Tomorrow we're going to ",
                    "sourceTerm": "fly",
                    "sourceSuffix": " home.",
                    "targetPrefix": "明天我们将",
                    "targetTerm": "乘飞机",
                    "targetSuffix": "回家",
                },
                {
                    "sourcePrefix": "Tomorrow we're going to ",
                    "sourceTerm": "fly",
                    "sourceSuffix": " home.",
                    "targetPrefix": "明天我们就",
                    "targetTerm": "乘飞机",
                    "targetSuffix": "回家了。",
                },
                {
                    "sourcePrefix": "No students ",
                    "sourceTerm": "fly",
                    "sourceSuffix": " to school.",
                    "targetPrefix": "没有学生",
                    "targetTerm": "乘飞机",
                    "targetSuffix": "上学。",
                },
            ],
        )
        return examples

    def _unique_word_examples(self, examples_info: list[dict]) -> list[dict]:
        """将重复的例句进行合并,比如同一个句子有多个翻译的情况
        examples_info 是_send_word_examples_request方法的返回结果
        """
        _ = [
            {
                "sourcePrefix": "Tomorrow we're going to ",
                "sourceTerm": "fly",
                "sourceSuffix": " home.",
                "targetPrefix": "明天我们将",
                "targetTerm": "乘飞机",
                "targetSuffix": "回家",
            },
            {
                "sourcePrefix": "Tomorrow we're going to ",
                "sourceTerm": "fly",
                "sourceSuffix": " home.",
                "targetPrefix": "明天我们就",
                "targetTerm": "乘飞机",
                "targetSuffix": "回家了。",
            },
            {
                "sourcePrefix": "No students ",
                "sourceTerm": "fly",
                "sourceSuffix": " to school.",
                "targetPrefix": "没有学生",
                "targetTerm": "乘飞机",
                "targetSuffix": "上学。",
            },
        ]

        # 最终结果的一个中间态存储结构
        """
        1. 新的句子example结构:
        {
            "sourcePrefix": "前半句",
            "sourceTerm": "关键词",
            "sourceSuffix": "后半句",

            // 将这里翻译放到了list中，因为部分句子一样，但是翻译不一样
            "target": [
                {
                    "targetPrefix": "翻译前半句",
                    "targetTerm": "翻译关键词",
                    "targetSuffix": "翻译后半句",
                }
            ],
        }

        2. 临时句子就是: "前半句+关键词+后半句"

        3. final_res_info的结构:
        {
            临时句子: 句子翻译新结构
        }
        """
        final_res_info = {}

        for example_info in examples_info:
            # 1. 临时拼接形成完整句子，根据这个句子判断是否已经存在
            temp_sentence: str = (
                example_info["sourcePrefix"]
                + example_info["sourceTerm"]
                + example_info["sourceSuffix"]
            )

            # 1.1 [准备数据] 获取当前翻译的结构:
            # 如果首次添加，后面会在外层套个list,添加；
            # 如果已经存在，则在 `已经存在的翻译` list中追加 `当前翻译的结构`
            current_target = {
                "targetPrefix": example_info["targetPrefix"],
                "targetTerm": example_info["targetTerm"],
                "targetSuffix": example_info["targetSuffix"],
            }

            if temp_sentence not in final_res_info:
                # 当前句子不存在时，直接添加到final_res_info中

                # 2.1 生成新的sample结构
                new_example = {
                    "sourcePrefix": example_info["sourcePrefix"],
                    "sourceTerm": example_info["sourceTerm"],
                    "sourceSuffix": example_info["sourceSuffix"],
                    "target": [current_target],
                }

                # 2.2 添加到final_res_info中
                final_res_info[temp_sentence] = new_example
            else:
                # 当前句子已经存在时
                # 2.1 获取已经存在的sample [此处是引用获取的]
                exist_example_info: dict = final_res_info[temp_sentence]

                # 2.1 获取已经存在的sample中的翻译
                exist_example_target: list[dict] = exist_example_info["target"]
                # 2.2 将当前翻译添加到已经存在的翻译中
                exist_example_target.append(current_target)

                # 2.3 更新已经存在的sample中的翻译
                exist_example_info["target"] = exist_example_target

        # 3. 将final_res_info中的值取出来,组装成以下结构
        """
        [
            {
            "sourcePrefix": "前半句",
            "sourceTerm": "关键词",
            "sourceSuffix": "后半句",
            "target": [
                {
                    "targetPrefix": "翻译前半句",
                    "targetTerm": "翻译关键词",
                    "targetSuffix": "翻译后半句",
                }
            ],
        ]
        """
        final_res: list[dict] = list(final_res_info.values())
        return final_res

    def _get_word_translation_all_examples(
        self,
        raw_response: dict,
        source_language_code: LanguageCodeOfBackend,
        target_language_code: LanguageCodeOfBackend,
    ) -> list[dict]:
        """获取单词的所有翻译例句,返回一个新的翻译结果
        raw_response: 单词的原始翻译结果,是_send_word_request方法的返回结果
        """
        # 1. 获取标准化之后的单词
        normalized_word = raw_response["normalizedSource"]

        # 2.1 获取原始的翻译结果
        translations_info = raw_response["translations"]
        # 2.2 添加例句之后的新翻译结果
        final_translations_info = []

        # 遍历每一个翻译结果,获取其翻译例句
        for translation_info in translations_info:
            # 1. 获取翻译的标准化形式  例: "飞"
            normalized_translation: str = translation_info["normalizedTarget"]
            # 2. 获取当前翻译的所有例句
            raw_translation_samples: list[dict] = self._send_word_examples_request(
                normalized_word=normalized_word,
                normalized_translation=normalized_translation,
                source_language_code=source_language_code,
                target_language_code=target_language_code,
            )
            # 去重翻译例句
            translation_samples: list[dict] = self._unique_word_examples(
                raw_translation_samples
            )

            # 3. 为当前翻译添加所有例句
            translation_info["examples"] = translation_samples

            # 4. 将新的翻译结果添加到最终结果中
            final_translations_info.append(translation_info)

        return final_translations_info

    # ############################ [私有方法] 发送sentence请求 ############################
    def _send_sentence_request(
        self,
        text: str,
        source_language_code: LanguageCodeOfBackend,
        target_language_code: LanguageCodeOfBackend,
    ) -> dict:
        """发送句子翻译请求\n
        [文本翻译接口](https://learn.microsoft.com/en-us/azure/ai-services/translator/text-translation-overview)
        """
        # 1. 转换语言代码
        source_language_code = self._change_language_code(source_language_code)
        target_language_code = self._change_language_code(target_language_code)

        # 2. 构造请求查询参数: 源语言,目标语言
        params = self.part_params | {
            "from": source_language_code,
            "to": target_language_code,
        }

        # 3. 构造请求头: key,location,content-type
        headers = {
            "Ocp-Apim-Subscription-Key": self.key,
            "Ocp-Apim-Subscription-Region": self.location_region,
            "Content-type": "application/json",
            "X-ClientTraceId": str(uuid.uuid4()),
        }

        # 4. 构造请求体: 要翻译的文本
        body = [{"text": text}]

        # 5. 发送请求
        try:
            response = requests.post(
                self.text_endpoint, params=params, headers=headers, json=body
            )
        except Exception as e:
            _ = f"microsoft 翻译请求连接失败: {self.text_endpoint} {params} {headers} {body}"
            raise ValueError(_ + e)
        if response.status_code != 200:
            raise ValueError(
                f"microsoft 翻译响应状态: {response.status_code}; 响应具体错误: {response.text}\
                实际请求url: {response.url}; 请求参数: {headers} {body}"
            )

        # 6.返回原生响应
        response: list[dict] = response.json()
        assert len(response) == 1, f"microsoft翻译响应格式错误1: {response}"

        # 解析1
        response_dict: dict = response[0]
        assert (
            "translations" in response_dict
        ), f"microsoft翻译响应格式错误2: {response_dict}"
        _ = {
            "translations": [
                {
                    "text": "J'aimerais vraiment conduire votre voiture autour\
 du pâté de maisons plusieurs fois!",
                    "to": "fr",
                },
            ]
        }

        # 2. 解析原生响应
        response_dict2: list[dict] = response_dict["translations"]
        assert len(response_dict2) == 1, f"microsoft翻译响应格式错误3: {response_dict2}"
        _ = [
            {
                "text": "J'aimerais vraiment conduire votre voiture\
 autour du pâté de maisons plusieurs fois!",
                "to": "fr",
            },
        ]

        # 3. 返回结果
        res: dict = response_dict2[0]
        _ = {
            "text": "J'aimerais vraiment conduire votre voiture\
 autour du pâté de maisons plusieurs fois!",
            "to": "fr",
        }
        return res

    def _send_tts_request(self, text: str, _text_language_code: str) -> bytes:
        """发送tts请求
        # HACK 当前只能生成英文的音频
        """
        wav_data = self.tts_microsoft_obj.convert_text_to_speech(text)
        return wav_data

    # ############################ [静态方法] ############################
    @staticmethod
    def _change_language_code(language_code_of_backend: LanguageCodeOfBackend) -> str:
        """转换语言代码,将language_backend后端的语言代码转换为microsoft的语言代码
        [microsoft支持的语言](https://learn.microsoft.com/en-us/azure/ai-services/translator/reference/v3-0-languages)
        """
        match language_code_of_backend:
            case "zh-CN":
                # 简体中文. 将后端的`zh-CN`转换为微软`zh-Hans`
                return "zh-Hans"
            case "zh-TW":
                # 繁体中文. 将后端的`zh-TW`转换为微软`zh-Hant`
                return "zh-Hant"
            case "en" | "ja":
                # en: 英语, ja: 日语 等，不需要转换
                return language_code_of_backend
            case _:
                raise ValueError(
                    f"microsoft不支持的语言代码: {language_code_of_backend}"
                )

    @staticmethod
    def _change_pos_tag(pos_tag: str) -> tuple[str, str]:
        """将microsft的词性标签转换为人类可读的词性标签
        pos_tag: microsoft的词性标签   "ADJ"
        返回: ("Adjectives", "形容词")
        """

        # 将此术语与词性标签关联的字符串
        if pos_tag not in pos_tag_table:
            raise ValueError(f"microsoft不支持的词性标签: {pos_tag}")
        return pos_tag_table[pos_tag]

    @staticmethod
    def _change_frequency(frequency: float) -> float:
        """将microsoft的词频转换为人类可读的词频,小数点第二位四舍五入
        frequency: 0.123
        返回: 12.3
        """
        return round(frequency * 100, 1)

    @staticmethod
    def _sort_shapes(raw_shapes: list[dict]) -> list[dict]:
        """对单词的其他形式进行排序.从大到小"""
        return sorted(
            raw_shapes, key=lambda shape: shape["frequencyCount"], reverse=True
        )
