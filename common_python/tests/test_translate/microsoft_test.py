from common_packages.translate import SentenceInfo, WordInfo


class TestMicrosoft:
    word = "fly"
    normalized_translation = "飞翔"
    text = "I would really like to drive your car around the block several times!"
    source_language_code = "en"
    target_language_code = "zh-CN"

    # pytest tests/test_translate/microsoft_test.py::TestMicrosoft::test_translate_word
    def test_translate_word(self, translate_microsoft_obj):
        res_tran: dict = translate_microsoft_obj.translate_word(
            word=self.word,
            source_language_code=self.source_language_code,
            target_language_code=self.target_language_code,
        )
        # res_tran["audio_data"] = "audio_data_字节数据"
        # with open("word_res.json", "w", encoding="utf-8") as f:
        #     f.write(json.dumps(res_tran, indent=2, ensure_ascii=False))
        assert isinstance(res_tran, dict)
        assert "normalizedSource" in res_tran
        assert "displaySource" in res_tran
        # 补充的
        assert "audio_data" in res_tran
        audio_data = res_tran["audio_data"]
        assert isinstance(audio_data, bytes)
        assert "translations" in res_tran
        translations = res_tran["translations"]
        assert isinstance(translations, list)

    def test_translate_sentence(self, translate_microsoft_obj):
        res_tran: dict = translate_microsoft_obj.translate_sentence(
            text=self.text,
            source_language_code=self.source_language_code,
            target_language_code=self.target_language_code,
        )
        # print(json.dumps(res_tran, indent=2, ensure_ascii=False), type(res_tran))
        # res_tran["audio_data"] = "audio_data_字节数据"
        # with open("sentence_res.json", "w", encoding="utf-8") as f:
        #     f.write(json.dumps(res_tran, indent=2, ensure_ascii=False))

        assert isinstance(res_tran, dict)
        assert "text" in res_tran
        assert "to" in res_tran
        # 补充的
        assert "audio_data" in res_tran
        audio_data = res_tran["audio_data"]
        assert isinstance(audio_data, bytes)
        sentence = res_tran["sentence"]
        assert sentence == self.text

    # ########################### [类方法]格式化响应结果 ############################
    def test_format_word_response(self, translate_microsoft_obj, word_translate_data):
        res: WordInfo = translate_microsoft_obj.format_word_response(
            word_translate_data
        )
        assert isinstance(res, dict)
        assert "normalized_word" in res
        assert "display_word" in res
        assert "translations" in res
        # 检查translations
        translations = res["translations"]
        assert isinstance(translations, list)
        translation = translations[0]
        assert "normalized" in translation
        assert "display" in translation
        assert "pos_tag" in translation
        pos_tag = translation["pos_tag"]
        assert isinstance(pos_tag, tuple)
        assert len(pos_tag) == 2
        assert "frequency" in translation
        assert "examples" in translation

        assert "shapes" in res
        shapes = res["shapes"]
        assert isinstance(shapes, list)
        assert "audio_data" in res
        audio_data = res["audio_data"]
        assert isinstance(audio_data, bytes)
        assert "extended_info" in res
        extended_info = res["extended_info"]
        assert isinstance(extended_info, dict)

    def test_format_sentence_response(
        self, translate_microsoft_obj, sentence_translate_data
    ):
        res: SentenceInfo = translate_microsoft_obj.format_sentence_response(
            sentence_translate_data
        )
        assert isinstance(res, dict)
        assert "sentence" in res
        assert "translations" in res
        translations = res["translations"]
        assert isinstance(translations, list)
        assert "audio_data" in res
        audio_data = res["audio_data"]
        assert isinstance(audio_data, bytes)

    # ############################ [私有方法] 发送word请求  ############################
    def test__send_word_request(self, translate_microsoft_obj):
        res: dict = translate_microsoft_obj._send_word_request(
            self.word, self.source_language_code, self.target_language_code
        )

        # print(json.dumps(res, indent=2, ensure_ascii=False), type(res))
        assert isinstance(res, dict)
        assert "normalizedSource" in res
        assert "displaySource" in res
        assert "translations" in res
        translations = res["translations"]
        assert isinstance(translations, list)
        translation = translations[0]
        assert "normalizedTarget" in translation
        assert "displayTarget" in translation
        assert "posTag" in translation
        assert "confidence" in translation
        assert "prefixWord" in translation
        assert "backTranslations" in translation

    def test__send_word_examples_request(self, translate_microsoft_obj):
        res: list[dict] = translate_microsoft_obj._send_word_examples_request(
            normalized_word=self.word,
            normalized_translation=self.normalized_translation,
            source_language_code=self.source_language_code,
            target_language_code=self.target_language_code,
        )
        # print(json.dumps(res, indent=2, ensure_ascii=False), type(res))
        assert isinstance(res, list)
        example = res[0]
        assert "sourcePrefix" in example
        assert "sourceTerm" in example
        assert "sourceSuffix" in example
        assert "targetPrefix" in example
        assert "targetTerm" in example
        assert "targetSuffix" in example

    def test__unique_word_examples(
        self, translate_microsoft_obj, microsoft_word_example_data
    ):
        unique_examples: list[dict] = translate_microsoft_obj._unique_word_examples(
            microsoft_word_example_data
        )
        # print(
        #     json.dumps(unique_examples, indent=2, ensure_ascii=False),
        #     type(unique_examples),
        # )
        assert isinstance(unique_examples, list)
        # 例句中的的第一个例句
        first_example = unique_examples[0]
        assert isinstance(first_example, dict)
        assert "sourcePrefix" in first_example
        assert "sourceTerm" in first_example
        assert "sourceSuffix" in first_example
        assert "target" in first_example
        # 第一个例句的所有翻译
        first_example_first_trans = first_example["target"]
        assert isinstance(first_example_first_trans, list)
        # 第一个例句的第一个翻译
        first_example_first_tran = first_example_first_trans[0]
        assert "targetPrefix" in first_example_first_tran
        assert "targetTerm" in first_example_first_tran
        assert "targetSuffix" in first_example_first_tran

    def test__get_word_translation_all_examples(
        self, translate_microsoft_obj, microsoft_word_raw_response
    ):
        # 截取前2条翻译结果，获取所有例句
        raw_response = microsoft_word_raw_response["translations"]
        raw_response_short = raw_response[:2]
        microsoft_word_raw_response["translations"] = raw_response_short

        res: list[dict] = translate_microsoft_obj._get_word_translation_all_examples(
            microsoft_word_raw_response,
            self.source_language_code,
            self.target_language_code,
        )

        assert isinstance(res, list)
        assert len(res) == 2
        # 第一条结果
        first_res = res[0]
        assert "normalizedTarget" in first_res
        assert "confidence" in first_res
        # 额外补充的
        assert "examples" in first_res
        assert isinstance(first_res["examples"], list)

    # ############################ [私有方法] 发送sentence请求  ############################
    def test__send_sentence_request(self, translate_microsoft_obj):
        res = translate_microsoft_obj._send_sentence_request(
            self.text,
            self.source_language_code,
            self.target_language_code,
        )
        _ = {"text": "我真的很想开着你的车绕着街区转好几圈！", "to": "zh-Hans"}
        assert isinstance(res, dict)
        assert "text" in res
        assert "to" in res
        # print(res, type(res))

    def test__send_tts_request(self, translate_microsoft_obj):
        wav_data = translate_microsoft_obj._send_tts_request(self.text, None)
        assert isinstance(wav_data, bytes)
        assert len(wav_data) > 100

    # ############################ 静态方法测试 ############################
    def test__change_language_code(self, translate_microsoft_obj):
        assert translate_microsoft_obj._change_language_code("zh-CN") == "zh-Hans"
        assert translate_microsoft_obj._change_language_code("en") == "en"

    def test__change_pos_tag(self, translate_microsoft_obj):
        assert translate_microsoft_obj._change_pos_tag("ADJ") == (
            "Adjectives",
            "形容词",
        )
        assert translate_microsoft_obj._change_pos_tag("ADV") == ("Adverbs", "副词")
        assert translate_microsoft_obj._change_pos_tag("CONJ") == (
            "Conjunctions",
            "连词",
        )
        assert translate_microsoft_obj._change_pos_tag("DET") == (
            "Determiners",
            "限定词",
        )
        assert translate_microsoft_obj._change_pos_tag("MODAL") == ("Verbs", "动词")
        assert translate_microsoft_obj._change_pos_tag("NOUN") == ("Nouns", "名词")
        assert translate_microsoft_obj._change_pos_tag("PREP") == (
            "Prepositions",
            "介词",
        )
        assert translate_microsoft_obj._change_pos_tag("PRON") == ("Pronouns", "代词")
        assert translate_microsoft_obj._change_pos_tag("VERB") == ("Verbs", "动词")
        assert translate_microsoft_obj._change_pos_tag("OTHER") == ("Other", "其他")

    def test__change_frequency(self, translate_microsoft_obj):
        assert translate_microsoft_obj._change_frequency(0.123) == 12.3
        assert translate_microsoft_obj._change_frequency(0.1) == 10.0

    def test__sort_shapes(
        self, translate_microsoft_obj, microsoft_all_raw_backTranslations
    ):
        res: list[dict] = translate_microsoft_obj._sort_shapes(
            microsoft_all_raw_backTranslations
        )
        assert isinstance(res, list)
        assert len(res) == len(microsoft_all_raw_backTranslations)
        shape = res[0]
        assert isinstance(shape, dict)

        # print(json.dumps(res, indent=2, ensure_ascii=False))
