import 'dart:io';

abstract class ParseSubtitle {
  // 子类实现解析方法
  Future<SubtitleRes> parse();

  // 用于从文件中读取内容
  Future<Map<String, dynamic>> readContent(String filePath) async {
    try {
      // 使用 File 类来打开文件
      final file = File(filePath);

      // check file exists
      bool doesExist = await file.exists();

      if (!doesExist) {
        String msg = "文件不存在: $filePath";
        return {"success": false, "content": msg};
      }

      // 读取文件内容为字符串
      String content = await file.readAsString();

      return {"success": true, "content": content};
    } catch (e) {
      // 打印错误信息
      print('读取文件失败: $e');
      return {"success": false, "content": "读取文件失败"};
    }
  }
}

// 每个字幕解析的item
class SubtitleResItem {
  // 每个字幕块的索引
  int index;

  // 每个字幕块的开始时间
  String startTime;
  late double startTimeSeconds;

  // 每个字幕块的结束时间
  String endTime;
  late double endTimeSeconds;

  // 每个字幕块的内容，可能有多个
  List<String> content;

  SubtitleResItem(this.index, this.startTime, this.endTime, this.content) {
    // 解析时间戳字符串到秒
    startTimeSeconds = timestampToSeconds(startTime);
    endTimeSeconds = timestampToSeconds(endTime);
  }

  // 将字幕时间转为毫秒.
  // timestamp:  00:00:05,120
  double timestampToSeconds(String timestamp) {
    var parts = timestamp.split(','); // 分割秒和毫秒
    var timeParts = parts[0].split(':'); // 分割小时、分钟和秒

    // 解析小时、分钟、秒和毫秒
    int hours = int.parse(timeParts[0]);
    int minutes = int.parse(timeParts[1]);
    int seconds = int.parse(timeParts[2]);
    int milliseconds = parts.length > 1 ? int.parse(parts[1]) : 0;

    // 计算总秒数
    double totalSeconds =
        hours * 3600 + minutes * 60 + seconds + milliseconds / 1000.0;
    return totalSeconds;
  }

  @override
  String toString() {
    return "SubtitleResItem{index: $index, startTime: $startTime,startTimeSeconds: $startTimeSeconds, endTime: $endTime,endTimeSeconds: $endTimeSeconds, content: $content}";
  }
}

// 字幕解析结果类型
class SubtitleRes {
  // 是否解析成功
  bool success;
  String msg;
  // 解析后的内容
  List<SubtitleResItem> content;

  SubtitleRes(
    this.content, {
    this.success = true,
    this.msg = "ok",
  });

  @override
  String toString() {
    return "SubtitleRes{success: $success, msg: $msg, content: $content}";
  }
}
