"""合并本地视频，不拼接 Shell 命令、不修改源文件或全局日志。"""

from __future__ import annotations

import errno
import json
import math
import os
import re
import shutil
import subprocess
import tempfile
from collections.abc import Iterable
from pathlib import Path
from typing import Any


def _timeout(value: float | None) -> None:
    if value is not None and (
        isinstance(value, bool)
        or not isinstance(value, (int, float))
        or not math.isfinite(value)
        or value <= 0
    ):
        raise ValueError("timeout 必须为有限的正数或 None")


def _binary(name: str | Path) -> str:
    executable = shutil.which(os.fspath(name))
    if executable is None:
        raise FileNotFoundError(f"未找到可执行文件 {name}，请安装 FFmpeg 或传入完整路径")
    return executable


def _input_file(path: str | Path) -> Path:
    source = Path(path).expanduser().resolve(strict=True)
    if not source.is_file():
        raise ValueError(f"输入不是普通文件：{source}")
    return source


def _run(command: list[str], timeout: float | None):
    result = subprocess.run(
        command,
        stdin=subprocess.DEVNULL,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=True,
        timeout=timeout,
    )
    # 命令均使用 error 日志级别；有些读取错误会记录日志但仍返回 0。
    if result.stderr.strip():
        raise RuntimeError(f"FFmpeg 工具报告错误：{result.stderr.strip()}")
    return result


def _probe(path: Path, binary: str, timeout: float | None) -> dict[str, Any]:
    result = _run(
        [
            binary,
            "-v",
            "error",
            "-show_streams",
            "-show_format",
            "-of",
            "json",
            str(path),
        ],
        timeout,
    )
    metadata = json.loads(result.stdout)
    streams = metadata.get("streams") if isinstance(metadata, dict) else None
    if not isinstance(streams, list) or not all(
        isinstance(stream, dict) for stream in streams
    ):
        raise ValueError(f"ffprobe 响应缺少有效 streams：{path}")
    if not any(stream.get("codec_type") == "video" for stream in streams):
        raise ValueError(f"文件不包含视频流：{path}")
    return metadata


def probe_video(
    path: str | Path,
    *,
    ffprobe: str | Path = "ffprobe",
    timeout: float | None = 30,
) -> dict[str, Any]:
    """返回 ffprobe 完整 JSON；缺少工具、无视频流及执行失败均抛出异常。"""
    _timeout(timeout)
    return _probe(_input_file(path), _binary(ffprobe), timeout)


def _stream_signature(stream: dict[str, Any]) -> tuple:
    fields = ["codec_type", "codec_name", "time_base"]
    if stream.get("codec_type") == "video":
        fields += [
            "profile",
            "width",
            "height",
            "pix_fmt",
            "r_frame_rate",
            "sample_aspect_ratio",
            "field_order",
        ]
    elif stream.get("codec_type") == "audio":
        fields += ["sample_fmt", "sample_rate", "channels", "channel_layout"]
    return tuple(stream.get(field) for field in fields)


def _publish(staged: Path, output: Path, overwrite: bool) -> None:
    if overwrite:
        staged.replace(output)
        return
    try:
        # 同一文件系统上独占创建最终路径，避免覆盖并发产生的文件。
        os.link(staged, output)
        return
    except OSError as exc:
        if exc.errno not in {errno.EPERM, errno.ENOTSUP, errno.EXDEV}:
            raise
    # 不支持硬链接的文件系统使用独占复制，失败时清理本次新建的输出。
    created = False
    try:
        with output.open("xb") as destination:
            created = True
            with staged.open("rb") as source:
                shutil.copyfileobj(source, destination)
    except BaseException:
        if created:
            output.unlink(missing_ok=True)
        raise


def merge_videos(
    inputs: Iterable[str | Path],
    output_path: str | Path,
    *,
    overwrite: bool = False,
    ffmpeg: str | Path = "ffmpeg",
    ffprobe: str | Path = "ffprobe",
    timeout: float | None = None,
) -> Path:
    """按输入顺序无重编码合并，返回最终输出的绝对路径。

    检查流数量/顺序、编码、时间基、分辨率、帧率及音频参数，不自动转码。
    输出父目录必须已存在；默认不覆盖，输出不能是任何输入的别名。
    先在输出父目录的独立临时目录中生成并探测结果，再提交到目标路径。
    timeout 对每个子进程分别生效。CalledProcessError.stderr 保留 FFmpeg 错误。
    """
    _timeout(timeout)
    if not isinstance(overwrite, bool):
        raise TypeError("overwrite 必须为布尔值")
    if isinstance(inputs, (str, Path)):
        raise TypeError("inputs 必须为路径的可迭代对象，例如 [first, second]")
    sources = [_input_file(path) for path in inputs]
    if not sources:
        raise ValueError("至少需要一个输入视频")
    for source in sources:
        if "\n" in str(source) or "\r" in str(source):
            raise ValueError("视频路径不能包含换行符")
    output = Path(output_path).expanduser().resolve()
    if not output.suffix:
        raise ValueError("输出路径需要扩展名，以指定封装格式")
    if not output.parent.is_dir():
        raise FileNotFoundError(f"输出父目录不存在：{output.parent}")
    if any(
        source == output or (output.exists() and source.samefile(output))
        for source in sources
    ):
        raise ValueError("输出路径不能是输入文件或其别名")
    if output.exists():
        if not output.is_file():
            raise ValueError("输出路径不是普通文件")
        if not overwrite:
            raise FileExistsError(output)
    ffmpeg_binary = _binary(ffmpeg)
    ffprobe_binary = _binary(ffprobe)
    first_info = _probe(sources[0], ffprobe_binary, timeout)
    signature = [_stream_signature(stream) for stream in first_info["streams"]]
    for source in sources[1:]:
        info = _probe(source, ffprobe_binary, timeout)
        if [_stream_signature(stream) for stream in info["streams"]] != signature:
            raise ValueError(f"音视频流参数不一致，不能直接合并：{source}")

    with tempfile.TemporaryDirectory(
        prefix=".video-merge-", dir=output.parent
    ) as folder:
        workspace = Path(folder)
        manifest = workspace / "inputs.ffconcat"
        lines = ["ffconcat version 1.0"]
        for source in sources:
            escaped = source.as_posix().replace("'", "'\\''")
            lines.append(f"file '{escaped}'")
        manifest.write_text("\n".join(lines) + "\n", encoding="utf-8")
        staged = workspace / ("merged" + output.suffix)
        _run(
            [
                ffmpeg_binary,
                "-nostdin",
                "-hide_banner",
                "-loglevel",
                "error",
                "-n",
                "-f",
                "concat",
                "-safe",
                "0",
                "-i",
                str(manifest),
                "-map",
                "0",
                "-c",
                "copy",
                str(staged),
            ],
            timeout,
        )
        if not staged.is_file() or not staged.stat().st_size:
            raise RuntimeError("FFmpeg 未生成有效输出文件")
        merged = _probe(staged, ffprobe_binary, timeout)

        def codecs(info):
            return [
                (stream.get("codec_type"), stream.get("codec_name"))
                for stream in info["streams"]
            ]

        if codecs(merged) != codecs(first_info):
            raise RuntimeError("合并输出的音视频流与输入不一致")
        _publish(staged, output, overwrite)
    return output


def merge_directory(
    input_directory: str | Path,
    output_path: str | Path,
    *,
    extensions: Iterable[str] = (".mp4",),
    **options,
) -> Path:
    """合并目录首层的视频，按自然文件名排序，排除已有目标文件。

    默认选择 .mp4（不区分扩展名大小写）；例如 clip2.mp4 排在 clip10.mp4 前。
    可用 extensions 选择其他封装格式，options 同 merge_videos。
    """
    directory = Path(input_directory).expanduser().resolve(strict=True)
    if not directory.is_dir():
        raise NotADirectoryError(directory)
    if isinstance(extensions, str):
        raise TypeError("extensions 必须为扩展名的可迭代对象")
    suffixes = set()
    for suffix in extensions:
        if not isinstance(suffix, str) or not suffix.lstrip("."):
            raise ValueError("扩展名不能为空")
        suffixes.add("." + suffix.lstrip(".").lower())
    if not suffixes:
        raise ValueError("extensions 不能为空")
    output = Path(output_path).expanduser().resolve()
    sources = [
        path
        for path in directory.iterdir()
        if path.is_file()
        and path.suffix.lower() in suffixes
        and path.resolve() != output
    ]

    def natural_key(path):
        parts = tuple(
            int(part) if part.isdigit() else part
            for part in re.split(r"(\d+)", path.name.casefold())
        )
        return parts, path.name.casefold(), path.name

    return merge_videos(sorted(sources, key=natural_key), output, **options)
