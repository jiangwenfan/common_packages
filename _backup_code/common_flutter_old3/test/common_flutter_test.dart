import 'package:flutter_test/flutter_test.dart';
import 'package:common_flutter/common_flutter.dart';
import 'package:common_flutter/common_flutter_platform_interface.dart';
import 'package:common_flutter/common_flutter_method_channel.dart';
import 'package:plugin_platform_interface/plugin_platform_interface.dart';

class MockCommonFlutterPlatform
    with MockPlatformInterfaceMixin
    implements CommonFlutterPlatform {

  @override
  Future<String?> getPlatformVersion() => Future.value('42');
}

void main() {
  final CommonFlutterPlatform initialPlatform = CommonFlutterPlatform.instance;

  test('$MethodChannelCommonFlutter is the default instance', () {
    expect(initialPlatform, isInstanceOf<MethodChannelCommonFlutter>());
  });

  test('getPlatformVersion', () async {
    CommonFlutter commonFlutterPlugin = CommonFlutter();
    MockCommonFlutterPlatform fakePlatform = MockCommonFlutterPlatform();
    CommonFlutterPlatform.instance = fakePlatform;

    expect(await commonFlutterPlugin.getPlatformVersion(), '42');
  });
}
