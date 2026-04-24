import 'package:flutter/foundation.dart';
import 'package:flutter/services.dart';

import 'common_flutter_platform_interface.dart';

/// An implementation of [CommonFlutterPlatform] that uses method channels.
class MethodChannelCommonFlutter extends CommonFlutterPlatform {
  /// The method channel used to interact with the native platform.
  @visibleForTesting
  final methodChannel = const MethodChannel('common_flutter');

  @override
  Future<String?> getPlatformVersion() async {
    final version = await methodChannel.invokeMethod<String>('getPlatformVersion');
    return version;
  }
}
