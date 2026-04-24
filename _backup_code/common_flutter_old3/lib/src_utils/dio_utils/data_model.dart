// 该类主要是用来展示，当请求出错时，在ui层上需要展示的错误信息
class UIErrMessage {
  // 请求的状态码
  final int statusCode;

  /*
   表示是否需要解析错误信息
    true: 需要解析错误信息,400错误
    false: 不需要解析错误信息,非400错误
  */
  final bool needsErrorParsing;

  /*
    该字段用于 UI 显示的错误信息
      needsErrorParsing 为 true 时，表示需要解析错误信息
      needsErrorParsing 为 false 时，表示不需要解析错误信息,从key为_的字段中获取错误信息,如果没有提供该字段，则使用默认的错误信息
  */
  final Map<String, dynamic> errorMessage;
  // 默认的错误信息
  static const Map<String, dynamic> baseM = {"_": "默认错误信息-请求异常"};

  UIErrMessage({
    required int? statusCode,
    required Map<String, dynamic>? errorMessage,
  }) : statusCode = statusCode ?? 0,
       // 400 为true, 其他为false
       needsErrorParsing = statusCode == 400,
       // 400 时, 不为空使用原始响应的错误信息，为空时使用默认的错误信息
       // 非400时如果使用：默认+[不为空]响应的信息
       errorMessage =
           statusCode == 400
               ? errorMessage ?? {"_": "[未知错误]应该是400错误，实际上没有,"}
               : {...baseM, ...?errorMessage};

  // 格式化请求异常信息
  @override
  String toString() {
    return 'UIErrMessage{needsErrorParsing: $needsErrorParsing, errorMessage: $errorMessage}';
  }
}

// api响应结果
class ApiResponse {
  //  true 表示成功，false 表示失败
  final bool isSuccess;

  // data 表示响应的内容；可能是成功的Map数据，也可能是失败的String数据
  /// The response payload:
  /// - success → Map / model
  /// - failure →  MyCustomException: UIErrMessage{needsErrorParsing: false, errorMessage: {_: 服务器异常: 请求失败}}

  final dynamic payload;

  ApiResponse({required this.isSuccess, required this.payload});

  @override
  String toString() => 'ApiResponse{isSuccess: $isSuccess, payload: $payload}';
}
