class ParseSrtFile:
    def __init__(self, file_name: str):
        self.file_name = file_name
        with open(self.file_name) as f:
            content = f.readlines()
            self.content: list = self.clean_non_text_lines(content)

    def clean_non_text_lines(self, file_content: list) -> list:
        """清理控制字符和空行"""
        # 清理\n控制字符
        file_content = list(map(lambda line: line.strip("\n"), file_content))
        # 清理空行
        file_content = list(filter(lambda line: line != "", file_content))
        return file_content

    def get_all_timer_shaft(self) -> list[tuple[str, str]]:
        """获取所有时间轴
        [
            (start_time,end_time)
        ]
        """
        # `:` 和 `-->` 同时存在的行就是时间轴所在的行
        time_shaft_content: list = list(
            filter(lambda line: ":" in line and "-->" in line, self.content)
        )

        # 将时间轴数据拆分为
        def _clean(time_str: str):
            return tuple(map(lambda x: x.strip(" "), time_str.split("-->")))

        time_shaft_data: list = list(
            map(
                lambda time_str_line: _clean(time_str_line),
                time_shaft_content,
            )
        )
        import json

        print(json.dumps(time_shaft_data, indent=2, ensure_ascii=False))
        return time_shaft_data


# p = ParseSrtFile("test.srt")
# p.get_all_timer_shaft()
import logging
import os


def split(time_range, video_name):
    """单线程阻塞切割"""
    for index, time in enumerate(time_range):
        # cmd = f"ffmpeg -i 输入视频.mp4 -ss 00:02:10 -to 00:03:20 -c:v copy -c:a copy 输出视频.mp4"
        cmd = f"ffmpeg -i {video_name} -ss {time[0]} -to {time[1]} -c:v copy -c:a copy {index}.mp4"
        try:
            os.system(cmd)
        except Exception as e:
            logging.error(f"出错: {cmd} {e}")
        else:
            logging.debug(f"cmd: {cmd}")
            logging.info(f"{time}处理成功")
