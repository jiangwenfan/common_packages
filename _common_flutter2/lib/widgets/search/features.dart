/*
使用了: flutter pub add flutter_hooks
搜索输入框,封装普通textField,
- 当输入框内部有内容时，尾部显示x，点击x可以清空输入框
*/

export 'core.dart';

// 演示
import 'package:flutter/material.dart';
import 'package:flutter_hooks/flutter_hooks.dart';
import 'core.dart';

class SearchDemoPage extends HookWidget {
  const SearchDemoPage({super.key});

  @override
  Widget build(BuildContext context) {
    final inputText = useState('');
    return Column(
      children: [
        CSearch(
          onChanged: (value) {
            print("--$value");
            inputText.value = value;
          },
        ),

        Text(inputText.value),
      ],
    );
  }
}
