"""基于原始请求体的 GitHub SHA-256 验签，不记录密钥或签名。"""

from __future__ import annotations

import hashlib
import hmac
import re
from collections.abc import Callable


def _secret_bytes(secret: str | bytes) -> bytes:
    if isinstance(secret, str):
        secret = secret.encode("utf-8")
    if not isinstance(secret, bytes):
        raise TypeError("secret 必须为 str 或 bytes")
    if not secret:
        raise ValueError("secret 不能为空")
    return secret


def verify_signature(
    payload: bytes, secret: str | bytes, signature_header: str | None
) -> bool:
    """校验 X-Hub-Signature-256，返回 bool；密钥必须由调用方传入。

    payload 必须为原始请求体字节，不能是重新序列化的 JSON。
    签名缺失或格式错误时返回 False，配置/参数类型错误时抛出异常。
    """
    key = _secret_bytes(secret)
    if not isinstance(payload, bytes):
        raise TypeError("payload 必须为原始请求体 bytes")
    if (
        not isinstance(signature_header, str)
        or re.fullmatch(r"sha256=[0-9a-f]{64}", signature_header) is None
    ):
        return False
    expected = "sha256=" + hmac.new(key, payload, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, signature_header)


def create_webhook_app(
    secret: str | bytes,
    *,
    path: str = "/hook",
    handler: Callable[[bytes, str | None, str | None], None] | None = None,
):
    """返回 Flask 应用，不启动服务器；只有调用此函数才导入 Flask。

    只接受 POST。验签失败返回 403，成功时依次调用
    handler(payload, event, delivery_id)，然后返回 {"status": 200}。
    请求体不强制为 JSON，回调自行解析；回调失败由 Flask 按异常处理，不返回成功。
    """
    key = _secret_bytes(secret)
    if (
        not isinstance(path, str)
        or not path.startswith("/")
        or "<" in path
        or ">" in path
    ):
        raise ValueError("path 必须为以 / 开头的静态路由路径")
    if handler is not None and not callable(handler):
        raise TypeError("handler 必须可调用或为 None")
    try:
        from flask import Flask, jsonify, request
    except ImportError as exc:
        raise ImportError("HTTP 接入需要可选依赖：pip install flask") from exc

    app = Flask(__name__)

    def webhook():
        payload = request.get_data(cache=True)
        if not verify_signature(
            payload, key, request.headers.get("X-Hub-Signature-256")
        ):
            return jsonify({"error": "invalid_signature"}), 403
        if handler is not None:
            handler(
                payload,
                request.headers.get("X-GitHub-Event"),
                request.headers.get("X-GitHub-Delivery"),
            )
        return jsonify({"status": 200})

    app.add_url_rule(
        path, endpoint="github_webhook", view_func=webhook, methods=["POST"]
    )
    return app
