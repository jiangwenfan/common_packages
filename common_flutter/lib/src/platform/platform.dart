import 'platform_interface.dart';

/// 旧项目的平台查询外壳，当前包没有提供对应的原生插件实现。
///
/// 直接调用可能抛出 MissingPluginException，迁移时未补齐原生实现。
class CommonFlutter {
  Future<String?> getPlatformVersion() =>
      CommonFlutterPlatform.instance.getPlatformVersion();
}
