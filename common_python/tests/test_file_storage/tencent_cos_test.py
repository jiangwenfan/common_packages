class TestTencentCosStorage:
    def test_save_image(self, tencent_cos_obj, tencent_cos_config):
        # 要保存的文件名和内容
        file_name: str = "test_save_file.txt"
        content: bytes = "abc测试123!@!@".encode()

        # 保存文件
        status, actual_file_name = tencent_cos_obj.save(
            filename=file_name, content=content
        )

        # 断言保存成功
        assert status is True
        assert actual_file_name == file_name

    def test_load_image(self, tencent_cos_obj, tencent_cos_config):
        # 已经保存的文件名和内容
        file_name: str = "test_save_file.txt"
        content: bytes = "abc测试123!@!@".encode()

        # 读取文件
        status, actual_content = tencent_cos_obj.load(file_name)

        # 断言读取成功
        assert status is True
        assert actual_content == content
