import 'dart:io';
import 'dart:typed_data';

import 'package:common_dart/tts.dart';
import 'package:dotenv/dotenv.dart';
import 'package:test/test.dart';

void main() {
  final env = DotEnv(includePlatformEnvironment: true)..load(['.env']);
  final String? key = env['AZURE_TTS_KEY'];
  final String? region = env['AZURE_TTS_REGION'];

  final String? skipReason =
      (key == null || key.isEmpty || region == null || region.isEmpty)
      ? '需要 .env 或环境变量中的 AZURE_TTS_KEY 与 AZURE_TTS_REGION 才能运行 Azure TTS 集成测试'
      : null;

  group('TtsMicrosoft', () {
    late TtsMicrosoft client;

    setUp(() {
      client = TtsMicrosoft(
        key: key!,
        locationRegion: region!,
        // 使用中文语音进行测试，可按需调整。
        language: LanguageType.zh,
      );
    });

    tearDown(() {
      client.close();
    });

    test('fetchAccessToken 返回 token 字符串', () async {
      final token = await client.fetchAccessToken();
      expect(token, isA<String>());
      expect(token.length, greaterThan(50));
    });

    test('generateXmlData 返回 SSML 字符串', () {
      final xml = client.generateXmlData('hello world');
      expect(xml, isA<String>());
      expect(xml.contains('<speak'), isTrue);
      expect(xml.contains('</speak>'), isTrue);
    });

    test('convertTextToSpeech 返回音频字节并写入文件', () async {
      final bytes = await client.convertTextToSpeech('你好，世界');
      expect(bytes, isA<Uint8List>());
      expect(bytes.isNotEmpty, isTrue);

      final file = File('test/src/azure_cloud/test_zh.wav');
      await file.writeAsBytes(bytes, flush: true);
    });
  }, skip: skipReason);
}
