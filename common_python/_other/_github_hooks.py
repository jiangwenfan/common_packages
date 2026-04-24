from hashlib import sha256
from hmac import HMAC, compare_digest

from flask import Flask, jsonify, request

app = Flask(__name__)


def verify_signature(req):
    received_sign = req.headers.get("X-Hub-Signature-256").split("sha256=")[-1].strip()
    print("接收到的摘要头:", received_sign)
    secret = b"ac1a76cbaa742daacc8bb0f500ecd4dc3d64fe18"
    expected_sign = HMAC(key=secret, msg=req.data, digestmod=sha256).hexdigest()
    print("计算之后的摘要头:", expected_sign)
    return compare_digest(received_sign, expected_sign)


@app.route("/hook", methods=["POST", "GET"])
def webhook():
    if request.method == "POST":
        if verify_signature(request):
            return jsonify({"status": 200})
        return "Forbidden", 403
    return "Not allowed", 405


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=7071)
