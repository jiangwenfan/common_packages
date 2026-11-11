"""视频合并的参数、失败清理及真实 FFmpeg 集成测试。"""

import errno
import hashlib
import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from jwf_common_python.video import merge_directory, merge_videos, probe_video
from jwf_common_python.video.merge import _publish


FFMPEG = shutil.which("ffmpeg")
FFPROBE = shutil.which("ffprobe")


class ValidationTests(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.root = Path(directory.name)
        self.source = self.root / "source.mp4"
        self.source.write_bytes(b"source")
        self.output = self.root / "output.mp4"

    def test_invalid_paths_and_configuration_do_not_launch_processes(self):
        with patch("jwf_common_python.video.merge.subprocess.run") as run:
            for inputs, output, error in (
                ([], self.output, ValueError),
                (self.source, self.output, TypeError),
                ([self.root / "missing.mp4"], self.output, FileNotFoundError),
                ([self.root], self.output, ValueError),
                ([self.source], self.source, ValueError),
                ([self.source], self.root / "output", ValueError),
                (
                    [self.source],
                    self.root / "missing" / "output.mp4",
                    FileNotFoundError,
                ),
            ):
                with self.subTest(inputs=inputs, output=output), self.assertRaises(
                    error
                ):
                    merge_videos(inputs, output)
            for timeout in (0, True, float("inf"), float("nan")):
                with self.assertRaises(ValueError):
                    merge_videos([self.source], self.output, timeout=timeout)
            with self.assertRaises(TypeError):
                merge_videos([self.source], self.output, overwrite="false")
            run.assert_not_called()

    def test_existing_output_is_not_overwritten_by_default(self):
        self.output.write_bytes(b"original")
        with self.assertRaises(FileExistsError):
            merge_videos([self.source], self.output)
        self.assertEqual(self.output.read_bytes(), b"original")

    def test_symlink_and_hardlink_input_aliases_are_rejected(self):
        symlink = self.root / "symlink.mp4"
        symlink.symlink_to(self.source)
        hardlink = self.root / "hardlink.mp4"
        hardlink.hardlink_to(self.source)
        for output in (symlink, hardlink):
            with self.subTest(output=output), self.assertRaises(ValueError):
                merge_videos([self.source], output, overwrite=True)
        self.assertEqual(self.source.read_bytes(), b"source")

    def test_missing_ffmpeg_reports_installation_problem(self):
        with patch("jwf_common_python.video.merge.shutil.which", return_value=None):
            with self.assertRaisesRegex(FileNotFoundError, "FFmpeg"):
                merge_videos([self.source], self.output)

    def test_probe_returns_full_metadata_and_rejects_missing_video(self):
        metadata = {
            "streams": [{"codec_type": "video", "codec_name": "h264"}],
            "format": {"duration": "1.0"},
            "extra": "kept",
        }
        with patch(
            "jwf_common_python.video.merge.shutil.which", return_value="/fake/ffprobe"
        ), patch("jwf_common_python.video.merge.subprocess.run") as run:
            run.return_value = subprocess.CompletedProcess(
                [], 0, json.dumps(metadata), ""
            )
            self.assertEqual(probe_video(self.source), metadata)
            run.return_value = subprocess.CompletedProcess(
                [], 0, '{"streams": [{"codec_type": "audio"}]}', ""
            )
            with self.assertRaisesRegex(ValueError, "视频流"):
                probe_video(self.source)

    def test_publish_will_not_overwrite_a_concurrently_created_target(self):
        self.output.write_bytes(b"another result")
        with self.assertRaises(FileExistsError):
            _publish(self.source, self.output, False)
        self.assertEqual(self.output.read_bytes(), b"another result")

    def test_publish_falls_back_when_hardlinks_are_not_supported(self):
        with patch(
            "jwf_common_python.video.merge.os.link",
            side_effect=OSError(errno.ENOTSUP, "unsupported"),
        ):
            _publish(self.source, self.output, False)
        self.assertEqual(self.output.read_bytes(), b"source")
        self.assertEqual(self.source.read_bytes(), b"source")

    def test_failed_publish_copy_removes_only_its_own_incomplete_output(self):
        with patch(
            "jwf_common_python.video.merge.os.link",
            side_effect=OSError(errno.ENOTSUP, "unsupported"),
        ), patch(
            "jwf_common_python.video.merge.shutil.copyfileobj",
            side_effect=OSError("disk full"),
        ):
            with self.assertRaisesRegex(OSError, "disk full"):
                _publish(self.source, self.output, False)
        self.assertFalse(self.output.exists())
        self.assertEqual(self.source.read_bytes(), b"source")

    def test_directory_validation(self):
        with self.assertRaises(NotADirectoryError):
            merge_directory(self.source, self.output)
        with self.assertRaises(ValueError):
            merge_directory(self.root, self.output, extensions=[])
        with self.assertRaises(TypeError):
            merge_directory(self.root, self.output, extensions=".mp4")

    def test_zero_exit_code_with_error_log_is_not_reported_as_success(self):
        with patch(
            "jwf_common_python.video.merge.shutil.which", return_value="/fake/ffprobe"
        ), patch("jwf_common_python.video.merge.subprocess.run") as run:
            run.return_value = subprocess.CompletedProcess(
                [],
                0,
                '{"streams": [{"codec_type": "video"}]}',
                "failed to read packets",
            )
            with self.assertRaisesRegex(RuntimeError, "failed to read packets"):
                probe_video(self.source)


@unittest.skipUnless(FFMPEG and FFPROBE, "真实集成测试需要 ffmpeg 和 ffprobe")
class RealVideoTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        directory = tempfile.TemporaryDirectory()
        cls.addClassCleanup(directory.cleanup)
        cls.root = Path(directory.name)
        cls.clips = cls.root / "clips"
        cls.clips.mkdir()
        cls.first = cls.clips / "clip2 红色's.mp4"
        cls.second = cls.clips / "clip10 蓝色;$(echo unsafe).MP4"
        cls.different = cls.root / "different.mp4"
        for path, color, size in (
            (cls.first, "red", "64x48"),
            (cls.second, "blue", "64x48"),
            (cls.different, "green", "96x48"),
        ):
            subprocess.run(
                [
                    FFMPEG,
                    "-nostdin",
                    "-hide_banner",
                    "-loglevel",
                    "error",
                    "-n",
                    "-f",
                    "lavfi",
                    "-i",
                    f"color=c={color}:s={size}:r=10:d=0.4",
                    "-f",
                    "lavfi",
                    "-i",
                    "sine=frequency=440:sample_rate=48000:duration=0.4",
                    "-c:v",
                    "libx264",
                    "-preset",
                    "ultrafast",
                    "-pix_fmt",
                    "yuv420p",
                    "-c:a",
                    "aac",
                    "-shortest",
                    str(path),
                ],
                check=True,
                capture_output=True,
                timeout=30,
            )

    def pixels(self, path, time):
        result = subprocess.run(
            [
                FFMPEG,
                "-nostdin",
                "-loglevel",
                "error",
                "-ss",
                str(time),
                "-i",
                str(path),
                "-frames:v",
                "1",
                "-f",
                "rawvideo",
                "-pix_fmt",
                "rgb24",
                "pipe:1",
            ],
            check=True,
            capture_output=True,
            timeout=30,
        )
        self.assertGreater(len(result.stdout), 3)
        return tuple(result.stdout[:3])

    def options(self):
        return {"ffmpeg": FFMPEG, "ffprobe": FFPROBE, "timeout": 30}

    def test_merges_real_video_audio_and_preserves_order_and_inputs(self):
        original = [
            hashlib.sha256(path.read_bytes()).hexdigest()
            for path in (self.first, self.second)
        ]
        output = self.root / "真实合并.mp4"
        result = merge_videos([self.first, self.second], output, **self.options())
        self.assertEqual(result, output.resolve())
        metadata = probe_video(result, ffprobe=FFPROBE)
        self.assertEqual(
            [stream["codec_type"] for stream in metadata["streams"]], ["video", "audio"]
        )
        self.assertEqual(int(metadata["streams"][0]["nb_frames"]), 8)
        self.assertAlmostEqual(float(metadata["format"]["duration"]), 0.8, delta=0.15)
        early, late = self.pixels(result, 0.1), self.pixels(result, 0.6)
        self.assertGreater(early[0], 200)
        self.assertLess(early[2], 40)
        self.assertGreater(late[2], 200)
        self.assertLess(late[0], 40)
        audio = subprocess.run(
            [
                FFMPEG,
                "-nostdin",
                "-loglevel",
                "error",
                "-i",
                str(result),
                "-map",
                "0:a:0",
                "-f",
                "s16le",
                "-ac",
                "1",
                "pipe:1",
            ],
            check=True,
            capture_output=True,
            timeout=30,
        )
        self.assertFalse(audio.stderr)
        self.assertGreater(len(audio.stdout), 60000)
        self.assertEqual(
            original,
            [
                hashlib.sha256(path.read_bytes()).hexdigest()
                for path in (self.first, self.second)
            ],
        )
        self.assertEqual(list(self.root.glob(".video-merge-*")), [])

    def test_directory_natural_order_uppercase_extension_and_output_exclusion(self):
        output = self.clips / "output.mp4"
        output.write_bytes(b"old output")
        merge_directory(self.clips, output, overwrite=True, **self.options())
        early, late = self.pixels(output, 0.1), self.pixels(output, 0.6)
        self.assertGreater(early[0], 200)
        self.assertGreater(late[2], 200)

    def test_incompatible_streams_are_rejected_without_creating_output(self):
        output = self.root / "incompatible.mp4"
        with self.assertRaisesRegex(ValueError, "参数不一致"):
            merge_videos([self.first, self.different], output, **self.options())
        self.assertFalse(output.exists())

    def test_ffmpeg_failure_preserves_existing_output_and_unrelated_ts(self):
        output = self.root / "failed.unknown_format"
        output.write_bytes(b"old result")
        unrelated = self.root / "unrelated.ts"
        unrelated.write_bytes(b"keep me")
        with self.assertRaises(subprocess.CalledProcessError) as caught:
            merge_videos(
                [self.first, self.second], output, overwrite=True, **self.options()
            )
        self.assertTrue(caught.exception.stderr)
        self.assertEqual(output.read_bytes(), b"old result")
        self.assertEqual(unrelated.read_bytes(), b"keep me")
        self.assertEqual(list(self.root.glob(".video-merge-*")), [])

    def test_duplicate_input_is_an_explicit_repeat_not_an_error(self):
        output = self.root / "repeat.mp4"
        merge_videos([self.first, self.first], output, **self.options())
        metadata = probe_video(output, ffprobe=FFPROBE)
        self.assertEqual(int(metadata["streams"][0]["nb_frames"]), 8)


if __name__ == "__main__":
    unittest.main()
