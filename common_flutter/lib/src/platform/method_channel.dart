import 'package:flutter/foundation.dart';
import 'package:flutter/services.dart';

import 'platform_interface.dart';

/// 保留旧 MethodChannel 协议，尚无配套的原生通道处理代码。
class MethodChannelCommonFlutter extends CommonFlutterPlatform {
  @visibleForTesting
  final methodChannel = const MethodChannel('common_flutter');

  @override
  Future<String?> getPlatformVersion() =>
      methodChannel.invokeMethod<String>('getPlatformVersion');
}
