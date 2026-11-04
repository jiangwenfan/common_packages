import 'dart:convert';

import 'package:common_flutter/common_flutter.dart';
import 'package:example/demo_dio/api_services.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:flutter_test/flutter_test.dart';

class _StubClient extends DioClient {
  _StubClient(this.response) : super(baseUrl: 'https://example.test');

  final ApiResponse response;

  @override
  Future<ApiResponse> post(
    String path, {
    dynamic data,
    Map<String, dynamic>? queryParameters,
  }) async => response;
}

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();
  setUp(
    () => FlutterSecureStorage.setMockInitialValues({
      'access_token': 'existing-token',
    }),
  );

  test('登录失败不读取 token，也不覆盖已有认证信息', () async {
    final failure = ApiResponse(
      isSuccess: false,
      payload: UIErrMessage(statusCode: 401, errorMessage: null),
    );
    final client = _StubClient(failure);
    addTearDown(client.close);
    final response = await Api(client: client).login({});
    expect(identical(response, failure), isTrue);
    expect(await secureStorage.read(key: 'access_token'), 'existing-token');
    expect(await secureStorage.read(key: 'headers'), isNull);
  });

  for (final payload in <Object?>[
    null,
    'not a map',
    {},
    {'token': 123},
    {'token': ' '},
  ]) {
    test('无效登录响应 $payload 返回错误并保留已有认证信息', () async {
      final client = _StubClient(
        ApiResponse(isSuccess: true, payload: payload),
      );
      addTearDown(client.close);
      final response = await Api(client: client).login({});
      expect(response.isSuccess, isFalse);
      expect(response.payload, isA<UIErrMessage>());
      expect(await secureStorage.read(key: 'access_token'), 'existing-token');
      expect(await secureStorage.read(key: 'headers'), isNull);
    });
  }

  test('有效登录响应保存 token 和原有客户请求头', () async {
    final client = _StubClient(
      const ApiResponse(isSuccess: true, payload: {'token': 'new-token'}),
    );
    addTearDown(client.close);
    final response = await Api(client: client).login({});
    expect(response.isSuccess, isTrue);
    expect(await secureStorage.read(key: 'access_token'), 'new-token');
    expect(jsonDecode((await secureStorage.read(key: 'headers'))!), {
      'x-customer-id': '4',
    });
  });
}
