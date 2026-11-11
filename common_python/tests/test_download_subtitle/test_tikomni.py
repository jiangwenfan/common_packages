"""TikOmni 协议回归测试；所有网络和轮询等待均使用 mock。"""

from unittest import TestCase
from unittest.mock import Mock, patch
import requests
from jwf_common_python.download_subtitle import tikomni


class TestTikomniDownload(TestCase):
    video_id = "dQw4w9WgXcQ"
    content = "1\n00:00:01,250 --> 00:00:03,000\nHello\nworld\n\n"

    def setUp(self):
        self.client = tikomni.TikomniSubtitleDownloader("test-token")

    @patch("jwf_common_python.download_subtitle.tikomni.requests.get")
    def test_sync_download(self, get):
        """场景：视频同时有人工作成及自动生成英文；模拟列表与同步内容响应，验证优先人工英文、鉴权和时间轴转换。"""
        get.side_effect = [
            Mock(
                json=Mock(
                    return_value={
                        "captions": [{"language_code": "a.en"}, {"language_code": "en"}]
                    }
                )
            ),
            Mock(json=Mock(return_value={"content": self.content})),
        ]
        result = self.client.download_youtube_subtitle(self.video_id)
        self.assertEqual(
            result["subtitles"],
            [{"text": "Hello\nworld", "start": 1.25, "duration": 1.75}],
        )
        self.assertEqual(get.call_args.kwargs["params"]["language_code"], "en")
        self.assertEqual(
            get.call_args.kwargs["headers"], {"Authorization": "Bearer test-token"}
        )
        self.assertEqual(get.call_args.kwargs["timeout"], 30)

    @patch("jwf_common_python.download_subtitle.tikomni.time.sleep")
    @patch(
        "jwf_common_python.download_subtitle.tikomni.TikomniSubtitleDownloader._request"
    )
    def test_async_download(self, request, sleep):
        """场景：自动英文字幕下载进入异步；依次返回排队、处理中、完成，验证用原任务 ID 轮询并生成字幕。"""
        request.side_effect = [
            {"captions": [{"language_code": "a.en"}]},
            {"status": "processing", "job_id": "test-job"},
            {"status": "queued"},
            {"status": "active"},
            {"status": "completed", "content": self.content},
        ]
        result = self.client.download_youtube_subtitle(self.video_id)
        self.assertTrue(result["is_generated"])
        self.assertEqual(
            result["subtitles"],
            [{"text": "Hello\nworld", "start": 1.25, "duration": 1.75}],
        )
        request.assert_called_with(
            "get_video_captions_result", {"job_id": "test-job", "format": "srt"}
        )
        self.assertEqual(sleep.call_count, 3)
        sleep.assert_called_with(3)

    @patch("jwf_common_python.download_subtitle.tikomni.time.sleep")
    @patch(
        "jwf_common_python.download_subtitle.tikomni.TikomniSubtitleDownloader._request"
    )
    def test_async_list_completed(self, request, sleep):
        """场景：列表请求直接进入异步且完成时带英文内容；执行下载，验证复用结果而不重复付费请求。"""
        request.side_effect = [
            {"status": "processing", "job_id": "test-job"},
            {
                "status": "completed",
                "available_languages": ["en"],
                "language_code": "en",
                "content": self.content,
            },
        ]
        self.assertEqual(
            len(self.client.download_youtube_subtitle(self.video_id)["subtitles"]), 1
        )
        self.assertEqual(request.call_count, 2)

    @patch(
        "jwf_common_python.download_subtitle.tikomni.TikomniSubtitleDownloader._request"
    )
    def test_unavailable_or_invalid_content(self, request):
        """场景：无字幕、仅其他语言、空内容或损坏 SRT；模拟上游数据后下载，预期报错，避免缓存为成功的空字幕。"""
        for responses in [
            [{"captions": []}],
            [{"captions": [{"language_code": "ja"}]}],
            [{"captions": [{"language_code": "en"}]}, {"content": ""}],
            [{"captions": [{"language_code": "en"}]}, {"content": "invalid"}],
        ]:
            with self.subTest(responses=responses):
                request.side_effect = responses
                with self.assertRaises(ValueError):
                    self.client.download_youtube_subtitle(self.video_id)

    @patch("jwf_common_python.download_subtitle.tikomni.time.sleep")
    @patch(
        "jwf_common_python.download_subtitle.tikomni.TikomniSubtitleDownloader._request"
    )
    def test_async_failure_and_timeout(self, request, sleep):
        """场景：上游一直排队或返回失败；缩短轮询次数以快速测试，验证有限重试后报错、缺少任务 ID 也不会循环请求。"""
        with patch.object(tikomni, "_MAX_POLLS", 2):
            request.return_value = {"status": "queued"}
            with self.assertRaisesRegex(ValueError, "超时"):
                self.client._resolve({"status": "processing", "job_id": "test-job"})
            self.assertEqual(request.call_count, 2)
        request.return_value = {"status": "failed"}
        with self.assertRaisesRegex(ValueError, "失败"):
            self.client._resolve({"status": "processing", "job_id": "test-job"})
        with self.assertRaisesRegex(ValueError, "job_id"):
            self.client._resolve({"status": "processing"})

    @patch("jwf_common_python.download_subtitle.tikomni.requests.get")
    def test_credentials_and_network_errors(self, get):
        """场景：缺少令牌或上游 HTTP/网络失败；调用下载后应报可读错误，缺令牌时不发请求，也不泄漏底层错误内容。"""
        with (self.assertRaisesRegex(ValueError, "api_token"),):
            tikomni.download_youtube_subtitle(self.video_id, api_token="")
        get.assert_not_called()
        get.side_effect = requests.RequestException("sensitive upstream detail")
        with self.assertRaisesRegex(ValueError, "TikOmni 字幕请求失败"):
            self.client.download_youtube_subtitle(self.video_id)

    @patch("jwf_common_python.download_subtitle.tikomni.requests.get")
    def test_raw_srt_response(self, get):
        """场景：同步接口直接返回 SRT 文件而非 JSON；模拟 JSON 解码失败，验证仍可读取正文并保留毫秒精度。"""
        get.side_effect = [
            Mock(json=Mock(return_value={"captions": [{"language_code": "en"}]})),
            Mock(json=Mock(side_effect=ValueError), text=self.content),
        ]
        # 从公开函数调用，确保上游原始 SRT 在返回前已解析为完整结果字典。
        result = tikomni.download_youtube_subtitle(self.video_id, api_token="test-token")
        self.assertEqual(result, {
            "video_id": self.video_id,
            "language": "English",
            "language_code": "en",
            "is_generated": False,
            "subtitles": [{"text": "Hello\nworld", "start": 1.25, "duration": 1.75}],
        })

    @patch("jwf_common_python.download_subtitle.tikomni.requests.get")
    def test_real_response_envelope(self, get):
        """场景：真实接口把字幕列表和内容放在 data 内，而非顶层。

        前置数据采用临时真实请求观察到的公共响应结构，省略请求标识等元数据；
        模拟列表和内容响应后执行完整下载，预期读出英文字幕，不再误报无字幕。
        """
        payloads = [
            {"captions": [{"language_code": "en", "language_name": "English"}]},
            {"content": self.content},
        ]
        get.side_effect = [
            Mock(json=Mock(return_value={"code": 200, "data": data}))
            for data in payloads
        ]
        result = self.client.download_youtube_subtitle(self.video_id)
        self.assertEqual(result["language_code"], "en")
        self.assertEqual(result["subtitles"][0]["text"], "Hello\nworld")

    @patch("jwf_common_python.download_subtitle.tikomni.requests.get")
    def test_response_envelope_errors(self, get):
        """场景：HTTP 成功但业务失败或 data 缺失；模拟公共响应并请求列表，预期明确报错，不将异常响应当作无字幕。"""
        for payload, message in [
            ({"code": 500}, "业务错误"),
            ({"code": 200}, "data"),
            ({"code": 200, "data": None}, "data"),
        ]:
            with self.subTest(payload=payload):
                get.return_value = Mock(json=Mock(return_value=payload))
                with self.assertRaisesRegex(ValueError, message):
                    self.client._request(
                        "get_video_captions", {"video_id": self.video_id}
                    )

    @patch("jwf_common_python.download_subtitle.tikomni.requests.get")
    def test_http_error_includes_status_and_response(self, get):
        """场景：真实额度不足返回 HTTP 402；使用 requests.Response 模拟 HTTP 错误，验证异常包含状态码和完整业务响应且隐藏令牌。"""
        response = requests.Response()
        response.status_code = 402
        response._content = (
            b'{"code":402,"message":"Insufficient credits","token":"test-token"}'
        )
        get.return_value = response
        with self.assertRaises(ValueError) as raised:
            self.client._request("get_video_captions", {"video_id": self.video_id})
        message = str(raised.exception)
        self.assertIn("HTTP 402", message)
        self.assertIn('"message":"Insufficient credits"', message)
        self.assertIn("[REDACTED]", message)
        self.assertNotIn("test-token", message)

    @patch("jwf_common_python.download_subtitle.tikomni.requests.get")
    def test_network_error_without_response(self, get):
        """场景：连接超时尚未收到 HTTP 响应；模拟超时异常，验证明确提示无状态码、保留错误类型与原因并隐藏令牌。"""
        get.side_effect = requests.Timeout("connection timeout test-token")
        with self.assertRaises(ValueError) as raised:
            self.client._request("get_video_captions", {"video_id": self.video_id})
        message = str(raised.exception)
        self.assertIn("无状态码", message)
        self.assertIn("Timeout: connection timeout", message)
        self.assertNotIn("test-token", message)
