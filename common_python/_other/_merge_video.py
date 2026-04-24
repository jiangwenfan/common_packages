import os
import logging
import sys
import threading
from typing import Union, NoReturn

logging.basicConfig(level=logging.INFO)


class VideoMerge:
    video_format = ["mp4"]

    def __init__(self):
        # check
        self.check_base()

    def check_base(self) -> None:
        """检查基础"""
        if not os.path.exists("need_video"):
            os.mkdir("need_video")
        if not os.path.exists("result_video"):
            os.mkdir("result_video")
        if os.path.exists("need_video") and os.path.exists("result_video"):
            logging.info("检查通过")
        else:
            logging.critical("环境检查失败")
            sys.exit()
        # TODO 检查ffmpeg

    def check_video(self, files: list) -> bool | NoReturn:
        videos_format = [file.split(".")[-1] for file in files]
        videos_format2 = set(videos_format)
        # 视频统一性检查
        res = len(videos_format2)
        if res > 1:
            logging.critical("视频格式不统一")
        elif res == 1:
            logging.info("视频合法")
            return True
        else:
            logging.warning("没有视频")

        # 视频格式是否支持检查
        for format in videos_format2:
            if format not in self.video_format:
                logging.error(f"格式不支持{format}")
            else:
                return True
        sys.exit()

    def change_mp4_ts(self, video_name):
        name = video_name.split(".")[0]
        input_name = f"need_video/{video_name}"
        res_name = f"result_video/{name}.ts"
        cmd = f"ffmpeg -i {input_name} -vcodec copy -acodec copy -vbsf h264_mp4toannexb {res_name}"
        os.system(cmd)

    def merge_all_ts(self, all_ts: list):
        print(all_ts, type(all_ts), [type(ts) for ts in all_ts])
        ts_format = "|".join(all_ts)
        print(ts_format)
        cmd = f"""ffmpeg -i "concat:{ts_format}" -acodec copy -vcodec copy -absf aac_adtstoasc 'result_video/output.mp4'"""
        os.system(cmd)
        logging.info("合并成功")

    def clean_all_ts(self):
        files = os.listdir("result_video")
        all_ts = [file for file in files if file.split(".")[-1] == "ts"]
        logging.info(all_ts)
        for ts in all_ts:
            name = "result_video/" + ts
            os.remove(name)
        logging.info("clean")

    def change(self):
        all_thread = []

        # 读取文件
        files: list = os.listdir("need_video")

        # 检查视频
        self.check_video(files)

        # 多线程转化
        for file in files:
            # 转化为ts
            t = threading.Thread(target=self.change_mp4_ts, args=(file,))
            all_thread.append(t)
            t.start()
        for t in all_thread:
            t.join()
        logging.info("所有视频转化完成")

        # 合并视频
        all_ts = ["result_video/" + file.split(".")[0] + ".ts" for file in files]
        self.merge_all_ts(all_ts)

        # 清理ts视频
        self.clean_all_ts()


if __name__ == "__main__":
    v = VideoMerge()
    v.change()

# check env

# read video
# change ts video
# merge ts video to mp4
# clean ts video
