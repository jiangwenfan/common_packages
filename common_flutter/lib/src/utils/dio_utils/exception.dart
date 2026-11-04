import 'package:dio/dio.dart';

import 'data_model.dart';

/// 已转换为 UI 错误信息的请求异常，保留原请求、响应及异常类型。
class HandledRequestException extends DioException {
  HandledRequestException({
    required int? statusCode,
    required this.uiErrMessage,
    required super.requestOptions,
    super.response,
    super.type = DioExceptionType.badResponse,
    super.message,
    super.stackTrace,
  }) : statusCode = statusCode ?? 0,
       super(error: uiErrMessage);

  final int statusCode;
  final UIErrMessage uiErrMessage;

  @override
  String toString() =>
      'HandledRequestException: $uiErrMessage, statusCode: $statusCode';
}
