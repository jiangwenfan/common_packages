# YoudaoProviderHandle().get_resource(input_words=json.loads(words))


import hashlib
import json
import logging
import os
import time
import uuid
from abc import ABCMeta, abstractclassmethod, abstractmethod
from typing import TypedDict

import requests


class WordInfo(TypedDict):
    word: str
    translation: dict
    speak_url: dict
    phonetic: dict
    word_type: list
    grammar_info: list
    extended_info: list[dict]
    grammar_info: str

class Translate(metaclass=ABCMeta):
    @abstractmethod
    def __init__(self,**kwargs) -> None:
        ...

    @abstractmethod
    def translate(self,word: str) -> dict:
        ...

    @abstractclassmethod
    @classmethod
    def format_word_response(self,response: dict) -> WordInfo:
        ...

    @abstractclassmethod
    @classmethod
    def format_sentence_response(self,response: dict) -> WordInfo:
        ...

    @abstractclassmethod
    @classmethod
    def download_audio_file(self,url: str) -> bytes:
        ...

    def generate_word_audio_file_name(self,word: str,audio_type: str) -> str:
        file_id: str = hashlib.md5(word.encode("utf-8")).hexdigest()
        file_name: str = f"word_youdao_{audio_type}_{file_id}.mp3"
        absolute_audio_file_path = os.path.join("/opt/",file_name)
        return absolute_audio_file_path



