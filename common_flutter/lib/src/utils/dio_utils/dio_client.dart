import 'package:dio/dio.dart';

import 'auth_interceptor.dart';
import 'data_model.dart';
import 'exception.dart';

/// GET / POST 封装，每个实例维护自己的服务地址和 Dio 实例。
class DioClient {
  /// 可传入 Dio 以配置适配器；传入后由本客户端负责关闭，请勿跨客户端共享。
  DioClient({required String baseUrl, Dio? dio}) : _dio = dio ?? Dio() {
    _dio.options = _dio.options.copyWith(
      baseUrl: baseUrl,
      connectTimeout: const Duration(seconds: 5),
      receiveTimeout: const Duration(seconds: 3),
      contentType: 'application/json',
    );
    _dio.interceptors.add(AuthInterceptor());
  }

  final Dio _dio;

  Future<ApiResponse> get(
    String path, {
    Map<String, dynamic>? queryParameters,
  }) => _request(() => _dio.get(path, queryParameters: queryParameters));

  Future<ApiResponse> post(
    String path, {
    dynamic data,
    Map<String, dynamic>? queryParameters,
  }) => _request(
    () => _dio.post(path, data: data, queryParameters: queryParameters),
  );

  Future<ApiResponse> _request(
    Future<Response<dynamic>> Function() send,
  ) async {
    try {
      final response = await send();
      return ApiResponse(isSuccess: true, payload: response.data);
    } on HandledRequestException catch (error) {
      return ApiResponse(isSuccess: false, payload: error.uiErrMessage);
    }
  }

  void close({bool force = false}) => _dio.close(force: force);
}
