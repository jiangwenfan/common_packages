import 'dart:convert';

import 'package:common_flutter/common_flutter.dart';

/// 原项目地址是占位值；运行时可通过 --dart-define 配置演示服务。
const demoApiBaseUrl = String.fromEnvironment('DEMO_API_BASE_URL');

class Api {
  Api({DioClient? client})
    : _dioClient = client ?? DioClient(baseUrl: demoApiBaseUrl);

  final DioClient _dioClient;

  Future<ApiResponse> login(Map<String, dynamic> data) async {
    final response = await _dioClient.post('/users/login/', data: data);
    if (!response.isSuccess) return response;

    final payload = response.payload;
    final token = payload is Map ? payload['token'] : null;
    if (token is! String || token.trim().isEmpty) {
      return ApiResponse(
        isSuccess: false,
        payload: UIErrMessage(
          statusCode: null,
          errorMessage: const {'_': '登录响应缺少有效 token'},
        ),
      );
    }

    await secureStorage.write(key: 'access_token', value: token);
    await secureStorage.write(
      key: 'headers',
      value: jsonEncode({'x-customer-id': '4'}),
    );
    return response;
  }

  Future<ApiResponse> getCustomersOk() => _dioClient.get('/customers/');

  Future<ApiResponse> getCustomersErr500() async {
    await secureStorage.delete(key: 'access_token');
    return _dioClient.get('/customers/');
  }

  Future<ApiResponse> getCustomersErr401() async {
    await secureStorage.write(key: 'access_token', value: '123');
    return _dioClient.get('/customers/');
  }

  Future<ApiResponse> createEntitiesOk(Map<String, dynamic> data) =>
      _dioClient.post('/entities/', data: data);

  Future<ApiResponse> createEntitiesErr400(Map<String, dynamic> data) =>
      _dioClient.post('/entities/', data: data);

  void close() => _dioClient.close();
}
