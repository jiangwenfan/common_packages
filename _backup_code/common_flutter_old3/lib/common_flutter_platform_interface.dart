import 'package:plugin_platform_interface/plugin_platform_interface.dart';

import 'common_flutter_method_channel.dart';

abstract class CommonFlutterPlatform extends PlatformInterface {
  /// Constructs a CommonFlutterPlatform.
  CommonFlutterPlatform() : super(token: _token);

  static final Object _token = Object();

  static CommonFlutterPlatform _instance = MethodChannelCommonFlutter();

  /// The default instance of [CommonFlutterPlatform] to use.
  ///
  /// Defaults to [MethodChannelCommonFlutter].
  static CommonFlutterPlatform get instance => _instance;

  /// Platform-specific implementations should set this with their own
  /// platform-specific class that extends [CommonFlutterPlatform] when
  /// they register themselves.
  static set instance(CommonFlutterPlatform instance) {
    PlatformInterface.verifyToken(instance, _token);
    _instance = instance;
  }

  Future<String?> getPlatformVersion() {
    throw UnimplementedError('platformVersion() has not been implemented.');
  }
}
