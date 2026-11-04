import 'package:flutter/material.dart';

/// 基础按钮雏形：保留原来的点击日志，尚未接入业务回调。
class CButton extends StatelessWidget {
  const CButton({super.key, required this.title});

  final String title;

  @override
  Widget build(BuildContext context) {
    return ElevatedButton(
      onPressed: () {
        debugPrint('点击了按钮 $title');
      },
      child: Text(title),
    );
  }
}
