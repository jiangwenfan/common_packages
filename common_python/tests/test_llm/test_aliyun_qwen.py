"""使用 mock 验证翻译协议、跨实例限速及错误处理，不访问外部服务。"""

from unittest.mock import Mock, patch

import pytest
import requests

from jwf_common_python.llm import aliyun_qwen as qwen


@pytest.fixture(autouse=True)
def reset_request_clock():
    """隔离进程级限速状态，避免测试之间相互影响。"""
    qwen._last_request_started_at = None
    yield
    qwen._last_request_started_at = None


@pytest.fixture
def post():
    """所有请求都使用模拟响应，禁止真实 HTTP 调用。"""
    with patch.object(qwen.requests, "post") as mock:
        mock.return_value = Mock(status_code=200)
        mock.return_value.json.return_value = {
            "choices": [{"message": {"content": "你好"}}]
        }
        yield mock


def test_translation_defaults(post):
    client = qwen.LLMAliyunQwen("test-key")
    result = client.translate_text("hello")
    post.assert_called_once_with(
        qwen.DASHSCOPE_CHAT_URL,
        headers={
            "Content-Type": "application/json",
            "Authorization": "Bearer test-key",
        },
        json={
            "model": "qwen-mt-turbo",
            "messages": [{"role": "user", "content": "hello"}],
            "translation_options": {"source_lang": "auto", "target_lang": "Chinese"},
        },
        timeout=60.0,
    )
    assert result == post.return_value.json.return_value
    assert client.get_translated_text(result) == "你好"


def test_custom_parameters(post):
    qwen.LLMAliyunQwen("key").translate_text(
        "hello",
        model="custom",
        source_lang="English",
        target_lang="Japanese",
        timeout=5,
    )
    kwargs = post.call_args.kwargs
    assert kwargs["timeout"] == 5
    assert kwargs["json"]["model"] == "custom"
    assert kwargs["json"]["translation_options"] == {
        "source_lang": "English",
        "target_lang": "Japanese",
    }


def test_shared_interval_across_clients(post):
    """即使每次新建客户端，仍应遵守进程内最小请求间隔。"""
    with patch.object(qwen.time, "monotonic", side_effect=[10, 11, 12]), patch.object(
        qwen.time, "sleep"
    ) as sleep:
        qwen.LLMAliyunQwen("a").translate_text("first")
        qwen.LLMAliyunQwen("b").translate_text("second")
    sleep.assert_called_once_with(1)
    assert post.call_count == 2


@pytest.mark.parametrize("interval", [0, -1, "0"])
def test_disabled_interval(post, interval):
    with patch.object(qwen.time, "monotonic", return_value=10), patch.object(
        qwen.time, "sleep"
    ) as sleep:
        client = qwen.LLMAliyunQwen("key", request_interval=interval)
        client.translate_text("first")
        client.translate_text("second")
    sleep.assert_not_called()


def test_custom_interval(post):
    with patch.object(qwen.time, "monotonic", side_effect=[10, 11, 15]), patch.object(
        qwen.time, "sleep"
    ) as sleep:
        client = qwen.LLMAliyunQwen("key", request_interval=5)
        client.translate_text("first")
        client.translate_text("second")
    sleep.assert_called_once_with(4)


@pytest.mark.parametrize("second_status", [200, 429])
def test_rate_limit_retries_only_once(post, second_status):
    """首次限流后等待；第二次仍限流则原样抛出异常。"""
    limited = Mock(status_code=429)
    error = requests.HTTPError("429")
    limited.raise_for_status.side_effect = error
    success = post.return_value
    post.side_effect = [limited, success if second_status == 200 else limited]
    with patch.object(qwen.time, "monotonic", side_effect=[10, 10.5, 12]), patch.object(
        qwen.time, "sleep"
    ) as sleep:
        client = qwen.LLMAliyunQwen("key")
        if second_status == 200:
            assert client.translate_text("hello") == success.json.return_value
        else:
            with pytest.raises(requests.HTTPError) as exc:
                client.translate_text("hello")
            assert exc.value is error
    sleep.assert_called_once_with(1.5)
    assert post.call_count == 2


@pytest.mark.parametrize("status", [400, 401, 500])
def test_other_http_errors_not_retried(post, status):
    post.return_value.status_code = status
    post.return_value.raise_for_status.side_effect = requests.HTTPError(str(status))
    with pytest.raises(requests.HTTPError):
        qwen.LLMAliyunQwen("key").translate_text("hello")
    assert post.call_count == 1


def test_timeout_not_retried(post):
    post.side_effect = requests.Timeout("timeout")
    with pytest.raises(requests.Timeout):
        qwen.LLMAliyunQwen("key").translate_text("hello")
    assert post.call_count == 1


def test_missing_key(post):
    with pytest.raises(ValueError, match="api_key"):
        qwen.LLMAliyunQwen("")
    post.assert_not_called()
