from tests.fixtures.db import mysql_op, reset_default_data, start_stop_mysql
from tests.fixtures.geography import china_district_amap, search_location_amap
from tests.fixtures.llm import llm_baidu_ernie_obj
from tests.fixtures.oauth2 import oauth2_google_obj
from tests.fixtures.storage import (
    local_config,
    local_obj,
    tencent_cos_config,
    tencent_cos_obj,
)
from tests.fixtures.translate import (
    microsoft_all_raw_backTranslations,
    microsoft_word_example_data,
    microsoft_word_raw_response,
    sentence_translate_data,
    translate_microsoft_obj,
    word_translate_data,
)
from tests.fixtures.tts import tts_microsoft_obj
from tests.fixtures.utils import global_config
from tests.fixtures.weather import weather_amap, weather_wanwei

__all__ = [
    "global_config",
    "mysql_op",
    "start_stop_mysql",
    "global_config",
    "reset_default_data",
    "local_config",
    "tencent_cos_config",
    "local_obj",
    "tencent_cos_obj",
    "translate_microsoft_obj",
    "microsoft_word_example_data",
    "microsoft_word_raw_response",
    "microsoft_all_raw_backTranslations",
    "sentence_translate_data",
    "word_translate_data",
    "tts_microsoft_obj",
    "llm_baidu_ernie_obj",
    "oauth2_google_obj",
    "china_district_amap",
    "search_location_amap",
    "weather_amap",
    "weather_wanwei",
]
