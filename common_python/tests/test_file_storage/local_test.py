import os


class TestLocalStorage:
    def test_save_file(self, local_obj, local_config):
        # 要保存的文件名和内容
        file_name: str = "test_save_file.txt"
        content: bytes = "abc测试123!@!@".encode()

        # 保存文件
        status, file_path = local_obj.save(file_name, content)

        # 断言保存成功
        assert status is True
        except_file_path = os.path.join(local_config["storage_home_dir"], file_name)
        assert file_path == except_file_path

    def test_load_file(self, local_obj, local_config):
        file_name: str = "test_save_file.txt"
        content: bytes = "abc测试123!@!@".encode()

        # 提前写入文件
        file_path = os.path.join(local_config["storage_home_dir"], file_name)
        with open(file_path, "wb") as f:
            f.write(content)

        # 读取文件
        status, actual_content = local_obj.load(file_name)
        assert status is True
        assert actual_content == content

    # def test_save_binary_file(self, local_obj, get_local_config):
    #     image: bytes = image_utils.create_image(100, 100, (255, 255, 255))
    #     local = LocalStorage(**config["storage"]["local"])
    #     status, file_path = local.save("test_save_image.png", image)
    #     assert status == True
    #     assert (
    #         file_path
    #         == f'{config["storage"]["local"]["storage_home_dir"]}test_save_image.png'
    #     )

    # def test_load_binary_file(self):
    #     config: dict = get_config()
    #     local = LocalStorage(**config["storage"]["local"])
    #     status, content = local.load("test_save_image.png")
    #     assert status == True
    #     assert content == image_utils.create_image(100, 100, (255, 255, 255))
