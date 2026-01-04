import 'dart:typed_data';

import 'package:common_dart/src/azure_cloud/translate.dart';
import 'package:common_dart/src/azure_cloud/tts.dart';
import 'package:common_dart/translate.dart';
import 'package:dotenv/dotenv.dart';
import 'package:test/test.dart';

void main() {
  const word = 'fly';
  const text =
      'I would really like to drive your car around the block several times!';
  const sourceLanguage = LanguageCodeOfBackend.en;
  const targetLanguage = LanguageCodeOfBackend.zhCn;

  // 读取 .env 与环境变量。
  final env = DotEnv(includePlatformEnvironment: true)..load(['.env']);
  final translatorKey = env['AZURE_TRANSLATOR_KEY'];
  final translatorRegion = env['AZURE_TRANSLATOR_REGION'];
  final ttsKey = env['AZURE_TTS_KEY'];
  final ttsRegion = env['AZURE_TTS_REGION'];
  final textEndpoint =
      env['AZURE_TRANSLATOR_TEXT_ENDPOINT'] ??
      'https://api.cognitive.microsofttranslator.com/translate';
  final wordEndpoint =
      env['AZURE_TRANSLATOR_WORD_ENDPOINT'] ??
      'https://api.cognitive.microsofttranslator.com/dictionary/lookup';
  final wordSamplesEndpoint =
      env['AZURE_TRANSLATOR_WORD_SAMPLES_ENDPOINT'] ??
      'https://api.cognitive.microsofttranslator.com/dictionary/examples';

  final String? skipLiveReason =
      (translatorKey == null ||
          translatorKey.isEmpty ||
          translatorRegion == null ||
          translatorRegion.isEmpty ||
          ttsKey == null ||
          ttsKey.isEmpty ||
          ttsRegion == null ||
          ttsRegion.isEmpty)
      ? '需要翻译(AZURE_TRANSLATOR_KEY/REGION)与语音(AZURE_TTS_KEY/REGION)两套凭证才能运行微软翻译与 TTS 集成测试'
      : null;

  TranslateMicrosoft createClient() => TranslateMicrosoft(
    textEndpoint: textEndpoint,
    wordEndpoint: wordEndpoint,
    wordSamplesEndpoint: wordSamplesEndpoint,
    locationRegion: translatorRegion ?? '',
    key: translatorKey ?? '',
    partParams: const {'api-version': '3.0'},
    ttsMicrosoft: TtsMicrosoft(
      key: ttsKey ?? '',
      locationRegion: ttsRegion ?? '',
      language: LanguageType.en,
    ),
  );

  group('TranslateMicrosoft 集成', () {
    late TranslateMicrosoft client;

    setUp(() {
      client = createClient();
    });

    tearDown(() {
      client.ttsMicrosoft.close();
    });

    test('translateWord 返回包含音频的词典结果', () async {
      final resTran = await client.translateWord(
        word,
        sourceLanguageCode: sourceLanguage,
        targetLanguageCode: targetLanguage,
      );

      expect(resTran, isA<Map<String, dynamic>>());
      expect(resTran.containsKey('normalizedSource'), isTrue);
      expect(resTran.containsKey('displaySource'), isTrue);
      expect(resTran.containsKey('audio_data'), isTrue);
      expect(resTran['audio_data'], isA<Uint8List>());
      expect(resTran.containsKey('translations'), isTrue);
      expect(resTran['translations'], isA<List<dynamic>>());
    }, skip: skipLiveReason);

    test('translateSentence 返回包含音频的句子结果', () async {
      final resTran = await client.translateSentence(
        text,
        sourceLanguageCode: sourceLanguage,
        targetLanguageCode: targetLanguage,
      );

      expect(resTran, isA<Map<String, dynamic>>());
      expect(resTran.containsKey('text'), isTrue);
      expect(resTran.containsKey('to'), isTrue);
      expect(resTran.containsKey('audio_data'), isTrue);
      expect(resTran['audio_data'], isA<Uint8List>());
      expect(resTran['sentence'], equals(text));
    }, skip: skipLiveReason);
  });

  group('TranslateMicrosoft 格式化与工具方法', () {
    // 伪造 word 翻译结果，覆盖 posTag 映射、词频处理与形态排序。
    final fakeWordResponse = {
      'normalizedSource': 'fly',
      'displaySource': 'Fly',
      'translations': [
        {
          'normalizedTarget': '飞',
          'displayTarget': '飞',
          'posTag': 'VERB',
          'confidence': 0.2898,
          'examples': [
            {
              'sourcePrefix': 'Tomorrow we are going to ',
              'sourceTerm': 'fly',
              'sourceSuffix': ' home.',
              'target': [
                {
                  'targetPrefix': '明天我们将',
                  'targetTerm': '乘飞机',
                  'targetSuffix': '回家',
                },
              ],
            },
          ],
          'backTranslations': [
            {
              'normalizedText': 'fly',
              'displayText': 'fly',
              'numExamples': 15,
              'frequencyCount': 4995,
            },
            {
              'normalizedText': 'flew',
              'displayText': 'flew',
              'numExamples': 5,
              'frequencyCount': 968,
            },
          ],
        },
      ],
      'audio_data': Uint8List.fromList([0, 1, 2]),
    };

    final fakeSentenceResponse = {
      'sentence': text,
      'text': '我真的很想开着你的车绕着街区转好几圈！',
      'to': 'zh-Hans',
      'audio_data': Uint8List.fromList([3, 4, 5]),
    };

    test('formatWordResponse 返回 WordInfo 并正确映射字段', () {
      final res = TranslateMicrosoft.formatWordResponse(fakeWordResponse);

      expect(res, isA<WordInfo>());
      expect(res.normalizedWord, 'fly');
      expect(res.displayWord, 'Fly');
      expect(res.translations, isNotEmpty);

      final firstTranslation = res.translations.first;
      expect(firstTranslation.normalized, '飞');
      expect(firstTranslation.display, '飞');
      expect(firstTranslation.posTag, ('Verbs', '动词'));
      expect(firstTranslation.frequency, 29.0); // 0.2898 -> 29.0%
      expect(firstTranslation.examples, isNotEmpty);

      // backTranslations 排序后按频率从大到小。
      expect(res.shapes, isNotEmpty);
      final firstShape = res.shapes.first as Map<String, dynamic>;
      expect(firstShape['frequencyCount'], 4995);

      expect(res.audioData, isA<Uint8List>());
      expect(res.extendedInfo, isA<Map<String, dynamic>>());
    });

    test('formatSentenceResponse 返回 SentenceInfo 并附带音频', () {
      final res = TranslateMicrosoft.formatSentenceResponse(
        fakeSentenceResponse,
      );
      expect(res, isA<SentenceInfo>());
      expect(res.sentence, equals(text));
      expect(res.translations, equals(['我真的很想开着你的车绕着街区转好几圈！']));
      expect(res.audioData, isA<Uint8List>());
    });
  });
}
