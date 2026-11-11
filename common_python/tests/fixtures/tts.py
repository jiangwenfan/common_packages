import pytest

from jwf_common_python.tts.azure import TTSMicrosoft


@pytest.fixture(scope="class")
def tts_microsoft_obj(global_config):
    tts_config = global_config["tts"]["microsoft"]
    tts = TTSMicrosoft(**tts_config)
    return tts
