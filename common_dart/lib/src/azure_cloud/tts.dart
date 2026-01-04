import 'dart:convert';
import 'dart:io';
import 'dart:typed_data';
import 'package:dio/dio.dart';

/// 支持的 Azure 语音类型。
enum LanguageType { en, zh }

class _AudioStyle {
  const _AudioStyle({required this.languageCode, required this.name});

  final String languageCode;
  final String name;
}

// 与 Python 版本一致的语音预设。
const Map<LanguageType, _AudioStyle> _audioStyles = {
  LanguageType.en: _AudioStyle(
    languageCode: 'en-US',
    name: 'en-US-AndrewMultilingualNeural',
  ),
  LanguageType.zh: _AudioStyle(
    languageCode: 'zh-CN',
    name: 'zh-CN-YunjianNeural',
  ),
};

/// Azure 文本转语音客户端，对应原 Python 工具。
///
/// 文档: https://learn.microsoft.com/azure/ai-services/speech-service/index-text-to-speech
class TtsMicrosoft {
  TtsMicrosoft({
    required this.key,
    required this.locationRegion,
    this.language = LanguageType.en,
    this.userAgent = 'language_backend',
    this.outputFormat = 'riff-24khz-16bit-mono-pcm',
    this.gender = 'Male',
    Dio? dio,
    BaseOptions? dioOptions,
  }) : accessTokenUrl =
           'https://${locationRegion}.api.cognitive.microsoft.com/sts/v1.0/issueToken',
       textToSpeechUrl =
           'https://${locationRegion}.tts.speech.microsoft.com/cognitiveservices/v1',
       _dio = dio ?? Dio(dioOptions) {
    final style = _audioStyles[language]!;
    languageCode = style.languageCode;
    voiceName = style.name;
  }

  final String key;
  final String locationRegion;
  final LanguageType language;
  final String userAgent;
  final String outputFormat;
  final String gender;
  final String accessTokenUrl;
  final String textToSpeechUrl;
  late final String languageCode;
  late final String voiceName;

  final Dio _dio;

  /// 获取短时有效的访问令牌，用于 TTS 请求。
  Future<String> fetchAccessToken() async {
    final response = await _dio.post<String>(
      accessTokenUrl,
      options: Options(
        headers: {'Ocp-Apim-Subscription-Key': key},
        responseType: ResponseType.plain,
      ),
    );

    final status = response.statusCode ?? 0;
    final body = response.data ?? '';
    if (status >= 200 && status < 300) {
      return body;
    }

    throw HttpException(
      'Failed to fetch access token (status $status): $body',
      uri: Uri.parse(accessTokenUrl),
    );
  }

  /// 根据文本构建 SSML 负载。
  String generateXmlData(String text) =>
      '''
<speak version='1.0' xml:lang='$languageCode'>
  <voice xml:lang='$languageCode' xml:gender='$gender' name='$voiceName'>
    $text
  </voice>
</speak>
'''
          .trim();

  /// 调用 Azure TTS 将文本转换为音频字节。
  Future<Uint8List> convertTextToSpeech(String text) async {
    final token = await fetchAccessToken();
    final ssml = generateXmlData(text);

    final response = await _dio.post<List<int>>(
      textToSpeechUrl,
      data: ssml,
      options: Options(
        responseType: ResponseType.bytes,
        headers: {
          HttpHeaders.contentTypeHeader: 'application/ssml+xml; charset=utf-8',
          'X-Microsoft-OutputFormat': outputFormat,
          HttpHeaders.userAgentHeader: userAgent,
          HttpHeaders.authorizationHeader: 'Bearer $token',
        },
      ),
    );

    final status = response.statusCode ?? 0;
    final data = response.data;
    if (status >= 200 && status < 300 && data != null) {
      return Uint8List.fromList(data);
    }

    final rawBody = response.data;
    final errorBody = rawBody == null
        ? ''
        : utf8.decode(
            rawBody is List<int> ? rawBody : utf8.encode(rawBody.toString()),
            allowMalformed: true,
          );
    throw HttpException(
      'Failed to convert text to speech (status $status): $errorBody',
      uri: Uri.parse(textToSpeechUrl),
    );
  }

  /// 不再需要实例时关闭底层的 [HttpClient]。
  void close({bool force = false}) => _dio.close(force: force);
}
