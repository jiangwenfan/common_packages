// ignore_for_file: avoid_print

import 'dart:convert';

import 'package:crypto/crypto.dart';

/// 生成腾讯云 COS 上传所需的签名。
String generateTencentKey(
  String secretKey,
  String key,
  String secretId, {
  String method = 'get',
}) {
  final currentTime = DateTime.now();
  final futureTime = currentTime.add(const Duration(minutes: 30));

  final start = currentTime.millisecondsSinceEpoch ~/ 1000;
  final end = futureTime.millisecondsSinceEpoch ~/ 1000;

  final keyTime = '$start;$end';
  print('步骤一: key_time: $keyTime\n');

  final signKey = Hmac(sha1, utf8.encode(secretKey))
      .convert(utf8.encode(keyTime))
      .toString();
  print('步骤二: sign_key: $signKey\n');

  final normalizedMethod = method.toLowerCase();
  final httpString = '$normalizedMethod\n/$key\n\n\n';
  print('步骤五： http_string: ${httpString.replaceAll('\n', '\\n')}\n');

  final httpStringSha1 = sha1.convert(utf8.encode(httpString)).toString();
  final stringToSign = 'sha1\n$keyTime\n$httpStringSha1\n';
  print('步骤六: string_to_sign: ${stringToSign.replaceAll('\n', '\\n')}\n');

  final signature = Hmac(sha1, utf8.encode(signKey))
      .convert(utf8.encode(stringToSign))
      .toString();
  print('步骤七: signature: $signature');

  final authorization =
      'q-sign-algorithm=sha1&q-ak=$secretId&q-sign-time=$keyTime&q-key-time=$keyTime'
      '&q-header-list=&q-url-param-list=&q-signature=$signature';
  print('authorizaton: $authorization\n');

  return authorization;
}
