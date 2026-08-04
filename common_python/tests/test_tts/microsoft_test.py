import logging

logging.basicConfig(level=logging.INFO)



class TestTTSMicrosoft:
    def test_fetch_access_token(self, tts_microsoft_obj):
        access_token = tts_microsoft_obj.fetch_access_token()
        # print(access_token, type(access_token))
        assert isinstance(access_token, str)
        assert len(access_token) > 50

    def test_generate_xml_data(self, tts_microsoft_obj):
        text = "hello world"
        xml_data = tts_microsoft_obj.generate_xml_data(text)
        # print(xml_data, type(xml_data))
        assert isinstance(xml_data, str)
        # TODO 验证xml格式是否正确

    def test_convert_text_to_speech(self, tts_microsoft_obj):
        # text = "hello world"
        text = "你好，世界"
        wav_data = tts_microsoft_obj.convert_text_to_speech(text)
        # print(type(wav_data))
        assert isinstance(wav_data, bytes)
        # TODO 验证音频可以播放
        # with open("test_en.mp3", "wb") as f:
        #     f.write(wav_data)
        with open("test_zh.mp3", "wb") as f:
            f.write(wav_data)
