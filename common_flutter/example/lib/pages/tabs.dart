import 'package:flutter/material.dart';
import 'package:flutter_hooks/flutter_hooks.dart';
import 'package:common_flutter/common_flutter.dart';

class TabsExample extends HookWidget {
  const TabsExample({super.key});

  @override
  Widget build(BuildContext context) {
    final d = [
      TabType(
        key: "1",
        title: Text('按钮1按钮1按钮1按钮1按钮1'),
        content: Container(width: 100, height: 100, color: Colors.blue[300]),
      ),
      TabType(
        key: "2",
        title: Text('按钮2'),
        content: Container(width: 200, height: 200, color: Colors.green[300]),
      ),
      TabType(
        key: "3",
        title: Text('按钮3按钮3'),
        content: Container(width: 300, height: 300, color: Colors.red[300]),
      ),
    ];
    return Scaffold(
      appBar: AppBar(title: Text("tabs example")),
      body: ListView(
        children: [
          CTabs(tabs: d, initialKey: "3"),

          // 输入不存在的key,就显示第一个tab
          SizedBox(height: 20),
          CTabs(tabs: d, initialKey: "999"),

          // 不输入initialKey,就显示第一个tab
          SizedBox(height: 20),
          CTabs(tabs: d),
        ],
      ),
    );
  }
}
