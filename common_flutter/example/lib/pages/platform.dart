import 'package:common_flutter/common_flutter.dart';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_hooks/flutter_hooks.dart';

class PlatformExample extends HookWidget {
  const PlatformExample({super.key});

  @override
  Widget build(BuildContext context) {
    final version = useState('Unknown');
    useEffect(() {
      var active = true;
      Future<void> loadVersion() async {
        String result;
        try {
          result =
              await CommonFlutter().getPlatformVersion() ??
              'Unknown platform version';
        } on MissingPluginException {
          result = '当前包尚无原生插件实现';
        } on PlatformException {
          result = 'Failed to get platform version.';
        }
        if (active) version.value = result;
      }

      loadVersion();
      return () => active = false;
    }, const []);

    return Scaffold(
      appBar: AppBar(title: const Text('平台接口雏形')),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          Text('Running on: ${version.value}'),
          const MyCustomWidget(),
        ],
      ),
    );
  }
}
