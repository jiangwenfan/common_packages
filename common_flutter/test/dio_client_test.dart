import 'dart:convert';

import 'package:common_flutter/common_flutter.dart';
import 'package:dio/dio.dart';
import 'package:flutter/services.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:flutter_test/flutter_test.dart';

class _Adapter implements HttpClientAdapter {
  _Adapter(this.respond);

  final ResponseBody Function(RequestOptions) respond;
  final requests = <RequestOptions>[];

  @override
  Future<ResponseBody> fetch(
    RequestOptions options,
    Stream<Uint8List>? requestStream,
    Future<void>? cancelFuture,
  ) async {
    requests.add(options);
    return respond(options);
  }

  @override
  void close({bool force = false}) {}
}

ResponseBody _json(Object? data, [int status = 200]) => ResponseBody.fromString(
  jsonEncode(data),
  status,
  headers: {
    Headers.contentTypeHeader: [Headers.jsonContentType],
  },
);

class _UnavailableStorage extends FlutterSecureStorage {
  @override
  Future<String?> read({
    required String key,
    IOSOptions? iOptions,
    AndroidOptions? aOptions,
    LinuxOptions? lOptions,
    WebOptions? webOptions,
    MacOsOptions? mOptions,
    WindowsOptions? wOptions,
  }) async => throw PlatformException(code: 'unavailable');
}

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();
  setUp(() => FlutterSecureStorage.setMockInitialValues({}));

  (DioClient, _Adapter) clientFor(
    ResponseBody Function(RequestOptions) respond, {
    String baseUrl = 'https://first.test',
  }) {
    final adapter = _Adapter(respond);
    final dio = Dio()..httpClientAdapter = adapter;
    final client = DioClient(baseUrl: baseUrl, dio: dio);
    addTearDown(client.close);
    return (client, adapter);
  }

  test('不同客户端保留各自的 baseUrl 和 GET 查询参数', () async {
    final (first, firstAdapter) = clientFor((_) => _json({'name': 'first'}));
    final (second, secondAdapter) = clientFor(
      (_) => _json({'name': 'second'}),
      baseUrl: 'https://second.test',
    );
    final firstResult = await first.get('/items', queryParameters: {'page': 2});
    final secondResult = await second.get('/items');

    expect(identical(first, second), isFalse);
    expect(firstResult.isSuccess, isTrue);
    expect(firstResult.payload, {'name': 'first'});
    expect(secondResult.payload, {'name': 'second'});
    expect(firstAdapter.requests.single.uri.host, 'first.test');
    expect(firstAdapter.requests.single.uri.queryParameters, {'page': '2'});
    expect(secondAdapter.requests.single.uri.host, 'second.test');
  });

  test('POST 保留请求数据，认证信息每次从存储读取', () async {
    FlutterSecureStorage.setMockInitialValues({
      'access_token': 'first-token',
      'headers': '{"x-customer-id":4}',
    });
    final (client, adapter) = clientFor((_) => _json({'created': true}, 201));
    final result = await client.post(
      '/items',
      data: {'name': 'demo'},
      queryParameters: {'draft': true},
    );
    expect(result.isSuccess, isTrue);
    final request = adapter.requests.single;
    expect(request.method, 'POST');
    expect(request.data, {'name': 'demo'});
    expect(request.uri.queryParameters, {'draft': 'true'});
    expect(request.headers['Authorization'], 'Bearer first-token');
    expect(request.headers['x-customer-id'], '4');

    await secureStorage.write(key: 'access_token', value: 'second-token');
    await client.get('/items');
    expect(
      adapter.requests.last.headers['Authorization'],
      'Bearer second-token',
    );
  });

  for (final rawHeaders in ['not json', '[]', '123', 'null']) {
    test('无效 headers $rawHeaders 会结束请求且不访问服务', () async {
      FlutterSecureStorage.setMockInitialValues({'headers': rawHeaders});
      final (client, adapter) = clientFor((_) => _json({}));
      final result = await client
          .get('/items')
          .timeout(const Duration(seconds: 1));
      expect(result.isSuccess, isFalse);
      expect((result.payload as UIErrMessage).errorMessage['_'], '读取本地认证信息失败');
      expect(adapter.requests, isEmpty);
    });
  }

  test('安全存储读取失败会结束请求并保留异常类型', () async {
    final adapter = _Adapter((_) => _json({}));
    final dio = Dio(BaseOptions(baseUrl: 'https://example.test'))
      ..httpClientAdapter = adapter
      ..interceptors.add(AuthInterceptor(storage: _UnavailableStorage()));
    addTearDown(dio.close);
    await expectLater(
      dio.get('/items').timeout(const Duration(seconds: 1)),
      throwsA(
        isA<HandledRequestException>()
            .having((error) => error.type, 'type', DioExceptionType.unknown)
            .having(
              (error) => error.uiErrMessage.errorMessage['_'],
              'message',
              '读取本地认证信息失败',
            ),
      ),
    );
    expect(adapter.requests, isEmpty);
  });

  test('400 响应保留表单字段错误', () async {
    final (client, _) = clientFor(
      (_) => _json({
        'email': ['必填'],
      }, 400),
    );
    final result = await client.post('/login', data: {});
    expect(result.isSuccess, isFalse);
    final message = result.payload as UIErrMessage;
    expect(message.statusCode, 400);
    expect(message.needsErrorParsing, isTrue);
    expect(message.errorMessage, {
      'email': ['必填'],
    });
  });

  for (final body in <Object?>[
    'invalid request',
    ['invalid'],
    null,
    {},
  ]) {
    test('400 非标准错误体 $body 不会引发类型异常', () async {
      final (client, _) = clientFor((_) => _json(body, 400));
      final result = await client.get('/items');
      expect(result.isSuccess, isFalse);
      final message = result.payload as UIErrMessage;
      expect(message.statusCode, 400);
      expect(
        message.errorMessage['_'],
        isA<String>().having((s) => s.isNotEmpty, 'nonempty', true),
      );
    });
  }

  for (final status in [401, 403, 500, 502]) {
    test('$status 的 HTML 错误响应转换为 UI 错误', () async {
      final (client, _) = clientFor(
        (_) => ResponseBody.fromString('<html>error</html>', status),
      );
      final result = await client.get('/items');
      expect(result.isSuccess, isFalse);
      final message = result.payload as UIErrMessage;
      expect(message.statusCode, status);
      expect(message.needsErrorParsing, isFalse);
      expect(message.errorMessage['_'], isNotEmpty);
    });
  }

  for (final type in [
    DioExceptionType.connectionTimeout,
    DioExceptionType.receiveTimeout,
    DioExceptionType.sendTimeout,
    DioExceptionType.connectionError,
  ]) {
    test('$type 没有响应时也返回失败结果', () async {
      final (client, _) = clientFor(
        (request) => throw DioException(
          requestOptions: request,
          type: type,
          message: 'network failure',
        ),
      );
      final result = await client.get('/items');
      expect(result.isSuccess, isFalse);
      expect((result.payload as UIErrMessage).statusCode, 0);
      expect((result.payload as UIErrMessage).errorMessage['_'], isNotEmpty);
    });
  }

  test('错误转换保留原始响应和请求上下文', () async {
    final dio = Dio()
      ..httpClientAdapter = _Adapter((_) => _json({'email': 'invalid'}, 400));
    final client = DioClient(baseUrl: 'https://example.test', dio: dio);
    addTearDown(client.close);
    DioException? captured;
    dio.interceptors.add(
      InterceptorsWrapper(
        onError: (error, handler) {
          captured = error;
          handler.next(error);
        },
      ),
    );
    await client.get('/items');
    expect(captured, isA<HandledRequestException>());
    expect(captured!.response!.data, {'email': 'invalid'});
    expect(captured!.requestOptions.uri.path, '/items');
    expect(captured!.type, DioExceptionType.badResponse);
  });

  test('取消请求保留 Dio 取消异常', () async {
    final (client, _) = clientFor(
      (request) => throw DioException(
        requestOptions: request,
        type: DioExceptionType.cancel,
      ),
    );
    await expectLater(
      client.get('/items'),
      throwsA(
        isA<DioException>().having(
          (error) => error.type,
          'type',
          DioExceptionType.cancel,
        ),
      ),
    );
  });
}
