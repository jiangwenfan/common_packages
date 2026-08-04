// ignore_for_file: avoid_print

import 'dart:typed_data';

import 'package:dio/dio.dart';

import 'utils.dart';

/// 腾讯云 COS 简单封装。
class TencentCos {
  TencentCos({
    required this.bucket,
    required this.region,
    required this.secretKey,
    required this.secretId,
    Dio? dio,
  }) : _dio = dio ?? Dio();

  final String bucket;
  final String region;
  final String secretKey;
  final String secretId;
  final Dio _dio;

  String _buildUrl(String filename) =>
      'https://$bucket.cos.$region.myqcloud.com/$filename';

  /// 上传文件内容到 COS。
  /// [filename] 仅包含对象名（不含前导路径）。
  /// 返回 (success, messageOrFilename)。
  Future<(bool, String)> save(
    String filename,
    List<int> content, {
    String contentType = 'image/jpeg',
  }) async {
    final url = _buildUrl(filename);
    final authorization = generateTencentKey(
      secretKey,
      filename,
      secretId,
      method: 'put',
    );

    try {
      final response = await _dio.put<Object?>(
        url,
        data: content,
        options: Options(
          headers: {
            'Authorization': authorization,
            'Content-Type': contentType,
          },
        ),
      );

      final status = response.statusCode ?? 0;
      final success = status >= 200 && status < 300;
      final message = success
          ? filename
          : 'COS upload failed: HTTP $status ${response.statusMessage ?? ''}';

      print(
        'tencent cos save file $filename result. statusCode=$status success=$success',
      );
      return (success, message);
    } catch (e) {
      print('tencent cos save file $filename failed: $e');
      return (false, e.toString());
    }
  }

  /// 从 COS 读取文件内容。
  /// 返回 (success, data)。
  Future<(bool, Uint8List)> load(String filename) async {
    final url = _buildUrl(filename);
    final authorization = generateTencentKey(secretKey, filename, secretId);

    try {
      final response = await _dio.get<List<int>>(
        url,
        options: Options(
          headers: {'Authorization': authorization},
          responseType: ResponseType.bytes,
        ),
      );

      final status = response.statusCode ?? 0;
      final success = status >= 200 && status < 300;
      final bytes =
          response.data != null ? Uint8List.fromList(response.data!) : Uint8List(0);

      print(
        'tencent cos load file $filename result. statusCode=$status success=$success',
      );
      return (success, success ? bytes : Uint8List(0));
    } catch (e) {
      print('tencent cos load file $filename failed: $e');
      return (false, Uint8List(0));
    }
  }
}
