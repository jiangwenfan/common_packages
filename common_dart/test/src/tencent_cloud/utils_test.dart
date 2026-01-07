// ignore_for_file: avoid_print

import 'package:common_dart/src/tencent_cloud/utils.dart';
import 'package:dotenv/dotenv.dart';
import 'package:test/test.dart';

void main() {
  final env = DotEnv(includePlatformEnvironment: true)..load(['.env']);

  final secretKey = env['TENCENT_COS_SECRET_KEY'];
  final secretId = env['TENCENT_COS_SECRET_ID'];
  final objectKey = env['TENCENT_COS_OBJECT_KEY'] ?? 'test.png';
  final method = env['TENCENT_COS_METHOD'] ?? 'get';

  final String? skipReason =
      (secretKey == null || secretKey.isEmpty || secretId == null || secretId.isEmpty)
          ? '需要 .env 或环境变量中的 TENCENT_COS_SECRET_KEY 与 TENCENT_COS_SECRET_ID 才能运行腾讯云签名测试'
          : null;

  group('generateTencentKey', () {
    test('生成 authorization 字符串', () {
      final authorization = generateTencentKey(
        secretKey!,
        objectKey,
        secretId!,
        method: method,
      );

      print(authorization);
      expect(authorization, isNotEmpty);
      expect(authorization.contains('q-signature='), isTrue);
      expect(authorization.contains('q-ak=$secretId'), isTrue);
    });
  }, skip: skipReason);
}
