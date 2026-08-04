import 'package:flutter/material.dart';

/// 一个简单的自定义控件示例
class MyCustomWidget extends StatelessWidget {
  const MyCustomWidget({super.key});

  @override
  Widget build(BuildContext context) {
    return Text(
      'Hello from MyCustomWidget!',
      style: TextStyle(fontSize: 24, color: Colors.blue),
    );
  }
}
