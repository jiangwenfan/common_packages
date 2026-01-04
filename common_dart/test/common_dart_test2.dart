import 'package:common_dart/common_dart.dart';
import 'package:test/test.dart';
import 'package:common_dart/src/parse_subtitle/parse_srt_subtitle.dart';
import 'package:common_dart/src/parse_subtitle/subtitle.dart';
import 'dart:io';

void main() {
  group('A group of tests', () {
    final awesome = Awesome();

    setUp(() {
      // Additional setup goes here.
    });

    test('First Test', () {
      expect(awesome.isAwesome, isTrue);
    });
  });

  // 测试解析srt字幕
  group("parse srt subtitle", () {
//     setUpAll(() async {
//       // 测试前，创建测试文件
//       // 创建一个新文件
//       String msg = '''
// 1
// 00:00:00,080 --> 00:00:01,439
// welcome to the course my name is john
// 欢迎来到本课程，我的名字是 john

// 2
// 00:00:01,439 --> 00:00:03,600
// elder i'm the founder of codyme.com and
// Elder，我是 codyme.com 的创始人，

// 3
// 00:00:03,600 --> 00:00:05,120
// in this free and complete course i'll
// 在这个免费且完整的课程中，我将

// 4
// 00:00:05,120 --> 00:00:06,879
// walk you step by step through the dark
// 逐步引导您了解黑暗的
// ''';
//       var file = File("test/srt_demo.srt");
//       await file.create();
//       await file.writeAsString(msg);
//     });
//     tearDownAll(() {
//       // 测试完，删除测试文件
//     });

    test("解析srt字幕_成功", () async {
      ParseSrtSubtitle parseSrtSubtitle =
          ParseSrtSubtitle('test/srt_subtitle_demo.srt');

      SubtitleRes res = await parseSrtSubtitle.parse();
      // 断言SubtitleRes类型处理成功
      print(res.msg);
      expect(res.success, true);
      expect(res.msg, "ok");
      List<SubtitleResItem> d = res.content;
      expect(d.length, 4);

      // 断言SubtitleResItem类型处理成功
      SubtitleResItem i = d[1];
      expect(i.index, 2);
      expect(i.content, [
        "elder i'm the founder of codyme.com and",
        "Elder，我是 codyme.com 的创始人"
      ]);
      expect(i.startTime, "00:00:01,439");
      expect(i.endTime, "00:00:03,600");
      expect(i.startTimeSeconds, 1.439);
      expect(i.endTimeSeconds, 3.6);
    });

    test("解析srt字幕_文件不存在", () async {
      ParseSrtSubtitle parseSrtSubtitle =
          ParseSrtSubtitle('test/srt_subtitle_demo2.srt');
      SubtitleRes res = await parseSrtSubtitle.parse();
      // 断言SubtitleRes类型处理失败
      expect(res.success, false);
      expect(res.msg, "文件不存在: test/srt_subtitle_demo2.srt");
      expect(res.content, []);
    });

    test("解析srt字幕_文件读取失败", () async {
      // 修改权限。让文件无法读取
      ParseSrtSubtitle parseSrtSubtitle =
          ParseSrtSubtitle('test/srt_subtitle_demo3.srt');
      SubtitleRes res = await parseSrtSubtitle.parse();
      // 断言SubtitleRes类型处理失败
      expect(res.success, false);
      expect(res.msg, "读取文件失败");
      expect(res.content, []);
      // 恢复权限
    });
  });
}
