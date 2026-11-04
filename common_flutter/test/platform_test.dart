import 'package:common_flutter/common_flutter.dart';
import 'package:flutter/services.dart';
import 'package:flutter_test/flutter_test.dart';

class _FakePlatform extends CommonFlutterPlatform {
  @override
  Future<String?> getPlatformVersion() async => '42';
}

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();
  const channel = MethodChannel('common_flutter');
  final messenger =
      TestDefaultBinaryMessengerBinding.instance.defaultBinaryMessenger;
  late CommonFlutterPlatform initialPlatform;

  setUp(() => initialPlatform = CommonFlutterPlatform.instance);
  tearDown(() {
    CommonFlutterPlatform.instance = initialPlatform;
    messenger.setMockMethodCallHandler(channel, null);
  });

  test('默认保留旧 MethodChannel 平台接口', () {
    expect(CommonFlutterPlatform.instance, isA<MethodChannelCommonFlutter>());
  });

  test('平台外壳委托给注入的平台实现', () async {
    CommonFlutterPlatform.instance = _FakePlatform();
    expect(await CommonFlutter().getPlatformVersion(), '42');
  });

  test('保留原通道名称和 getPlatformVersion 方法协议', () async {
    messenger.setMockMethodCallHandler(channel, (call) async {
      expect(call.method, 'getPlatformVersion');
      expect(call.arguments, isNull);
      return '42';
    });
    expect(await MethodChannelCommonFlutter().getPlatformVersion(), '42');
  });

  test('没有原生实现时明确抛出 MissingPluginException', () async {
    await expectLater(
      CommonFlutter().getPlatformVersion(),
      throwsA(isA<MissingPluginException>()),
    );
  });
}
