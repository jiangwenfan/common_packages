import 'package:flutter/material.dart';
import 'package:flutter_hooks/flutter_hooks.dart';

/// 简单一行单选按钮
class CCheckboxPlus extends HookWidget {
  final String title;
  final ValueNotifier<bool> state;

  const CCheckboxPlus({super.key, required this.title, required this.state});

  @override
  Widget build(BuildContext context) {
    return Row(
      children: [
        Checkbox(
          value: state.value,
          onChanged: (bool? value) => state.value = !state.value,
        ),
        Text(title),
      ],
    );
  }
}
