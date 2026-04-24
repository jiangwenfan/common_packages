import pytest


class TestOauth2Google:
    # code1,code2,code3 必须是通过 get_web_auth_url() 认证之后，且没有被使用过的code
    code1 = "xxx"
    code2 = "xxx"
    code3 = "xxx"

    @pytest.mark.skip("当修改代码之后,手动测试")
    def test_get_web_auth_url(slef, oauth2_google_obj):
        url = oauth2_google_obj.get_web_auth_url()
        # print("\n", url, "\n", type(url))
        assert isinstance(url, str)
        assert url.startswith("https://accounts.google.com/o/oauth2/v2/auth")

    @pytest.mark.skip("当修改代码之后,手动测试")
    def test_get_access_token(self, oauth2_google_obj):
        access_token = oauth2_google_obj.get_access_token(self.code1)
        # print("\n", access_token, "\n", type(access_token))
        assert isinstance(access_token, str)

    @pytest.mark.skip("当修改代码之后,手动测试")
    def test_get_raw_user_info(self, oauth2_google_obj):
        access_token = oauth2_google_obj.get_access_token(self.code2)
        user_info = oauth2_google_obj.get_raw_user_info(access_token)
        # import json

        # print("\n", json.dumps(user_info, indent=2), "\n", type(user_info))
        assert isinstance(user_info, dict)

    def test_format_user_info(self, oauth2_google_obj):
        raw_info = {
            "resourceName": "people/110xxxx6656",
            "etag": "%EgwBAxxxxBAECBQc=",
            "names": [
                {
                    "metadata": {
                        "primary": True,
                        "source": {"type": "PROFILE", "id": "110xxxxx56"},
                        "sourcePrimary": True,
                    },
                    "displayName": "姜xx",
                    "familyName": "姜",
                    "givenName": "xx",
                    "displayNameLastFirst": "姜xx",
                    "unstructuredName": "姜xx",
                }
            ],
            "photos": [
                {
                    "metadata": {
                        "primary": True,
                        "source": {"type": "PROFILE", "id": "1xxxx11xxxx56"},
                    },
                    "url": "https://lh3.googleusercontent.com/a/\
ACgxxxxx_ZRPxxxxxxxeD31o=s100",
                }
            ],
            "emailAddresses": [
                {
                    "metadata": {
                        "primary": True,
                        "verified": True,
                        "source": {"type": "ACCOUNT", "id": "1xxxx852157xxxxx"},
                        "sourcePrimary": True,
                    },
                    "value": "zxxxx7@gmail.com",
                },
                {
                    "metadata": {
                        "verified": True,
                        "source": {"type": "ACCOUNT", "id": "xxxx157832xxxx"},
                    },
                    "value": "xxx@xxx.com",
                },
            ],
        }

        res = oauth2_google_obj.format_user_info(raw_info)
        # print("\n", res, "\n", type(res))
        assert isinstance(res, dict)
        assert "email" in res
        assert "name" in res
        assert "avatar_content" in res

    @pytest.mark.skip("当修改代码之后,手动测试")
    def test_get_user_info(self, oauth2_google_obj):
        user_info = oauth2_google_obj.get_user_info(self.code3)
        # print("\n", user_info, "\n", type(user_info))
        assert isinstance(user_info, dict)
        assert "email" in user_info
        assert "name" in user_info
        assert "avatar_content" in user_info
