import 'dart:convert';
import 'dart:io';
import 'dart:typed_data';
import 'dart:math';

import 'package:common_dart/translate.dart';
import 'package:common_dart/tts.dart';
import 'package:dio/dio.dart';

const Map<String, (String, String)> _posTagTable = {
  'ADJ': ('Adjectives', '形容词'),
  'ADV': ('Adverbs', '副词'),
  'CONJ': ('Conjunctions', '连词'),
  'DET': ('Determiners', '限定词'),
  'MODAL': ('Verbs', '动词'),
  'NOUN': ('Nouns', '名词'),
  'PREP': ('Prepositions', '介词'),
  'PRON': ('Pronouns', '代词'),
  'VERB': ('Verbs', '动词'),
  'OTHER': ('Other', '其他'),
};

/// 微软翻译实现。
class TranslateMicrosoft {
  TranslateMicrosoft({
    required this.textEndpoint,
    required this.wordEndpoint,
    required this.wordSamplesEndpoint,
    required this.locationRegion,
    required this.key,
    required this.ttsMicrosoft,
    Map<String, String>? partParams,
    Dio? dio,
  })  : partParams = partParams ?? const {},
        _dio = dio ?? Dio();

  final String textEndpoint;
  final String wordEndpoint;
  final String wordSamplesEndpoint;
  final String locationRegion;
  final String key;
  final Map<String, String> partParams;
  final TtsMicrosoft ttsMicrosoft;

  final Dio _dio;

  /// 翻译单词（词典接口），并补充发音与例句。
  Future<Map<String, dynamic>> translateWord(
    String word, {
    required LanguageCodeOfBackend sourceLanguageCode,
    required LanguageCodeOfBackend targetLanguageCode,
  }) async {
    final rawResponse = await _sendWordRequest(
      word,
      sourceLanguageCode,
      targetLanguageCode,
    );
    final normalizedWord = rawResponse['normalizedSource'] as String;

    final wordAudio = await _sendTtsRequest(normalizedWord);
    rawResponse['audio_data'] = wordAudio;

    final newTranslations = await _getWordTranslationAllExamples(
      rawResponse,
      sourceLanguageCode,
      targetLanguageCode,
    );
    rawResponse['translations'] = newTranslations;

    return rawResponse;
  }

  /// 翻译句子（文本翻译接口），并补充发音。
  Future<Map<String, dynamic>> translateSentence(
    String text, {
    required LanguageCodeOfBackend sourceLanguageCode,
    required LanguageCodeOfBackend targetLanguageCode,
  }) async {
    final rawResult = await _sendSentenceRequest(
      text,
      sourceLanguageCode,
      targetLanguageCode,
    );

    final textAudio = await _sendTtsRequest(text);
    rawResult['audio_data'] = textAudio;
    rawResult['sentence'] = text;

    return rawResult;
  }

  /// 将补充处理后的词典结果转换为 WordInfo。
  static WordInfo formatWordResponse(Map<String, dynamic> response) {
    final normalizedWord = response['normalizedSource'] as String;
    final displayWord = response['displaySource'] as String;

    final rawTranslations =
        (response['translations'] as List).cast<Map<String, dynamic>>();

    final translations = <WordTranslation>[];
    final rawShapes = <Map<String, dynamic>>[];

    for (final rawTranslation in rawTranslations) {
      translations.add(
        WordTranslation(
          normalized: rawTranslation['normalizedTarget'] as String,
          display: rawTranslation['displayTarget'] as String,
          posTag: _changePosTag(rawTranslation['posTag'] as String),
          frequency: _changeFrequency(
            (rawTranslation['confidence'] as num).toDouble(),
          ),
          examples: (rawTranslation['examples'] as List?)
                  ?.cast<Map<String, dynamic>>() ??
              const [],
        ),
      );

      final backTranslations =
          (rawTranslation['backTranslations'] as List?)?.cast<Map<String, dynamic>>() ??
              const [];
      rawShapes.addAll(backTranslations);
    }

    final sortedShapes = _sortShapes(rawShapes);
    final audio = response['audio_data'];
    final audioData = audio is Uint8List
        ? audio
        : audio is List<int>
            ? Uint8List.fromList(audio)
            : Uint8List(0);

    return WordInfo(
      normalizedWord: normalizedWord,
      displayWord: displayWord,
      translations: translations,
      shapes: sortedShapes,
      audioData: audioData,
      extendedInfo: const {},
    );
  }

  /// 将补充处理后的句子翻译结果转换为 SentenceInfo。
  static SentenceInfo formatSentenceResponse(Map<String, dynamic> response) {
    final sentence = response['sentence'] as String;
    final translation = [response['text'] as String];
    final audio = response['audio_data'];
    final audioData = audio is Uint8List
        ? audio
        : audio is List<int>
            ? Uint8List.fromList(audio)
            : Uint8List(0);

    return SentenceInfo(
      sentence: sentence,
      translations: translation,
      audioData: audioData,
    );
  }

  // ############################ [私有方法] 发送 word 请求 ############################
  Future<Map<String, dynamic>> _sendWordRequest(
    String word,
    LanguageCodeOfBackend sourceLanguageCode,
    LanguageCodeOfBackend targetLanguageCode,
  ) async {
    final source = _changeLanguageCode(sourceLanguageCode);
    final target = _changeLanguageCode(targetLanguageCode);

    final params = {
      ...partParams,
      'from': source,
      'to': target,
    };

    final accessToken = await ttsMicrosoft.fetchAccessToken();

    final headers = {
      'Authorization': 'Bearer $accessToken',
      'Ocp-Apim-Subscription-Key': key,
      'Ocp-Apim-Subscription-Region': locationRegion,
      'Content-type': 'application/json',
      'X-ClientTraceId': const Uuid().v4(),
    };

    final body = [
      {'Text': word}
    ];

    late Response response;
    try {
      response = await _dio.post<Object?>(
        wordEndpoint,
        queryParameters: params,
        data: jsonEncode(body),
        options: Options(headers: headers),
      );
    } catch (e) {
      throw HttpException(
        'microsoft 词典翻译请求连接失败: $wordEndpoint $params $headers $body; error: $e',
        uri: Uri.parse(wordEndpoint),
      );
    }

    if (response.statusCode != 200) {
      throw HttpException(
        'microsoft 词典翻译响应状态: ${response.statusCode}; 响应具体错误: ${response.data}; 请求参数: $headers $body; 实际请求url: ${response.realUri}',
        uri: Uri.parse(wordEndpoint),
      );
    }

    final data = response.data;
    if (data is! List || data.length != 1) {
      throw HttpException(
        'microsoft词典翻译响应格式错误: $data',
        uri: Uri.parse(wordEndpoint),
      );
    }

    final res = Map<String, dynamic>.from(data.first as Map);
    return res;
  }

  Future<List<Map<String, dynamic>>> _sendWordExamplesRequest(
    String normalizedWord,
    String normalizedTranslation,
    LanguageCodeOfBackend sourceLanguageCode,
    LanguageCodeOfBackend targetLanguageCode,
  ) async {
    final source = _changeLanguageCode(sourceLanguageCode);
    final target = _changeLanguageCode(targetLanguageCode);

    final params = {
      ...partParams,
      'from': source,
      'to': target,
    };

    final accessToken = await ttsMicrosoft.fetchAccessToken();

    final headers = {
      'Authorization': 'Bearer $accessToken',
      'Ocp-Apim-Subscription-Key': key,
      'Ocp-Apim-Subscription-Region': locationRegion,
      'Content-type': 'application/json',
      'X-ClientTraceId': const Uuid().v4(),
    };

    final body = [
      {'Text': normalizedWord, 'Translation': normalizedTranslation}
    ];

    late Response response;
    try {
      response = await _dio.post<Object?>(
        wordSamplesEndpoint,
        queryParameters: params,
        data: jsonEncode(body),
        options: Options(headers: headers),
      );
    } catch (e) {
      throw HttpException(
        'microsoft 词典示例请求连接失败: $wordSamplesEndpoint $params $headers $body; error: $e',
        uri: Uri.parse(wordSamplesEndpoint),
      );
    }

    if (response.statusCode != 200) {
      throw HttpException(
        'microsoft 词典示例响应状态: ${response.statusCode}; 响应具体错误: ${response.data}; 请求参数: $headers $body; 实际请求url: ${response.realUri}',
        uri: Uri.parse(wordSamplesEndpoint),
      );
    }

    final data = response.data;
    if (data is! List || data.length != 1) {
      throw HttpException(
        'microsoft词典翻译响应格式错误: $data',
        uri: Uri.parse(wordSamplesEndpoint),
      );
    }

    final sampleResponse = Map<String, dynamic>.from(data.first as Map);
    if (sampleResponse['normalizedSource'] != normalizedWord ||
        sampleResponse['normalizedTarget'] != normalizedTranslation) {
      throw HttpException(
        'microsoft词典示例响应格式错误: $sampleResponse',
        uri: Uri.parse(wordSamplesEndpoint),
      );
    }

    final examples =
        (sampleResponse['examples'] as List).cast<Map<String, dynamic>>();
    return examples;
  }

  List<Map<String, dynamic>> _uniqueWordExamples(
    List<Map<String, dynamic>> examplesInfo,
  ) {
    final Map<String, Map<String, dynamic>> finalResInfo = {};

    for (final exampleInfo in examplesInfo) {
      final tempSentence = StringBuffer()
        ..write(exampleInfo['sourcePrefix'] ?? '')
        ..write(exampleInfo['sourceTerm'] ?? '')
        ..write(exampleInfo['sourceSuffix'] ?? '');

      final currentTarget = {
        'targetPrefix': exampleInfo['targetPrefix'],
        'targetTerm': exampleInfo['targetTerm'],
        'targetSuffix': exampleInfo['targetSuffix'],
      };

      final key = tempSentence.toString();
      if (!finalResInfo.containsKey(key)) {
        finalResInfo[key] = {
          'sourcePrefix': exampleInfo['sourcePrefix'],
          'sourceTerm': exampleInfo['sourceTerm'],
          'sourceSuffix': exampleInfo['sourceSuffix'],
          'target': [currentTarget],
        };
      } else {
        final targets = finalResInfo[key]!['target'] as List<dynamic>;
        targets.add(currentTarget);
      }
    }

    return finalResInfo.values
        .map((value) => Map<String, dynamic>.from(value))
        .toList();
  }

  Future<List<Map<String, dynamic>>> _getWordTranslationAllExamples(
    Map<String, dynamic> rawResponse,
    LanguageCodeOfBackend sourceLanguageCode,
    LanguageCodeOfBackend targetLanguageCode,
  ) async {
    final normalizedWord = rawResponse['normalizedSource'] as String;
    final translationsInfo =
        (rawResponse['translations'] as List).cast<Map<String, dynamic>>();
    final finalTranslationsInfo = <Map<String, dynamic>>[];

    for (final translationInfo in translationsInfo) {
      final normalizedTranslation = translationInfo['normalizedTarget'] as String;
      final rawSamples = await _sendWordExamplesRequest(
        normalizedWord,
        normalizedTranslation,
        sourceLanguageCode,
        targetLanguageCode,
      );
      final translationSamples = _uniqueWordExamples(rawSamples);
      translationInfo['examples'] = translationSamples;
      finalTranslationsInfo.add(translationInfo);
    }

    return finalTranslationsInfo;
  }

  // ############################ [私有方法] 发送 sentence 请求 ############################
  Future<Map<String, dynamic>> _sendSentenceRequest(
    String text,
    LanguageCodeOfBackend sourceLanguageCode,
    LanguageCodeOfBackend targetLanguageCode,
  ) async {
    final source = _changeLanguageCode(sourceLanguageCode);
    final target = _changeLanguageCode(targetLanguageCode);

    final params = {
      ...partParams,
      'from': source,
      'to': target,
    };

    final headers = {
      'Ocp-Apim-Subscription-Key': key,
      'Ocp-Apim-Subscription-Region': locationRegion,
      'Content-type': 'application/json',
      'X-ClientTraceId': const Uuid().v4(),
    };

    final body = [
      {'text': text}
    ];

    late Response response;
    try {
      response = await _dio.post<Object?>(
        textEndpoint,
        queryParameters: params,
        data: jsonEncode(body),
        options: Options(headers: headers),
      );
    } catch (e) {
      throw HttpException(
        'microsoft 翻译请求连接失败: $textEndpoint $params $headers $body; error: $e',
        uri: Uri.parse(textEndpoint),
      );
    }

    if (response.statusCode != 200) {
      throw HttpException(
        'microsoft 翻译响应状态: ${response.statusCode}; 响应具体错误: ${response.data}; 实际请求url: ${response.realUri}; 请求参数: $headers $body',
        uri: Uri.parse(textEndpoint),
      );
    }

    final data = response.data;
    if (data is! List || data.length != 1) {
      throw HttpException(
        'microsoft翻译响应格式错误1: $data',
        uri: Uri.parse(textEndpoint),
      );
    }

    final responseDict = Map<String, dynamic>.from(data.first as Map);
    if (!responseDict.containsKey('translations')) {
      throw HttpException(
        'microsoft翻译响应格式错误2: $responseDict',
        uri: Uri.parse(textEndpoint),
      );
    }

    final translations =
        (responseDict['translations'] as List).cast<Map<String, dynamic>>();
    if (translations.length != 1) {
      throw HttpException(
        'microsoft翻译响应格式错误3: $translations',
        uri: Uri.parse(textEndpoint),
      );
    }

    final res = Map<String, dynamic>.from(translations.first);
    return res;
  }

  Future<Uint8List> _sendTtsRequest(String text) async {
    final wavData = await ttsMicrosoft.convertTextToSpeech(text);
    return wavData;
  }
}

// ############################ [静态方法] ############################
String _changeLanguageCode(LanguageCodeOfBackend language) {
  switch (language) {
    case LanguageCodeOfBackend.zhCn:
      return 'zh-Hans';
    case LanguageCodeOfBackend.zhTw:
      return 'zh-Hant';
    case LanguageCodeOfBackend.en:
    case LanguageCodeOfBackend.ja:
      return language.code;
    default:
      throw ArgumentError('microsoft不支持的语言代码: ${language.code}');
  }
}

(String, String) _changePosTag(String posTag) {
  final mapped = _posTagTable[posTag];
  if (mapped == null) {
    throw ArgumentError('microsoft不支持的词性标签: $posTag');
  }
  return mapped;
}

double _changeFrequency(double frequency) =>
    double.parse((frequency * 100).toStringAsFixed(1));

List<Map<String, dynamic>> _sortShapes(List<Map<String, dynamic>> rawShapes) {
  final shapes = List<Map<String, dynamic>>.from(rawShapes);
  shapes.sort(
    (a, b) => ((b['frequencyCount'] as num?) ?? 0)
        .compareTo((a['frequencyCount'] as num?) ?? 0),
  );
  return shapes;
}

/// 简单 UUID 生成，避免额外依赖。
class Uuid {
  const Uuid();

  String v4() {
    final random = Random.secure();
    final bytes = List<int>.generate(16, (_) => random.nextInt(256));
    // Variant and version bits.
    bytes[6] = (bytes[6] & 0x0f) | 0x40;
    bytes[8] = (bytes[8] & 0x3f) | 0x80;

    final hex = bytes.map((b) => b.toRadixString(16).padLeft(2, '0')).join();
    return '${hex.substring(0, 8)}-'
        '${hex.substring(8, 12)}-'
        '${hex.substring(12, 16)}-'
        '${hex.substring(16, 20)}-'
        '${hex.substring(20, 32)}';
  }
}
