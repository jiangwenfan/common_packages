import 'package:plugin_platform_interface/plugin_platform_interface.dart';

import 'method_channel.dart';

/// 旧项目的平台接口占位，目前没有 Android / iOS 原生实现。
abstract class CommonFlutterPlatform extends PlatformInterface {
  CommonFlutterPlatform() : super(token: _token);

  static final Object _token = Object();
  static CommonFlutterPlatform _instance = MethodChannelCommonFlutter();

  static CommonFlutterPlatform get instance => _instance;

  static set instance(CommonFlutterPlatform instance) {
    PlatformInterface.verifyToken(instance, _token);
    _instance = instance;
  }

  Future<String?> getPlatformVersion() {
    throw UnimplementedError('platformVersion() has not been implemented.');
  }
}
