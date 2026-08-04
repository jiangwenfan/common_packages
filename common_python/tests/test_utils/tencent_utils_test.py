import requests
from .. import get_config
from common_packages.utils.tencent_utils import generate_tencent_key


def test_generate_tencent_key():
    config = get_config()["storage"]["tencent_cos"]
    config["key"] = "test.png"
    authorization = generate_tencent_key(**config)
    print(authorization)
