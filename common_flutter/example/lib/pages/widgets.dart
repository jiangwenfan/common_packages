import 'package:flutter/material.dart';

import 'auth.dart';
import 'filter_list.dart';
import 'search.dart';

/// 原独立应用的演示内容，整合进现有示例的路由。
class WidgetsExample extends StatelessWidget {
  const WidgetsExample({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('搜索、筛选与登录表单')),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: const [
          SearchDemoPage(),
          SizedBox(height: 20),
          FilterListDemoPage(),
          Divider(),
          AuthDemoPage(),
          SizedBox(height: 20),
        ],
      ),
    );
  }
}
