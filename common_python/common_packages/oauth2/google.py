import requests


class Oauth2Google:
    def __init__(
        self, client_id: str, client_secret: str, redirect_uri: str, scope: str
    ):
        self.client_id = client_id
        self.client_secret = client_secret
        self.response_type = "code"
        self.access_type = "online"
        self.grant_type = "authorization_code"
        # 认证完成之后的回调地址,必须与google console中配置的一致
        self.redirect_uri = redirect_uri
        # 请求的权限
        self.scope = scope

    def get_web_auth_url(self) -> str:
        """获取web页面上认证地址"""
        url = f"https://accounts.google.com/o/oauth2/v2/auth?\
client_id={self.client_id}&response_type={self.response_type}&access_type={self.access_type}\
&redirect_uri={self.redirect_uri}&scope={self.scope}"
        return url

    def get_access_token(self, code: str) -> str:
        """根据code获取access_token"""
        url = "https://oauth2.googleapis.com/token"
        data = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "code": code,
            "grant_type": self.grant_type,
            "redirect_uri": self.redirect_uri,
        }
        response = requests.post(
            url,
            data=data,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        if response.status_code != 200:
            raise Exception(f"获取access_token失败 {response.status_code} {response.text}")
        res = response.json()
        access_token = res["access_token"]
        return access_token

    def get_raw_user_info(self, access_token: str) -> dict:
        """获取原生的用户信息

        email: 用户邮箱
        name: 用户名字
        avatar_content: 用户头像字节流
        """
        url = "https://people.googleapis.com/v1/people/me?personFields=\
names,emailAddresses,genders,nicknames,phoneNumbers,photos"
        response = requests.get(
            url, headers={"Authorization": f"Bearer {access_token}"}
        )
        if response.status_code != 200:
            raise Exception(f"获取用户信息失败 {response.status_code} {response.text}")

        res = response.json()
        return res

    def format_user_info(self, raw_user_info: dict) -> dict:
        """格式化用户信息"""
        _ = {
            "resourceName": "people/110311852157832716656",
            "etag": "%EgwBAxxxPj8axxxxBQc=",
            "names": [
                {
                    "metadata": {
                        "primary": True,
                        "source": {"type": "PROFILE", "id": "1185215783"},
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
                        "source": {"type": "PROFILE", "id": "1215783xx6"},
                    },
                    "url": "https://lh3.googleusercontent.com/a/\
ACg8ocLGxxxxkIpZx7vEfeD31o=s100",
                }
            ],
            "emailAddresses": [
                {
                    "metadata": {
                        "primary": True,
                        "verified": True,
                        "source": {"type": "ACCOUNT", "id": "11xxxxxx656"},
                        "sourcePrimary": True,
                    },
                    "value": "xxxx@gmail.com",
                },
                {
                    "metadata": {
                        "verified": True,
                        "source": {"type": "ACCOUNT", "id": "1103xxxxxx56"},
                    },
                    "value": "xxxx@xxx.com",
                },
            ],
        }
        # 1. 获取用户邮箱
        email = None
        emailAddresses = raw_user_info["emailAddresses"]
        for email_info in emailAddresses:
            # 获取主邮箱
            metadata = email_info["metadata"]
            if metadata.get("primary"):
                # 当primary存在，且为True时，表示为主邮箱
                email = email_info["value"]
                break

        # 2. 获取用户名字
        name = None
        names = raw_user_info["names"]
        for name_info in names:
            if name_info.get("displayName"):
                # 当displayName存在时，表示为用户名
                name = name_info["displayName"]
                break

        # 3. 获取用户头像
        photo_url = None
        photos = raw_user_info["photos"]
        for photo_info in photos:
            if photo_info.get("url"):
                # 当url存在时，表示为用户头像
                photo_url = photo_info["url"]
                break
        # 3.1 如果有头像,获取图片字节流
        avatar_content = None
        if photo_url:
            response = requests.get(photo_url)
            if response.status_code == 200:
                avatar_content = response.content

        return {
            "email": email,
            "name": name,
            "avatar_content": avatar_content,
        }

    def get_user_info(self, code: str) -> dict:
        """获取用户信息,格式化后返回"""
        access_token = self.get_access_token(code)
        raw_user_info = self.get_raw_user_info(access_token)
        user_info = self.format_user_info(raw_user_info)
        return user_info
