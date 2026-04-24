class TestLLMBaiduErnie:
    def test_get_token_info(self, llm_baidu_ernie_obj):
        res = llm_baidu_ernie_obj.get_token_info()
        # print(res, type(res))
        assert isinstance(res, dict)
        assert hasattr(llm_baidu_ernie_obj, "token_info")
        assert "access_token" in res
        assert "expire_time" in res

    def test_send_model_request(self, llm_baidu_ernie_obj):
        text = "你好"
        res = llm_baidu_ernie_obj.send_model_request(text)
        # print(res, type(res))
        assert isinstance(res, str)

    def test_is_natural_language(self, llm_baidu_ernie_obj):
        text = "6.      Babel can be configured in a file called .babelrc.json.\
Create this file at the root of the project with the following content: "
        status = llm_baidu_ernie_obj.is_natural_language(text)
        # print(status, type(status))
        assert isinstance(status, bool)
        assert status is True
