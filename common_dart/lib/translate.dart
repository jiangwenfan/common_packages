import 'dart:typed_data';

/// 后端支持的语言代码。
enum LanguageCodeOfBackend {
  zhCn('zh-CN'),
  zhTw('zh-TW'),
  en('en'),
  fr('fr'),
  ja('ja'),
  de('de'),
  es('es'),
  ko('ko');

  const LanguageCodeOfBackend(this.code);
  final String code;
}

/// 单词翻译结果结构。
class WordTranslation {
  const WordTranslation({
    required this.normalized,
    required this.display,
    required this.posTag,
    required this.frequency,
    required this.examples,
  });

  /// 2.1 标准化之后的翻译。
  final String normalized;

  /// 用于常见显示的翻译。
  final String display;

  /// 2.2 翻译词性, 是 part-of-speech tag 的简写，形如 ("Adjectives", "形容词")。
  final (String, String) posTag;

  /// 2.3 翻译频率，数据格式如 10.3（显示为 10.3%）。
  final double frequency;

  /// 2.4 翻译的例句。
  ///
  /// [
  ///   {
  ///     "sourcePrefix": "前半句",
  ///     "sourceTerm": "关键词",
  ///     "sourceSuffix": "后半句",
  ///     "target": [
  ///       {
  ///         "targetPrefix": "翻译前半句",
  ///         "targetTerm": "翻译关键词",
  ///         "targetSuffix": "翻译后半句",
  ///       }
  ///     ],
  ///   }
  /// ]
  final List<Map<String, dynamic>> examples;
}

/// 单词查询信息结构。
class WordInfo {
  const WordInfo({
    required this.normalizedWord,
    required this.displayWord,
    required this.translations,
    required this.shapes,
    required this.audioData,
    required this.extendedInfo,
  });

  /// 1. 传入 word 标准化之后的形式，word 表中唯一标识。
  final String normalizedWord;

  /// 1.1 用于常见显示的 word，通常处理大小写。
  final String displayWord;

  /// 2. word 翻译。
  final List<WordTranslation> translations;

  /// 3. 单词其他变体形式，例如复数、过去式等。
  final List<dynamic> shapes;

  /// 4. word 的发音数据。
  final Uint8List audioData;

  /// 5. 扩展信息。
  final Map<String, dynamic> extendedInfo;
}

/// 句子查询信息结构。
class SentenceInfo {
  const SentenceInfo({
    required this.sentence,
    required this.translations,
    required this.audioData,
  });

  /// 1. 原始 sentence 文本。
  final String sentence;

  /// 2. 翻译之后的文本。部分翻译提供商提供多个翻译。
  final List<String> translations;

  /// 3. 原始 sentence 的发音数据。
  final Uint8List audioData;
}
