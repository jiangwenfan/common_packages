import os
from collections.abc import ByteString

from common_packages.file_storage.file_interface import Storage


class LocalStorage(Storage):
    def __init__(self, **kwargs) -> None:
        """
            1. try to create directory if not exist
        Args:
            storage_home_dir(str): 本地存储的家目录

        Raises:
            ValueError: _description_
            ValueError: _description_
        """
        if "storage_home_dir" not in kwargs:
            raise ValueError("storage_home_dir must be provided")
        storage_home_dir = kwargs["storage_home_dir"]
        # 判断目录是否存在，不存在则创建
        if not os.path.exists(storage_home_dir):
            try:
                os.mkdir(storage_home_dir)
            except Exception as e:
                raise ValueError(
                    "storage_home_dir does not exist and cannot be created"
                )
        self.storage_home_dir = storage_home_dir

    def save(self, filename: str, content: ByteString) -> tuple[bool, str]:
        """保存文件内容到指定文件中.filename是文件名，不是文件全部路径"""
        # 完整路径
        file_path: str = os.path.join(self.storage_home_dir, filename)
        try:
            with open(file_path, "wb") as f:
                f.write(content)
        except Exception as e:
            return False, e
        else:
            return True, file_path

    def load(self, filename: str) -> tuple[bool, bytes]:
        try:
            with open(os.path.join(self.storage_home_dir, filename), "rb") as f:
                content: bytes = f.read()
        except Exception as e:
            return False, e
        else:
            return True, content
