import 'package:dio/dio.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'dart:convert';
import 'exception.dart';
import 'data_model.dart';

// 创建一个 FlutterSecureStorage 实例
final secureStorage = FlutterSecureStorage(
  aOptions: const AndroidOptions(encryptedSharedPreferences: true),
  iOptions: const IOSOptions(accessibility: KeychainAccessibility.first_unlock),
);

// 自定义拦截器类，负责自动添加请求头以及处理响应和错误
class AuthInterceptor extends Interceptor {
  // 从本地获取 access token
  Future<String?> getATokenFromLocal() async {
    String? token = await secureStorage.read(key: 'access_token');
    return token;
  }

  // 从本地获取所有要添加的请求头
  Future<Map<String, String>?> getHeadersFromLocal() async {
    String? headers = await secureStorage.read(key: "headers");
    if (headers == null) {
      return null;
    }

    Map<String, dynamic> jsonMap = json.decode(headers);

    // 将 headers 字符串转换为 Map<String, String>
    Map<String, String> headersMap = {};
    jsonMap.forEach((key, value) {
      headersMap[key] = value.toString();
    });
    return headersMap;
  }

  @override
  void onRequest(
    RequestOptions options,
    RequestInterceptorHandler handler,
  ) async {
    // 1. 添加 access token
    String? accessToken = await getATokenFromLocal();
    // print("添加token: $accessToken");
    if (accessToken != null && accessToken.isNotEmpty) {
      options.headers["Authorization"] = "Bearer $accessToken";
    }

    // 2. 添加请求头
    Map<String, String>? headers = await getHeadersFromLocal();
    if (headers != null && headers.isNotEmpty) {
      headers.forEach((key, value) {
        // 添加所有请求头
        options.headers[key] = value;
      });
    }

    handler.next(options);
  }

  @override
  void onResponse(Response response, ResponseInterceptorHandler handler) {
    handler.next(response);
  }

  @override
  void onError(DioException err, ErrorInterceptorHandler handler) {
    // 第一个拦截器出错响应之后，第二个拦截器也会执行出错响应
    if (err.type == DioExceptionType.connectionTimeout ||
        err.type == DioExceptionType.receiveTimeout) {
      // print("网络连接超时，请稍后再试");
      return handler.reject(
        HandledRequestException(
          statusCode: err.response?.statusCode,
          uiErrMessage: UIErrMessage(
            statusCode: err.response?.statusCode,
            errorMessage: err.response?.data,
          ),
          requestOptions: err.requestOptions,
        ),
      );
    } else if (err.response != null) {
      switch (err.response?.statusCode) {
        case 400:
          // print(
          //   "请求参数错误: ${err.response?.statusCode} , ${err.response?.data},${err.response?.data.runtimeType}",
          // );
          // 使用 reject 替换异常，阻断错误继续传播
          return handler.reject(
            HandledRequestException(
              statusCode: err.response?.statusCode,
              uiErrMessage: UIErrMessage(
                statusCode: err.response?.statusCode,
                errorMessage: err.response?.data,
              ),
              requestOptions: err.requestOptions,
            ),
          );
        // break;
        case 401:
          // print(
          //   "缺少token,token错误,token过期: ${err.response?.statusCode} , ${err.response?.data}",
          // );
          return handler.reject(
            HandledRequestException(
              statusCode: err.response?.statusCode,
              uiErrMessage: UIErrMessage(
                statusCode: err.response?.statusCode,
                errorMessage: {
                  "_": "缺少token,token错误,token过期--->${err.response?.data}",
                },
              ),
              requestOptions: err.requestOptions,
            ),
          );
        // break;
        case 403:
          // print("权限拒绝: ${err.response?.statusCode} , ${err.response?.data}");
          return handler.reject(
            HandledRequestException(
              statusCode: err.response?.statusCode,
              uiErrMessage: UIErrMessage(
                statusCode: err.response?.statusCode,
                errorMessage: {"_": "权限拒绝--->${err.response?.data}"},
              ),
              requestOptions: err.requestOptions,
            ),
          );
        case 500:
          // print("服务器异常: ${err.response?.statusCode} , ${err.response?.data}");
          return handler.reject(
            HandledRequestException(
              statusCode: err.response?.statusCode,
              uiErrMessage: UIErrMessage(
                statusCode: err.response?.statusCode,
                errorMessage: {"_": "服务器异常"},
              ),
              requestOptions: err.requestOptions,
            ),
          );
        default:
          // print("未知的请求出错：${err.response?.statusCode}");
          return handler.reject(
            HandledRequestException(
              statusCode: err.response?.statusCode,
              uiErrMessage: UIErrMessage(
                statusCode: err.response?.statusCode,
                errorMessage: {"_": "未知的请求出错1"},
              ),
              requestOptions: err.requestOptions,
            ),
          );
      }
    }
    handler.next(err);
  }
}
