import 'package:flutter/material.dart';

class CButton extends StatelessWidget {
  final String title;
  const CButton({super.key, required this.title});

  @override
  Widget build(BuildContext context) {
    return ElevatedButton(
      onPressed: () {
        print('点击了按钮 $title');
      },
      child: Text(title, style: TextStyle(fontSize: 16)),
    );
  }
}
