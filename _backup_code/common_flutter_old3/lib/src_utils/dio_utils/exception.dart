import 'package:dio/dio.dart';
import 'data_model.dart';

// 这是一个处理过之后的请求异常
class HandledRequestException extends DioException {
  /// 请求的状态码,默认是0
  final int statusCode;

  // 该字段用于 UI 显示的错误信息
  final UIErrMessage uiErrMessage;

  HandledRequestException({
    required int? statusCode,
    required this.uiErrMessage,
    // 请求的异常配置 err.requestOptions, err是DioException
    required super.requestOptions,
    super.response,
  }) : statusCode = statusCode ?? 0,
       super(type: DioExceptionType.badResponse, error: uiErrMessage);

  // 格式化请求异常信息
  @override
  String toString() =>
      'HandledRequestException: $uiErrMessage, statusCode: $statusCode';
}
