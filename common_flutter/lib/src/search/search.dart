import 'package:flutter/material.dart';
import 'package:flutter_hooks/flutter_hooks.dart';

/// 搜索输入框，支持输入和清空后通知调用方。
class CSearch extends HookWidget {
  const CSearch({super.key, required this.onChanged});

  final ValueChanged<String> onChanged;

  @override
  Widget build(BuildContext context) {
    final controller = useTextEditingController();
    final focusNode = useFocusNode();
    // 监听程序修改和用户输入，使清空按钮跟随文本变化。
    useListenable(controller);

    return TextField(
      controller: controller,
      focusNode: focusNode,
      decoration: InputDecoration(
        prefixIcon: const Icon(Icons.search),
        hintText: '搜索',
        border: OutlineInputBorder(borderRadius: BorderRadius.circular(20)),
        suffixIcon: controller.text.isNotEmpty
            ? IconButton(
                onPressed: () {
                  controller.clear();
                  focusNode.requestFocus();
                  // 程序清空不会触发 TextField.onChanged，需要显式通知。
                  onChanged('');
                },
                icon: const Icon(Icons.clear),
                tooltip: '清空',
              )
            : null,
      ),
      textInputAction: TextInputAction.search,
      onChanged: onChanged,
    );
  }
}
