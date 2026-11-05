import logging
from abc import ABC, abstractmethod
from collections.abc import ByteString

import requests


class Storage(ABC):
    @abstractmethod
    def __init__(self, **kwargs) -> None:
        ...

    @abstractmethod
    def save(self, filename: str, content: ByteString) -> tuple[bool, str]:
        ...

    @abstractmethod
    def load(self, filename: str) -> tuple[bool, bytes]:
        ...

    def download_audio_file(self, url: str) -> bytes:
        try:
            response = requests.get(url=url)
        except Exception as e:
            raise ValueError(f"download error: {e}")
        if response.status_code != 200:
            raise ValueError(f"download failed,status code: {response.status_code}")
        logging.info(f"download success: {url}")
        return response.content
