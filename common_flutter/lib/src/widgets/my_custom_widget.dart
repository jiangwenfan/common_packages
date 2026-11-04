import 'package:flutter/material.dart';

/// 从旧项目保留的简单自定义控件示例，文字使用宿主主题。
class MyCustomWidget extends StatelessWidget {
  const MyCustomWidget({super.key});

  @override
  Widget build(BuildContext context) {
    return Text(
      'Hello from MyCustomWidget!',
      style: Theme.of(context).textTheme.headlineSmall,
    );
  }
}
