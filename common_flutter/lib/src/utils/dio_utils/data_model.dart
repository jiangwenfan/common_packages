/// 请求失败时供 UI 展示的错误信息。
class UIErrMessage {
  UIErrMessage({required int? statusCode, required Object? errorMessage})
    : statusCode = statusCode ?? 0,
      needsErrorParsing = statusCode == 400,
      errorMessage = _messageFor(statusCode, errorMessage);

  final int statusCode;

  /// 400 响应可包含按表单字段组织的错误，其余错误使用 `_` 展示摘要。
  final bool needsErrorParsing;
  final Map<String, dynamic> errorMessage;

  static const Map<String, dynamic> baseM = {'_': '默认错误信息-请求异常'};

  static Map<String, dynamic> _messageFor(int? statusCode, Object? data) {
    final Map<String, dynamic> message;
    if (data is Map) {
      message = {
        for (final entry in data.entries) entry.key.toString(): entry.value,
      };
    } else if (data == null || (data is String && data.trim().isEmpty)) {
      message = {};
    } else {
      message = {'_': data.toString()};
    }

    if (statusCode == 400) {
      return message.isEmpty ? {'_': '请求参数错误'} : message;
    }
    return {...baseM, ...message};
  }

  @override
  String toString() =>
      'UIErrMessage{needsErrorParsing: $needsErrorParsing, errorMessage: $errorMessage}';
}

/// API 调用结果：成功时 payload 为响应数据，已处理的失败为 [UIErrMessage]。
class ApiResponse {
  const ApiResponse({required this.isSuccess, required this.payload});

  final bool isSuccess;
  final dynamic payload;

  @override
  String toString() => 'ApiResponse{isSuccess: $isSuccess, payload: $payload}';
}
