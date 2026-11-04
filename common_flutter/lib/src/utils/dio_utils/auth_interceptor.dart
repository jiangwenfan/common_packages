import 'dart:convert';

import 'package:dio/dio.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';

import 'data_model.dart';
import 'exception.dart';

/// 延续旧项目的认证存储配置和键名：access_token、headers。
const secureStorage = FlutterSecureStorage(
  aOptions: AndroidOptions(encryptedSharedPreferences: true),
  iOptions: IOSOptions(accessibility: KeychainAccessibility.first_unlock),
);

/// 从安全存储添加认证信息，并将请求错误转换为 UI 可读信息。
class AuthInterceptor extends Interceptor {
  AuthInterceptor({FlutterSecureStorage? storage})
    : _storage = storage ?? secureStorage;

  final FlutterSecureStorage _storage;

  Future<String?> getATokenFromLocal() => _storage.read(key: 'access_token');

  Future<Map<String, String>?> getHeadersFromLocal() async {
    final rawHeaders = await _storage.read(key: 'headers');
    if (rawHeaders == null || rawHeaders.trim().isEmpty) return null;

    final decoded = jsonDecode(rawHeaders);
    if (decoded is! Map) {
      throw const FormatException('headers 必须是 JSON 对象');
    }
    return {
      for (final entry in decoded.entries)
        entry.key.toString(): entry.value.toString(),
    };
  }

  @override
  void onRequest(
    RequestOptions options,
    RequestInterceptorHandler handler,
  ) async {
    try {
      final accessToken = await getATokenFromLocal();
      if (accessToken != null && accessToken.isNotEmpty) {
        options.headers['Authorization'] = 'Bearer $accessToken';
      }
      final headers = await getHeadersFromLocal();
      if (headers != null) options.headers.addAll(headers);
    } catch (error, stackTrace) {
      // 异步读取或 JSON 解析失败也必须完成 handler，避免请求一直等待。
      handler.reject(
        DioException(
          requestOptions: options,
          error: error,
          stackTrace: stackTrace,
          message: '读取本地认证信息失败',
        ),
        true,
      );
      return;
    }
    handler.next(options);
  }

  @override
  void onError(DioException err, ErrorInterceptorHandler handler) {
    if (err is HandledRequestException || err.type == DioExceptionType.cancel) {
      handler.next(err);
      return;
    }

    final statusCode = err.response?.statusCode;
    final Object? message;
    if (err.type == DioExceptionType.connectionTimeout ||
        err.type == DioExceptionType.sendTimeout ||
        err.type == DioExceptionType.receiveTimeout) {
      message = {'_': '网络连接超时，请稍后再试'};
    } else {
      message = switch (statusCode) {
        400 => err.response?.data,
        401 => {'_': '缺少 token、token 错误或 token 过期'},
        403 => {'_': '权限拒绝'},
        int code when code >= 500 => {'_': '服务器异常'},
        _ => err.response?.data ?? {'_': err.message ?? '请求异常'},
      };
    }

    handler.next(
      HandledRequestException(
        statusCode: statusCode,
        uiErrMessage: UIErrMessage(
          statusCode: statusCode,
          errorMessage: message,
        ),
        requestOptions: err.requestOptions,
        response: err.response,
        type: err.type,
        message: err.message,
        stackTrace: err.stackTrace,
      ),
    );
  }
}
