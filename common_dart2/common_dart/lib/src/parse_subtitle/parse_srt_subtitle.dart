import 'subtitle.dart';

class ParseSrtSubtitle extends ParseSubtitle {
  // srt字幕文件内容
  String filePath;

  ParseSrtSubtitle(this.filePath);

  @override
  Future<SubtitleRes> parse() async {
    // 读取文件内容
    Map<String, dynamic> contentRes = await readContent(filePath);
    bool contentStatus = contentRes['success'];
    String content = contentRes['content'];

    List<SubtitleResItem> items = [];

    if (contentStatus) {
      // 开始解析
      List<String> lines = content.split('\n');

      int index = -1;
      String startTime = '';
      String endTime = '';
      List<String> resContent = [];

      for (String line in lines) {
        // Map item = {};
        String cleanLine = line.trim();

        if (cleanLine.isNotEmpty) {
          if (int.tryParse(cleanLine) != null) {
            // 设置行号
            index = int.parse(cleanLine);
            continue;
          }

          if (cleanLine.contains('-->')) {
            // 时间戳行
            List<String> times = cleanLine.split('-->');
            startTime = times[0].trim();
            endTime = times[1].trim();
            continue;
          }

          // 内容行
          if (cleanLine.endsWith('，')) {
            // 如果末尾含有逗号，获取从字符串开始到去掉最后一个字符前的所有字符。
            cleanLine = cleanLine.substring(0, cleanLine.length - 1);
          }
          resContent.add(cleanLine);
        } else {
          // 如果遇到空行，说明上面解析完成了
          // 添加数据
          SubtitleResItem item =
              SubtitleResItem(index, startTime, endTime, resContent);
          items.add(item);
          // 清空item
          index = 0;
          startTime = '';
          endTime = '';
          resContent = [];
        }
      }

      return SubtitleRes(items);
    } else {
      // 读取文件失败
      return SubtitleRes([], success: false, msg: content);
    }
  }
}

void main() async {
  ParseSrtSubtitle parseSrtSubtitle = ParseSrtSubtitle('aaa.srt');

  var data = await parseSrtSubtitle.parse();
  print(data);
}
