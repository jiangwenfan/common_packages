import datetime
import hashlib
import hmac
from datetime import timedelta


# 参考签名工具
def generate_tencent_key(secret_key,key,secret_id,method="get",**kwargs) -> str:
    # 1. KeyTime
    current_time = datetime.datetime.now()
    future_time = current_time + timedelta(minutes=30)

    start = current_time.timestamp()
    end = future_time.timestamp()

    key_time = f"{int(start)};{int(end)}"
    print(f"步骤一: key_time: {key_time}\n")


    # 2. SignKey
    sign_key = hmac.new(
        secret_key.encode("utf-8"), key_time.encode("utf-8"), hashlib.sha1
    ).hexdigest()
    print(f"步骤二: sign_key: {sign_key}\n")


    # 5. http_string
    http_string = f"{method}\n/{key}\n\n\n"

    # http_string = f"put\n/{key}\n\n\n"
    print(f"步骤五： http_string: {repr(http_string)}\n")  # get\n/picture.jpg\n\n\n

    # 6. StringToSign
    sha1 = hashlib.sha1()
    sha1.update(http_string.encode("utf-8"))
    http_string_sha1 = sha1.hexdigest()
    string_to_sign = f"sha1\n{key_time}\n{http_string_sha1}\n"
    print(f"步骤六: string_to_sign: {repr(string_to_sign)}\n")


    # 7. Signature
    signature = hmac.new(
        sign_key.encode("utf-8"), string_to_sign.encode("utf-8"), hashlib.sha1
    ).hexdigest()
    print(f"步骤七: signature: {signature}")


    # 8. authorization
    authorization = f"q-sign-algorithm=sha1&q-ak={secret_id}&q-sign-time={key_time}&q-key-time={key_time}&q-header-list=&q-url-param-list=&q-signature={signature}"
    print(f"authorizaton: {authorization}\n")
    return authorization