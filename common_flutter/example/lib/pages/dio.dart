import 'package:flutter/material.dart';

import '../demo_dio/widgets.dart';

class DioExample extends StatelessWidget {
  const DioExample({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Dio 请求演示')),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: const [DioWidget()],
      ),
    );
  }
}
