"""通用 SRT 解析测试，不访问网络或真实字幕服务。"""

from unittest import TestCase

from jwf_common_python.parse_subtitle import parse_srt

CONTENT = "1\n00:00:01,250 --> 00:00:03,000\nHello\nworld\n\n"


class TestParseSrt(TestCase):
    def test_srt_timestamps(self):
        """场景：带 BOM 和 Windows 换行的字幕以及非法时间轴；解析合法数据应保持文本，逆序或越界时间应拒绝入库。"""
        self.assertEqual(
            parse_srt("\ufeff" + CONTENT.replace("\n", "\r\n"))[0][
                "text"
            ],
            "Hello\nworld",
        )
        for content in [
            CONTENT.replace("00:00:03,000", "00:00:00,000"),
            CONTENT.replace("00:00:01,250", "00:60:01,250"),
        ]:
            with (
                self.subTest(content=content),
                self.assertRaisesRegex(ValueError, "时间轴"),
            ):
                parse_srt(content)

    def test_multiple_blocks(self):
        """场景：多条字幕包含多行文本和毫秒时间；解析两段 SRT，预期保留顺序与换行，并返回秒数和持续时间。"""
        content = CONTENT + "2\n00:01:00,500 --> 00:01:02,750\nNext\n"
        self.assertEqual(parse_srt(content), [
            {"text": "Hello\nworld", "start": 1.25, "duration": 1.75},
            {"text": "Next", "start": 60.5, "duration": 2.25},
        ])

    def test_invalid_content(self):
        """场景：空内容、普通文本或合法字幕中混入损坏段落；调用解析器，预期报错而非返回不完整字幕。"""
        for content in ("", "invalid", CONTENT + "broken"):
            with self.subTest(content=content), self.assertRaises(ValueError):
                parse_srt(content)
